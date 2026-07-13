# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 17:06:33 2020

@author: jjanko
"""

import os
import pandas as pd
from scipy.interpolate import interp1d
import csv
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from multiprocessing import Pool

class OptData():
    
    def __init__(self):
        self.rootDir = r'D:\btdata_cloudrun'
        
    def make_hdf(self):
        
        for dirName, subdirList, fileList in os.walk(self.rootDir):
            pass
        #initialize a dataframe to populate with data
        df = pd.DataFrame()
        
        for x in fileList:
            if '.csv' in x:
                if len(df) == 0:
                    df = pd.read_csv(os.path.join(self.rootDir, x))
                else:
                    add = pd.read_csv(os.path.join(self.rootDir, x))
                    df = pd.concat([df, add], axis = 0)
        #filter for only puts
        df = self.filter_c_p('P', df)
        df.to_hdf('option_data.h5', key = 'df')
        
        return df
    
    def get_data(self):
        try:
            df = pd.read_hdf('option_data.h5')
        except FileNotFoundError:
            df = self.make_hdf()
            
        return df
    
    def filter_c_p(self, flag, df):
        df = df.loc[df['type'] == flag]
        return df
    
    def get_skew_df(self):
        try:
            skew = pd.read_csv(os.path.join(os.getcwd(), 'skew_data.csv'))
        except FileNotFoundError: 
            df = self.get_data()
            
            dates = df['quote_date'].unique()
            
            #interpolate the curve to get a constant skew metric for analysis
            
            interpolation_values = [.5, .45,.35, .25,.2,.15, .1]
            column_list = ['date','dte'] + interpolation_values
            skew = pd.DataFrame(columns = column_list)
            #day_delta.plot.scatter(x='delta',y='iv')
            
            for i in dates:
                day = df.loc[df['quote_date'] == i]
                exp = day['expiry'].unique()
                for j in exp:
                    #get the data by expiration and interpolate by delta
                    day_exp = day.loc[day['expiry'] == j]
                    #I want to look at out of the money only
                    day_delta = day_exp.loc[day_exp['delta'] <= .55]
                    day_delta = day_delta.loc[day_exp['delta'] >= .05]
                    if len(day_delta) >= len(interpolation_values):
                        try:
                            f = interp1d(day_exp['delta'], day_exp['iv'], kind = 'cubic')
                            interpolated_day = [i,day_delta['dte'].unique()[0]] + f(interpolation_values).tolist()
                            add = pd.DataFrame(interpolated_day).transpose()
                            add.columns = column_list
                            if len(skew) == 0:
                                skew = add.copy()
                            else:
                                skew = pd.concat([skew, add], axis = 0, ignore_index = True)
                        except ValueError:
                            pass
                        
            #for simplicity filter out outliers
            diff = (skew[.1] / skew[.5])
            #set bounds to filter out errors in data and interpolation process in interest of time. ideally you would check individually
            skew = skew.loc[diff <= 2.0]
            #there should really never be too much of a smirk
            skew = skew.loc[diff >= .9]
            z_score = (diff - diff.mean()) / diff.std()
            
            #convert the dates to datetime
            skew.loc[:,'date'] = pd.to_datetime(skew.loc[:,'date'])
            #get the 30 day skew via interpolation
            dates_interp = skew['date'].unique()
            column_list = ['date'] + interpolation_values
            skew_cleaned = pd.DataFrame(columns = column_list)
            
            for i in dates_interp:
                day = skew.loc[skew.date == i]
                try:
                    interpolated_skew = []
                    for j in interpolation_values:
                        f = interp1d(day['dte'].values.tolist(), day[j].values.tolist(), kind = 'linear')
                        #get the 30 day dte interpolated skew 
                        interpolated_skew.append(f(60).tolist())
                    add = pd.DataFrame([i] + interpolated_skew).transpose()
                    add.columns = column_list
                    if len(skew_cleaned) == 0:
                        skew_cleaned = add.copy()
                    else:
                        skew_cleaned = pd.concat([skew_cleaned, add], axis = 0, ignore_index = True)
                except ValueError:
                    pass
                
            #look for major outliers
            
            for i in interpolation_values:
                if i != .5:
                    #for simplicity filter out outliers
                    diff = (skew_cleaned[i] / skew_cleaned[.5])
                    #set bounds to filter out errors in data and interpolation process in interest of time. ideally you would check individually
                    z_score = (diff - diff.mean()) / diff.std()
                    
                    #remove outliers for simplicity
                    skew_cleaned = skew_cleaned.loc[z_score.abs() < 3.25]
                
                
            #get the ratios for analysis
            for i in interpolation_values:
                if i != .5:
                    skew_cleaned.loc[:,i] = skew_cleaned.loc[:,i] / skew_cleaned.loc[:,.5]
                    
            skew_cleaned = skew_cleaned.drop(labels = .5, axis = 1)
            
            skew_cleaned.to_csv('skew_data.csv')
            skew = skew_cleaned.copy()
        return skew
        
    
    
class indxData():
    #this class uses data that cannot release to you because I paid for it or its is part of WRDS license
    def __init__(self):
        pass
    def get_idx_output(self):
        indx = pd.read_excel(r'D:\indx\idx_cleaned.xlsx')

        output = pd.DataFrame()
        
        with open(r'D:\indx\daily_tickers.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            for row in indx.iterrows():
                data = row[1].dropna()
                tickers = data.index.tolist()
                add = pd.DataFrame(pd.Series(tickers[1:]), columns = [row[1][0]]).transpose()
                writer.writerow( [row[1][0]] + add.values.tolist()[0])
        
                
        tickers =  pd.read_excel(r'D:\indx\daily_tickers.xlsx', sheet_name = 'daily_tickers', index_col = 0)
        spx =  pd.read_excel(r'D:\indx\daily_tickers.xlsx', sheet_name = 'spx', index_col = 0)
        output = pd.concat([tickers, spx], axis = 0)
        output = output.sort_index()
        #the weightings are  given quarterly so you must forward fill 
        output = output.fillna(method = 'ffill')
        output = output.loc[spx.index]
        output.to_excel(r'D:\indx\daily_tickers_cleaned.xlsx')
        
    def getnamesCRSP(self):
        names = pd.read_excel(r'D:\indx\idx_cleaned.xlsx', sheet_name = r'original')
        names = names.columns.tolist()
        string = ''
        file1 = open("myfile.txt","w")
        out = []
        for i in names:
           
            ticker = i.split()[0].split('.')[0]
            if ticker not in out:
                out.append(ticker)
                string = string + ' ' + ticker
                writestring = ticker + ' \n'
                file1.write(writestring)
        file1.close()
        
    def gethistorical(self):
        try:
            indx_data = pd.read_csv('cleaned_index.csv', index_col = 0)
            return indx_data

        except FileNotFoundError: 
            historical = pd.read_csv('crsp_data2.csv', index_col = 0)
            
            #adjist for dividends and shares
            historical['PRC'] = historical['PRC'] / historical['CFACPR']
            historical['SHROUT'] = historical['SHROUT'] * historical['CFACSHR']
            
            
            historical['market cap'] = historical['PRC'] * historical['SHROUT']
            historical = historical.drop(labels = ['CFACPR','CFACSHR','SHROUT'], axis = 1)
            historical['ln return'] = 0.0
            historical['return'] = 0.0
            historical['Weight'] = 0.0
            historical['3M RV'] = 0.0
            historical.index = historical['date']
            historical = historical.drop(labels = 'date', axis = 1)
            
            
            #get the volatility
            ticker = historical['TICKER'].unique()
            for i in ticker:
                historical.loc[historical['TICKER'] == i, 'return'] = historical.loc[historical['TICKER'] == i,'PRC'].pct_change()
                historical.loc[historical['TICKER'] == i, 'ln return'] = np.log(historical.loc[historical['TICKER'] == i,'PRC']) - np.log(historical.loc[historical['TICKER'] == i,'PRC'].shift(1))
                historical.loc[historical['TICKER'] == i, '3M RV'] = historical.loc[historical['TICKER'] == i, 'ln return'].rolling(63).std() * np.sqrt(252) * 100.0
            
            #drop days where we do not have data
            historical = historical.dropna()
            
            df = pd.DataFrame()
            #filter out the top 500 by market cap on each day and get weights
            for i in historical.index.unique().tolist():
                #remove dates with too little data or errors
                if len(historical.loc[historical.index == i]) < 500:
                    historical = historical.loc[historical.index != i]
                else:
                    day = historical.loc[historical.index == i]
                    day = day.loc[day['market cap'].rank(ascending = False) <= 500]
                    #get the daily weight
                    day['Weight'] = (day['market cap'] / day['market cap'].sum())*100.0
                    if len(df) == 0:
                        df = day.copy()
                    else:
                        df = pd.concat([df, day], axis = 0)
            #convert to format to concatenate with other data
            indx_data = df[['3M RV', 'Weight']]
            indx_data['Ticker'] =  df['TICKER']
            indx_data['pct return'] = df['return'] 
            indx_data['Type'] = 'component'
            indx_data.to_csv('cleaned_index.csv')
            return indx_data

        
class SP500Data():
    
    def __init__(self):
        self.spx = pd.read_excel(r'D:\indx\spx.xlsx', sheet_name = 'data')
        #get the annualized volatility over the last 3 months from returns 
    def get_data(self):
        self.spx['log_ret'] = np.log(self.spx.Price) - np.log(self.spx.Price.shift(1))
        self.spx['3M RV'] = self.spx['log_ret'].rolling(63).std() * np.sqrt(252) * 100.0
        self.spx['pct return'] = self.spx.Price.pct_change() * 100.0
        self.spx = self.spx.dropna()
        self.spx.index = self.spx['Date']
        self.spx = self.spx.drop(labels = ['Date','Price', 'log_ret'], axis = 1)
        return self.spx
    
        
class HelperFunctions():
    
    def __init__(self):
        self.ix_data = 0.0
    
    def calcDenominator(self, Component_Data, columnName, i):
        denominator = 0.0
        for x in Component_Data.loc[Component_Data.index == i[0],'Ticker'].unique():
            denominator = denominator + (Component_Data[Component_Data.index == i[0]][Component_Data[Component_Data.index == i[0]]['Ticker'] != x]['Weight'] * Component_Data[Component_Data.index == i[0]][Component_Data[Component_Data.index == i[0]]['Ticker'] == x]['Weight'].values[0] * Component_Data[Component_Data.index == i[0]][Component_Data[Component_Data.index == i[0]]['Ticker'] != x][columnName] * Component_Data[Component_Data.index == i[0]][Component_Data[Component_Data.index == i[0]]['Ticker'] == x][columnName].values[0]).sum()
        return denominator
    


    def getImpliedCorr(self, Index_Data, Component_Data):
        for i in Index_Data.iterrows():
            if i[1]['Realized Corr'] == 0.0:
                denominator = self.calcDenominator(Component_Data, '3M RV',i)
                #calculate the implied correlation
                Index_Data.loc[Index_Data.index == i[0], 'Realized Corr']=100.0*(Index_Data.loc[Index_Data.index == i[0],'3M RV'].values[0]**2 - \
                              ((Component_Data.loc[Component_Data.index == i[0],'3M RV']**2)*(Component_Data.loc[Component_Data.index == i[0],'Weight']**2)).sum()) / denominator 
                print(i[0])
                
                if Index_Data is not None:
                    self.ix_data = Index_Data
        return Index_Data

        
    def drop_labels(self, header_label, df):
        df = df.drop(labels = header_label, axis = 1)
        return df

if __name__ == "__main__":
    
    #create objects for anaylsis
    helper = HelperFunctions()
    data = OptData()
    component_data = indxData()
    spx_obj = SP500Data()
    
    df = data.get_skew_df()
    
    
    spx = spx_obj.get_data()
    spx = spx.loc[~spx.index.duplicated(keep='first')]
    vol_data = spx.copy()
    
    #get the 2019 index component data
    tickers_2019 = pd.read_excel(r'D:\indx\daily_tickers_2019_printed.xlsx', sheet_name = 'tickers', index_col = 'date')[0:-1]
    tickers_2019 = helper.drop_labels(0, tickers_2019)
    tickers_2019 = tickers_2019.loc[~tickers_2019.index.duplicated(keep='first')]
    vol_2019 = pd.read_excel(r'D:\indx\daily_tickers_2019_printed.xlsx', sheet_name = 'vol', index_col = 'date')[0:-1]
    vol_2019 = helper.drop_labels(0, vol_2019)
    vol_2019 = vol_2019.loc[~vol_2019.index.duplicated(keep='first')]
    mkt_cap_2019 = pd.read_excel(r'D:\indx\daily_tickers_2019_printed.xlsx', sheet_name = 'market_cap', index_col = 'date')[0:-1]
    mkt_cap_2019 = helper.drop_labels(0, mkt_cap_2019)
    mkt_cap_2019 = mkt_cap_2019.loc[~mkt_cap_2019.index.duplicated(keep='first')]
    
    #coerce errors in the data
    weights = mkt_cap_2019.copy()
    for i in weights.columns:
        weights[i] = pd.to_numeric(weights[i], errors = 'coerce')
        vol_2019[i] = pd.to_numeric(vol_2019[i], errors = 'coerce')
    
    
    weights = weights.divide(weights.sum(axis = 1), axis = 'index') * 100.0
    
    
    #merge the spx data and index components for 2019
    for i in tickers_2019.index.unique().tolist():
        
        add = pd.concat([tickers_2019.loc[tickers_2019.index == i].T, weights.loc[weights.index == i].T, vol_2019.loc[vol_2019.index == i].T], axis = 1)
        add.columns = ['Ticker', 'Weight', '3M RV']
        add['pct return'] = ''
        add['Type'] = 'component'
        add['Date'] = i
        add.index = add['Date']
        add = helper.drop_labels('Date', add)
        add = add.dropna(axis = 0)
        vol_data = pd.concat([vol_data, add], axis = 0, sort = 'True')
    
    #get the component data from years other than 2019
    vol_1992_2018 = component_data.gethistorical()
    vol_1992_2018.index = pd.to_datetime(vol_1992_2018.index)
    
    vol_data = pd.concat([vol_data, vol_1992_2018], axis = 0, sort = True)
    #get rid of days that do not have both index and component data due to data issues/errors
    
    days = []
    for i in vol_data.index.unique():
        day = vol_data.loc[vol_data.index == i]
        if (len(day.loc[day.Type == 'Index']) ==1) and (len(day.loc[day.Type != 'Index']) >=450) and (day.loc[day.Type != 'Index', 'Weight'].sum() >= 99.0):
            days.append(i)
        
    
    vol_data = vol_data.loc[vol_data.index.isin(days)]
    vol_data = vol_data.loc[days,:]

    
    Index_Data = vol_data.loc[vol_data['Type'] == 'Index']
    Component_Data = vol_data.loc[vol_data['Type'] != 'Index']

    
    #I have to change the format of data since the calculation came from another program
    
    Index_Data = vol_data.loc[vol_data['Type'] == 'Index']
    Component_Data = vol_data.loc[vol_data['Type'] != 'Index']
    #get rid of the percentage basis
    Component_Data.loc[:,'Weight'] = Component_Data.loc[:,'Weight'] / 100.0
    Index_Data.loc[:,'Realized Corr'] = 0.0
    #do the process in parallel for faster speed
    helper.getImpliedCorr(Index_Data,Component_Data)
    
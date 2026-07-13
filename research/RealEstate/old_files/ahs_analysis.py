# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 17:42:55 2019
@author: yruan
"""
import pandas as pd
import os
import numpy as np
from statsmodels import regression
#import matplotlib.pyplot as plt
import warnings
import net_yields_calculation as net_yield_calc
import non_parametric_median as npm

warnings.filterwarnings("ignore")


class Cleaning():
    
    def __init__(self):
        pass

    def check_col_float2(self,header_list, df):
        for col in header_list:
            try:
                df.loc[:,col] = df.loc[:,col].str.replace("\'","").str.strip().astype(float)
                
            except AttributeError:
                pass
            except KeyError:
                try:
                    df[col.upper()] = df[col.lower()].str.replace("\'","").str.strip().astype(float)
                except AttributeError:
                    df[col.upper()] = df[col.lower()].copy()
        return df
    
    
    
    def change_airsys_data(self,data):
        
        data.loc[(data['AIRSYS'] == 2) & (data['year'] < 2015), 'AIRSYS'] = 0.0
        data.loc[(data['AIRSYS'] == 12) & (data['year'] >= 2015), 'AIRSYS'] = 0.0
        data.loc[(data['AIRSYS'] != 12) & (data['year'] >= 2015), 'AIRSYS'] = 1.0
        
        return data
    
    def change_bath_data(self,data):
        for i in data.year.unique():
            if i >=2015 and i<=2017:
                data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({7: 0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 3:2,4:3,5:3,6:4 })
            else:
                data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({5:4, 6:4, 7: 4, 8:4, 9:4, 10:4, 11:4, 12:4, 13:4})
        return data
    
    def change_unit_type_data(self,data):
        data['Unit Type'] = 'None' 
        data.loc[data['CONDO'] == 1, 'Unit Type'] = 'Condo'
    
        data.loc[(data['year'] < 2015) & (data['NUNIT2'] == 1 ),'Unit Type'] = 'Detached'
        data.loc[(data['year'] < 2015) & (data['NUNIT2'] == 2 ),'Unit Type'] = 'Attached'
        
        
        data.loc[(data['year'] >= 2015) & (data['TYPE'] == 2 ),'Unit Type'] = 'Detached'
        data.loc[(data['year'] >= 2015) & (data['TYPE'] == 3 ),'Unit Type'] = 'Attached'
        
        
        return data
    
    def get_city_names(self,data, smsa_dict):
        data['CITY'] = ''
        for i in smsa_dict.keys():
            data.loc[data['SMSA'] == float(i), 'CITY'] = smsa_dict[str(i)]
        return data
        
        
    
    def change_build_data(self,data):
        
        for i in data.year.unique():
            data.loc[data.year==i,'BUILT'] = data.loc[data.year==i,'BUILT'].replace({80: 1980,
                    81:1981,82:1982,83:1983,84:1984,85:1985,86:1986,87:1987,88:1988,89:1989,
                    90:1990,91:1991,92:1992,93:1993,94:1994,95:1995,96:1996,97:1997,98:1998,
                    99:1999})
                 
        for i in data.year.unique():
            if i >=1985 and i<=1995:
                data.loc[data.year==i,'BUILT'] = data.loc[data.year==i,'BUILT'].replace({9: 1919,
                        8:1920,7:1930,6:1940,5:1950,4:1960,3:1970,2:1970,1:1970})
        
        for i in data.year.unique():
            data.loc[data.year==i,'BUILT']=data.loc[data.year==i,'BUILT'].replace({1919:1910,
                 1981:1980,1982:1980, 1983:1980,1984:1980,1986:1985,1987:1985,1988:1985,1989:1985,
                 1991:1990,1992:1990, 1993:1990,1994:1990,1996:1995,1997:1995,1998:1995,1999:1995,
                 2001:2000,2002:2000, 2003:2000,2004:2000,2006:2005,2007:2005,2008:2005,2009:2005,
                 2011:2010,2012:2010, 2013:2010,2014:2010})
        #for i in data.year.unique():
        #    data.loc[data.year==i,'BUILT']=(np.floor(data.loc[data.year==i,'BUILT']/10.0)*10.0).astype(int)
        
                    
            
        for i in data.year.unique():
            if i >=2015 and i<=2017:
                data.loc[data.year==i,'AIRSYS'] = data.loc[data.year==i,'AIRSYS'].replace({2: 1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1, 11:1,12:2})
                 
        for i in data.year.unique():
            if i >=2015 and i<=2017:
                data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({7: 0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 3:2,4:3,5:3,6:4 })
            else:
                data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({5:4, 6:4, 7: 4, 8:4, 9:4, 10:4, 11:4, 12:4, 13:4})
            
        return data
    
    def get_distribution2(self,data, filter_code, name):
        dct = {}
        for i in data.year.unique():
            dct[i] = data.loc[data.year == i, filter_code].value_counts()
        dct = pd.DataFrame(dct)
        dct.to_csv(os.path.join(r'T:\PhD Students\yearly_breakdown', name + '.csv'))
        data.loc[:,name].value_counts().to_csv(os.path.join(r'T:\PhD Students\yearly_breakdown', 'total_' + name + '.csv'), header = True)
    
    def get_distribution(self,data, name):
        dct = {}
        for i in data.year.unique():
            dct[i] = data.loc[data.year == i, name].value_counts()
        dct = pd.DataFrame(dct)
        dct.to_csv(os.path.join(r'T:\PhD Students\yearly_breakdown', name + '.csv'))
        data.loc[:,name].value_counts().to_csv(os.path.join(r'T:\PhD Students\yearly_breakdown', 'total_' + name + '.csv'), header = True)
    
    def change_rent_data(self, hedonic_model_data):
        hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['year']<=1995) & (hedonic_model_data['RENT'] == 1))]
        hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['year']<=1995) & (hedonic_model_data['RENT'] == 999))]
        hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['year']<=1995) & (hedonic_model_data['RENT'] == 9999))]
        hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['year']> 1995) & (hedonic_model_data['RENT'] == 9999))]
        hedonic_model_data.loc[:, 'RENT'] = hedonic_model_data.loc[:, 'RENT']*12.0
        return hedonic_model_data
        
class Calculations():
    
    def get_mean_var(self, data, varname):
        mean_yearly=pd.DataFrame(np.nan,index=data['year'].unique(), columns=range(1))
        for i in data['year'].unique():
            sample_year=data.loc[data['year']==i,:]
            mean_year=np.mean(sample_year[varname])
            mean_yearly.loc[i,:]=mean_year
        
        print(mean_yearly)        
        mean_yearly.plot(kind='bar')
        return mean_yearly
    
    def get_net_yields(self, owned_data, rental_data):
        
        
        return owned_data, rental_data
    
    
if __name__ == "__main__":
    
    c = Cleaning()
    calc = Calculations()
    
    same_smsa = {'35620':5600,'31080':4480,'16980':1600,'19100':1920,'37980':6160,'26420':3360,'47900':8840,'33100':5000,'12060':520,'14460':1120,'41860':7360,'19820':2160,'40140':6780,'38060':6200,'42660':7600,'19740':2080,'38300':6280,'38900':6440,'17140':1640,'17460':1680,'28140':3760,'33340':5080,'32820':4920,'35380':5560,'39580':6640,'33460':5120,'45300':8280,'12580':720,'41700':7240,'29820':4120,'41940':7400,'36420':5880,'40060':6760,'13820':1000,'40380':6840}
    same_smsa_back = {'5600': 35620, '4480': 31080, '1600': 16980, '1920': 19100, '6160': 37980, '3360': 26420, '8840': 47900, '5000': 33100, '520': 12060, '1120': 14460, '7360': 41860, '2160': 19820, '6780': 40140, '6200': 38060, '7600': 42660, '2080': 19740, '6280': 38300, '6440': 38900, '1640': 17140, '1680': 17460, '3760': 28140, '5080': 33340, '4920': 32820, '5560': 35380, '6640': 39580, '5120': 33460, '8280': 45300, '720': 12580, '7240': 41700, '4120': 29820, '7400': 41940, '5880': 36420, '6760': 40060, '1000': 13820, '6840': 40380}
    
    eisfeldt_top_30 = {"6280": "Pittsburgh","7040": "St. Louis","3760": "Kansas City","3360": "Houston","1920": "Dallas","5880": "Oklahoma City","1680": "Cleveland ","6160": "Philadelphia","520": "Atlanta","5120": "Minneapolis","7600": "Seatle","720": "Baltimore","5380": "Nassau-Suffolk","5680": "Virginia Beach","1600": "Chicago","8280": "Tampa","8840": "Washington","5000": "Miami","7360": "San Fransico","1120": "Boston","7320": "San Diego","7400": "San Jose","360": "Anaheim","2160": "Detroit","5640": "Newark","5600": "New York","5775": "Oakland","4480": "Los Angeles","6200": "Phoenix","6780": "Riverside"}


    vals = []
    for iterate in eisfeldt_top_30.keys():
        vals.append(float(iterate))
    
    
    _vals = []
    for v in vals:
        if str(int(v)) in same_smsa_back.keys():
            _vals.append(same_smsa_back[str(int(v))])
            


    filepath = r'T:\PhD Students\ftp_data_census2'
    
    hedonic_model_data = pd.DataFrame()
    sample = {}
    for item in os.listdir(filepath):
        if item[0] == 'o':
            year = int(item.split(".")[0][1:])
            data = pd.read_hdf(os.path.join(filepath, item))
            
            if year >= 2015:
                data = data.loc[data['SMSA'].isin(_vals)]
            else:
                data = data.loc[data['SMSA'].isin(vals)]
            
            
            if len(hedonic_model_data.index) == 0:
                hedonic_model_data = data.copy()
            else:
                hedonic_model_data = pd.concat([hedonic_model_data, data.copy()], axis = 0)
                
    for i in same_smsa.keys():
        hedonic_model_data.loc[hedonic_model_data.SMSA == float(i),'SMSA'] = same_smsa[i]
        
    hedonic_model_data = c.change_rent_data(hedonic_model_data)
    hedonic_model_data =  c.get_city_names(hedonic_model_data, eisfeldt_top_30)
    c.get_distribution2(hedonic_model_data, 'CITY')
    
                
    #clean the data
    hedonic_model_data['log rent'] = np.log(hedonic_model_data['RENT'])
    hedonic_model_data = c.change_build_data(hedonic_model_data)
    hedonic_model_data = c.change_unit_type_data(hedonic_model_data)
    hedonic_model_data = c.change_airsys_data(hedonic_model_data)
    hedonic_model_data = c.change_bath_data(hedonic_model_data)
    
    
    
    #filter the data section
    
    
    hedonic_model_data = hedonic_model_data.loc[hedonic_model_data['ROOMS'] >= 0]
    hedonic_model_data = hedonic_model_data.loc[hedonic_model_data['BEDRMS'] >= 0]
    
    c.get_distribution(hedonic_model_data, 'ROOMS')
    c.get_distribution(hedonic_model_data, 'BEDRMS')
    
    hedonic_model_data = c.check_col_float2(['TENURE'], hedonic_model_data)
    
    #get rid of homes that are occupied without payment for rent
    hedonic_model_data = hedonic_model_data[hedonic_model_data['TENURE'] != 3.0]
    c.get_distribution(hedonic_model_data, 'TENURE')
    

    

    #remove rent control
    """
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['RCNTRL'].isin([8,1,9,-9])) & (hedonic_model_data['year'] < 1997 ) )]
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['RCNTRL'].isin([1,-7,-8,-9,-6])) & (hedonic_model_data['year'] >= 1997 ) )]
    """
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['RCNTRL'].isin([8,1,2])) & (hedonic_model_data['year'] < 1997 ) )]
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['RCNTRL'].isin([1,-7,-8,-9])) & (hedonic_model_data['year'] >= 1997 ) )]
   
    c.get_distribution(hedonic_model_data, 'RCNTRL')
    
    
    #remove windows
    """
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['EBAR'].isin([9,1,8.-9])) & (hedonic_model_data['year'] < 1997 ) )]
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['EBAR'].isin([1,-7,-8,-9,-6])) & (hedonic_model_data['year'] >= 1997 ) )]
    """
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['EBAR'].isin([9,1,8])) & (hedonic_model_data['year'] < 1997 ) )]
    hedonic_model_data = hedonic_model_data.loc[~((hedonic_model_data['EBAR'].isin([1,-7,-8,-9])) & (hedonic_model_data['year'] >= 1997 ) )]
    
    c.get_distribution(hedonic_model_data, 'EBAR')
    
        
    hedonic_model_data = hedonic_model_data.loc[hedonic_model_data['VALUE'] < 999999]
    
    hedonic_model_data = hedonic_model_data[(hedonic_model_data['ZINC2'] / hedonic_model_data['VALUE']) < 2. ]  
    c.get_distribution(hedonic_model_data, 'ZINC2')
    c.get_distribution(hedonic_model_data, 'VALUE')
    
    
    hedonic_model_data = hedonic_model_data.loc[(hedonic_model_data['ZINC2'] /(hedonic_model_data['RENT'])) < 100. ] 
    hedonic_model_data = hedonic_model_data.loc[hedonic_model_data['Unit Type'].isin(['Detached', 'Attached'])]
    rhedonic_model_data = hedonic_model_data.sort_values(['SMSA', 'year'], axis = 0)
    hedonic_model_data.loc[hedonic_model_data['Unit Type'] == 'Detached','Unit Type'] = 1.0
    hedonic_model_data.loc[hedonic_model_data['Unit Type'] == 'Attached','Unit Type'] = 0.0
    c.get_distribution(hedonic_model_data, 'Unit Type')
    
    owned_data = hedonic_model_data[hedonic_model_data['log rent'].isnull()]
    owned_data = hedonic_model_data[hedonic_model_data['VALUE'] > 0]
    rental_data = hedonic_model_data[hedonic_model_data['log rent'] > 0.0]
    
    r_data = hedonic_model_data[['BUILT','ROOMS','BATHS','AIRSYS','BEDRMS','Unit Type','SMSA','year', 'log rent', 'VALUE']]

    hedonic_data = r_data.loc[r_data['log rent'] > 0.0]
    
    dumvarcols = ['year', 'SMSA']
    
    
    hedonic_data  = pd.get_dummies(hedonic_data, columns = dumvarcols )
    
    
    """convert the airsys variable to a dummy variable which is binary"""
    
    hedonic_data.loc[:,'intercept'] = 1.0
    
    x_var = hedonic_data.columns.tolist()
    x_var.remove('year_1985')
    x_var.remove('SMSA_360.0')
    x_var.remove('log rent')
    x_var.remove('VALUE')
    
    
    thedonic_data  = hedonic_data.copy()
    
    model = regression.linear_model.OLS(hedonic_data['log rent'], hedonic_data[x_var])
    results = model.fit()
    print(results.summary())
    
    #estimate the log rent on the owned data
    df_o = owned_data.copy()
    df_o = pd.get_dummies(df_o, columns = dumvarcols  )
    df_o.loc[:,'intercept'] = 1.0
    #change the coefficients for predictions to match eisfeldt
    
    predictions = results.predict(df_o[x_var])
    

    """
    #fix a constant
    fixed = thedonic_data.loc[:,'intercept']*8.87 + thedonic_data.loc[:,'ROOMS']*.05 + thedonic_data.loc[:,'BEDRMS']*.02 + thedonic_data.loc[:,'BATHS']*.18 + thedonic_data.loc[:,'AIRSYS']*.15 + thedonic_data.loc[:,'Unit Type']*.05
    
    y = thedonic_data['log rent']  - fixed
    
    x_var = x_var = thedonic_data.columns.tolist()
    x_var.remove('intercept')
    x_var.remove('ROOMS')
    x_var.remove('BEDRMS')
    x_var.remove('BATHS')
    x_var.remove('AIRSYS')
    x_var.remove('Unit Type')
    x_var.remove('year_1985')
    x_var.remove('SMSA_360.0')
    x_var.remove('log rent')
    x_var.remove('VALUE')

    model = regression.linear_model.OLS(y , thedonic_data[x_var])
    results = model.fit()
    print(results.summary())   
    
    
    
    df_o = owned_data.copy()
    df_o = pd.get_dummies(df_o, columns = dumvarcols  )
    df_o.loc[:,'intercept'] = 1.0
    #change the coefficients for predictions to match eisfeldt
    
    predictions = results.predict(df_o[x_var]) +    df_o.loc[:,'intercept']*8.87 + df_o.loc[:,'ROOMS']*.05 + df_o.loc[:,'BEDRMS']*.02 + df_o.loc[:,'BATHS']*.18 + df_o.loc[:,'AIRSYS']*.15 + df_o.loc[:,'Unit Type']*.05
    """
    
    
    owned_data.loc[:,'log rent'] = predictions
    owned_data.loc[:,'RENT'] = np.exp(predictions)
    owned_data.loc[:,'rent_to_price'] = owned_data['RENT'] /  owned_data['VALUE']    
    owned_data.loc[:,'price_to_rent'] = owned_data['VALUE'] /  owned_data['RENT'] 
    c.get_distribution(owned_data, 'price_to_rent')
    
    owned_data = owned_data.sort_values(['CITY', 'year'], axis = 0)
    owned_data.loc[:,'weight'] = 0.0
    owned_data.loc[:,'status']= 1.0
    rental_data.loc[:,'status']=2.0
    

    
    for i in owned_data['year'].unique():
        dataplot = owned_data.loc[:,:][owned_data.loc[:,'price_to_rent'] < 50]
        dataplot = dataplot.loc[:,'price_to_rent'][dataplot.loc[:,'year'] == i]
        dataplot.plot.kde()
    
    #mean_price_to_rent = calc.get_mean_var(owned_data, 'price_to_rent')
    
        
    #######################################################################
    #get the net yields from module
    
    owned_data, rental_data = net_yield_calc.get_net_yields(owned_data, rental_data)
    c.get_distribution(owned_data, 'CITY')
    c.get_distribution(rental_data, 'CITY')
    #######################################################################
    #get the non parametric weighting for the medians of the data
    
    #owned_data, rental_data = npm.get_median_weighting(owned_data, rental_data)
    
    city_percentage = {}
    obs = {}
    
    for i in owned_data['year'].unique():
        year = owned_data.loc[owned_data['year'] == i]
        city_percentage[i] = year['CITY'].value_counts(normalize=True)
        obs[i] = len(year)
    
    city_percentage = pd.DataFrame.from_dict(city_percentage)
    
    


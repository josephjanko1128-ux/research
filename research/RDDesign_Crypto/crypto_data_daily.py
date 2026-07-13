# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 10:04:07 2020

@author: jjandso
"""

import requests
import pandas as pd
import numpy as np
from statsmodels import regression
import matplotlib.pyplot as plt
import datetime
from scipy.optimize import minimize


def get_data(symbol):
        
    url = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym='+ symbol + '&tsym=USD&limit=2000'
    #url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=' + symbol + '&tsym=USD&limit=2000'
    f = requests.get(url)
    ipdata = f.json()
    df = pd.DataFrame(ipdata['Data']['Data'])
    df.time = pd.to_datetime(df['time'], unit = 's')
    df.set_index('time', inplace=True) 
    df.sort_index(ascending=False, inplace=True)   
    
    return df

def clean_data(df):
    
    df['returns'] = np.log(df['close']) - np.log(df['close'].shift(1))
    df['vol'] = df['volumeto'] - df['volumefrom']
    
    df['liquidity'] = df['returns'] / df['vol']
    
    return df[1:]
    
def get_between_dates(df, before, after):
    df =df.loc[df.index <= after ]
    df =df.loc[df.index >= before ]
    return df

def k_folds(indices, K):

    for k_fold in range(K):
        
        training = []
        validation = []
        
        for i,x in enumerate(indices):
            if i % K != k_fold:
                training.append(x)
            if i % K == k_fold:
                validation.append(x)
        
    return training, validation

def sum_constraint(inputs):
    total = 1.0 - np.sum(inputs)
    return total

def minimization_mse(weights,y,x):
    weights = weights / np.sum(weights)
    return np.mean(((y.values-(x * weights).sum(axis=1))**2).values)



if __name__ == "__main__":

    key = 'cb4ff6780b711762d2e9ac8f1c853ced9d57ffab566204c64c344098c39771a7'
    
    symbols = ['NEO','BTC', 'ETH','XRP','LTC','XMR']
    
    data_dict = {}
    
    for x in symbols:
        data_dict[x] = get_data(x)
        data_dict[x] = clean_data(data_dict[x])
        
    
    
    df = pd.DataFrame()
    plot_df = pd.DataFrame()
    #define the inputs
    date_of_interest = pd.Timestamp(2019, 10, 25)
    window = 20
    
    control_symbols = symbols[1:]
    interest = symbols[0]
    
    
    for x in symbols:
        
        returns = pd.DataFrame(get_between_dates(data_dict[x]['close'],date_of_interest -  \
                    datetime.timedelta(days = window),date_of_interest + \
                    datetime.timedelta(days = window)).sort_index().pct_change().resample('1D').sum().cumsum())
        volume = pd.DataFrame(get_between_dates(data_dict[x]['vol'],date_of_interest -  \
                        datetime.timedelta(days = window),date_of_interest + \
                            datetime.timedelta(days = window)).sort_index())
        r = returns.copy()
        r.columns = [x]
        returns.columns = ['returns']
        returns['symbol'] = x
        returns['volume'] = volume
        
        if len(df) == 0:
            df = returns.copy()
            plot_df = r.copy()
        else:
            df=pd.concat([df, returns], axis = 0)
            plot_df = pd.concat([plot_df, r], axis = 1)
    """
    plt.plot(plot_df)
    plt.axvline(x=date_of_interest)
    plt.xlabel('Time')
    plt.ylabel('Cumlative Returns')
    plt.xticks(fontsize=8)
    plt.title('Time Series Plot of Crypocurrencies')
    plt.show()
    """
            
    df_copy = df.copy()
       
    z = (((plot_df - plot_df.shift(1))[1:] - (plot_df - plot_df.shift(1))[1:].mean()) \
         / (plot_df - plot_df.shift(1))[1:].std())
    """
    z.plot()
    """    
    
    z_day = z.loc[z.index == date_of_interest]
    
    controls = {}
    for x in symbols:
        controls[x] = df_copy.loc[df_copy['symbol'] == x, 'returns']
    controls = pd.DataFrame.from_dict(controls)
    pre =  controls.loc[controls.index < date_of_interest - datetime.timedelta(days = 1)]
    training, validation = k_folds(pre.index, 2)
    training_set = pre.loc[pre.index.isin(training)]
    validation_set = pre.loc[pre.index.isin(validation)]
    
    
    x = pre[control_symbols]
    y = pre[interest]
    
    #initially guess equal weights
    weights_0 = []
    bound_list = []
    for i in range(len(x.columns)):
        weights_0.append(1.0/len(x.columns))
        bound_list.append((0.0,1.0))
                    
    
    my_constraints = ({'type': 'eq', "fun": sum_constraint })
    
    result = minimize(minimization_mse, weights_0, method='SLSQP',args = (y,x),bounds=\
                      bound_list,options={'disp': True},constraints=my_constraints)
    
    i = 0
    weights_output = {}
    for x in control_symbols:
        weights_output[x] = result.x[i]
        i = i +1
    
    out_of_sample = (validation_set[control_symbols] * result.x).sum(axis=1)
    out_of_sample.columns = ['NEO']
    out_of_sample_mse = minimization_mse(result.x,validation_set[interest],\
                                         validation_set[control_symbols])
    validation_resid = validation_set[[interest]] - out_of_sample
    print(result.fun / out_of_sample_mse)
    
    iterate = 0
    controls['control'] = 0.0
    for x in control_symbols:
        controls['control'] = controls[x] * result.x[iterate] + controls['control']
        iterate = iterate + 1
    controls[['control', interest]].plot()
    
    df = pd.DataFrame()
    #create a synthetic control column
    for x in ['control', interest]:
        returns = pd.DataFrame(controls[x])
        returns.columns = ['returns']
        returns['symbol'] = x
        
        if len(df) == 0:
            df = returns.copy()
        else:
            df=pd.concat([df, returns], axis = 0)
        
    df['constant'] = 1.0
    df['t/c'] = 0
    df.loc[df['symbol'] == interest,'t/c'] = 1.0
    df['post'] = 0.0
    df.loc[df.index >= date_of_interest, 'post'] = 1.
    df['date'] = df.index
    df = df.reset_index()
    df = df.drop(labels = 'time', axis  = 1)
    date_dummies = pd.get_dummies(df['date'])
    df['interaction'] = df['t/c'] * df['post']
    
    model = regression.linear_model.OLS(df['returns'], \
                pd.concat([df[['constant','t/c', 'post', 'interaction']]], axis =1 ))
    results = model.fit()
    print(results.summary())
    
    
    NEO = df.loc[df['symbol']=='NEO'][['returns','date']]
    NEO_before = df.loc[(df['symbol']=='NEO') & (df['date']<date_of_interest)][['returns','date']]
    control_before = df.loc[(df['symbol']=='control') & (df['date']<date_of_interest)][['returns','date']]
    control_after = df.loc[(df['symbol']=='control') & (df['date']>=date_of_interest)][['returns','date']]
    


    #plt.axvline(date_of_interest, 0, .5, label='pyplot vertical line')
    """
    #plots the returns before
    plt.plot(NEO_before['date'], NEO_before['returns'])
    plt.plot(control_before['date'], control_before['returns'])
    plt.xticks(fontsize=8)
    plt.xlabel('Time')
    plt.ylabel('Cumlative Returns')
    plt.title('NEO and Control Plot Pre')
    """
    
    """
    #plots the returns fully
    plt.plot(controls['NEO'], 'r',label = 'NEO')
    plt.plot(controls['control'], 'g',label = 'control')
    plt.xticks(fontsize=8)
    plt.xlabel('Time')
    plt.axvline(x=date_of_interest)
    plt.ylabel('Cumlative Returns')
    plt.legend()
    plt.title('NEO and Control Plot')
    plt.show()
    """
    plt.plot(NEO['date'], NEO['returns'],'go',label='NEO')
    plt.plot(control_before['date'], control_before['returns'],'r+',label='control before')
    plt.plot(control_after['date'], control_after['returns'],'b+',label='control after')
    plt.legend(loc="upper left")
    plt.axvline(x=date_of_interest)
    plt.xlabel('Time')
    plt.ylabel('Cumlative Returns')
    plt.title('NEO and Control Plot')
    plt.show()

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import os
from math import e


def get_fred(string_file):
    fred = pd.read_csv(os.path.join(os.getcwd(), 'data',string_file))
    fred.index = fred.DATE
    fred.drop('DATE', axis = 1, inplace = True)
    fred.index = fred.index.str[0:7].str.replace('-','')
    fred = fred[fred.index.str[-2:] == '10']
    fred.index =  fred.index.str.replace('10', '')
    fred.index = fred.index.astype(int)
    return fred

print("J.P. Janko")
print("get data and clean")

#get the famma french 25 portfolios
ff_25 = pd.read_csv(os.path.join(os.getcwd(), 'data','25_Portfolios_5x5_cleaned.csv'))
ff_25.index = ff_25.Date
ff_25.drop('Date', axis = 1, inplace = True)
ff_25 = ff_25 / 100.0
ff_25 = ff_25.loc[(ff_25.index >= 1955) & (ff_25.index <= 2012)]


mkt_ret = pd.read_csv(os.path.join(os.getcwd(), 'data','mkt_ret.csv'))
mkt_ret.index = mkt_ret.date
mkt_ret.drop('date', axis = 1, inplace = True)
mkt_ret = mkt_ret / 100.0
mkt_ret = mkt_ret.loc[(mkt_ret.index >= 1955) & (mkt_ret.index <= 2012)]

fred = get_fred('fred_consumption.csv')
nondurables = get_fred('fred_nondurable.csv')
service = get_fred('fred_services.csv')
fred = fred / fred.shift(1)
fred.columns = ['C']
fred['lagged C'] = fred['C'].shift(1)
fred = fred.loc[(fred.index >= 1955) & (fred.index <= 2012)]



nipa = pd.read_csv(os.path.join(os.getcwd(), 'data','nipa_consumption.csv'))
nipa.index = nipa.date
nipa.drop('date', axis = 1, inplace = True)
nipa['lagged C'] = nipa.shift(1)
nipa = e**nipa
nipa = nipa.loc[(nipa.index >= 1955) & (nipa.index <= 2012)]

mkt_ret = pd.read_csv(os.path.join(os.getcwd(), 'data','mkt_ret_kro.csv'))
mkt_ret.index = mkt_ret.year
mkt_ret.drop('year', axis = 1, inplace = True)
mkt_ret = mkt_ret.loc[(mkt_ret.index >= 1955) & (mkt_ret.index <= 2012)]



cay = pd.read_csv(os.path.join(os.getcwd(), 'data','cay.csv'), delimiter=',')
cay.index = cay.date
cay.drop('date', axis = 1, inplace = True)
cay.index = cay.index.astype(str)
cay.index = cay.index.str.replace('-','')
cay.index = cay.index.str[0:-2]
cay = cay[cay.index.str[-2:] == '12']
cay.index =  cay.index.str.replace('12', '')
cay = cay.shift(1)
cay.index = cay.index.astype(int)
cay = cay.loc[(cay.index >= 1955) & (cay.index <= 2012)]
cay = e**cay

#get the market price dividend ratio
crsp = pd.read_csv(os.path.join(os.getcwd(), 'data','crsp.csv'), delimiter=',')
crsp['SHRCD'] = crsp.loc[:, 'SHRCD'].astype(str)
crsp = crsp[crsp['SHRCD'].str[0] == '1']
crsp = crsp[crsp['EXCHCD'].isin([1.,2.,3.])]
crsp['date'] = crsp.loc[:,'date'].astype(str)
crsp.index = crsp.date
crsp.drop('date', axis = 1, inplace = True)
crsp.index = crsp.index.str[0:-2]
crsp = crsp[crsp.index.str[-2:] == '12']
crsp.index =  crsp.index.str.replace('12', '')
crsp.index = crsp.index.astype(int)
crsp = crsp.loc[(crsp.index >= 1955) & (crsp.index <= 2012)]

p_d = pd.read_csv(os.path.join(os.getcwd(), 'data','p_d.csv'), index_col = 0)

#combine the columns together
df = pd.concat([nipa, mkt_ret, ff_25, cay, p_d], axis = 1)
df = df.interpolate()
print(df.head(5))
df.to_csv('data.csv')
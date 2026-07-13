# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 15:15:13 2019

@author: jjanko
"""

import os
import pandas as pd
import numpy as np
from statsmodels import regression



if __name__ == "__main__":
    
    data = pd.read_hdf(os.path.join(r'T:\PhD Students','hedonic_data.h5'))

    #create data for unit type fixed effect
    data['Unit Type'] = 'None' 
    data.loc[data['CONDO'] == 1, 'Unit Type'] = 'Condo'
    data.loc[(data['CONDO'] != 1) & (data['year'] < 2015) & (data['NUNIT2'] == 1 ),'Unit Type'] = 'Detached'
    data.loc[(data['CONDO'] != 1) & (data['year'] < 2015) & (data['NUNIT2'] == 3 ),'Unit Type'] = 'Apartment'
    data.loc[(data['CONDO'] != 1) & (data['year'] < 2015) & (data['NUNIT2'] == 2 ),'Unit Type'] = 'Attached'
    
    data.loc[(data['CONDO'] != 1) & (data['year'] >= 2015) & (data['TYPE'] == 2 ),'Unit Type'] = 'Detached'
    data.loc[(data['CONDO'] != 1) & (data['year'] >= 2015) & (data['TYPE']>= 4 ),'Unit Type'] = 'Apartment'
    data.loc[(data['CONDO'] != 1) & (data['year'] >= 2015) & (data['TYPE'] == 3 ),'Unit Type'] = 'Attached'
    data = data.loc[data['Unit Type'].isin(['Detached', 'Apartment', 'Attached', 'Condo'])]
    
    
    data.loc[(data['AIRSYS'] == 2) & (data['year'] < 2015), 'AIRSYS'] = 0.0
    data.loc[(data['AIRSYS'] == 12) & (data['year'] >= 2015), 'AIRSYS'] = 0.0
    data.loc[(data['AIRSYS'] != 12) & (data['year'] >= 2015), 'AIRSYS'] = 1.0
    
    #for purposes of matching 
    data = data[data.year < 2015]
    
    for i in data.year.unique():
        data.loc[data.year==i,'BUILT'] = data.loc[data.year==i,'BUILT'].replace({80: 1980,81:1981,82:1982,83:1983,84:1984,85:1985,86:1986,87:1987,88:1988,89:1989,90:1990,91:1991,92:1992,93:1993,94:1994,95:1995,96:1996,97:1997,98:1998,99:1999})
             
    for i in data.year.unique():
        if i >=1985 and i<=1995:
            data.loc[data.year==i,'BUILT'] = data.loc[data.year==i,'BUILT'].replace({9: 1919,8:1920,7:1930,6:1940,5:1950,4:1960,3:1970,2:1970,1:1970})
    
    for i in data.year.unique():
        data.loc[data.year==i,'BUILT']=(np.floor(data.loc[data.year==i,'BUILT']/10.0)*10.0).astype(int)
                        
                        
                
    for i in data.year.unique():
        if i >=2015 and i<=2017:
            data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({7: 0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 3:2,4:3,5:3,6:4 })
        else:
            data.loc[data.year==i,'BATHS'] = data.loc[data.year==i,'BATHS'].replace({5:4, 6:4, 7: 4, 8:4, 9:4, 10:4, 11:4, 12:4, 13:4})
    
    data.to_hdf(os.path.join(r'T:\PhD Students\hedonic_data','hedonic_data.h5'), key = 'df')

    data = data.sort_values(['MSA', 'year'], axis = 0)
    
    hedonic_data  = pd.get_dummies(data, columns = ['year', 'MSA','Unit Type', 'BUILT'])
    
    """convert the airsys variable to a dummy variable which is binary"""
    
    hedonic_data['intercept'] = 1.0
    
    x_var = hedonic_data.columns.tolist()
    x_var.remove('log rent')
    x_var.remove('TENURE')
    x_var.remove('CONDO')
    x_var.remove('NUNIT2')
    x_var.remove('TYPE')
    
    hedonic_data = hedonic_data[hedonic_data['log rent'] != 0.0]
    
    model = regression.linear_model.OLS(hedonic_data['log rent'], hedonic_data[x_var])
    results = model.fit()
    print(results.summary())



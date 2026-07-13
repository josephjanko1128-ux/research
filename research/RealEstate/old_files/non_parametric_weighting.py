# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 08:56:20 2019

@author: jjanko
"""

import pandas as pd
import os
import numpy as np
import seaborn as sns

if __name__ == "__main__":
    
    owned_data = pd.read_hdf(os.path.join(r'T:\PhD Students','owned_data.h5'))
    rental_data = pd.read_hdf(os.path.join(r'T:\PhD Students','rental_data.h5'))
    
    incremental=5
    
    
    owned_data['R/V Weighted'] = 0.0
    w_df = {}
    
    for i in owned_data.CITY.unique():
        w_df[i] = {}
        for j in owned_data.year.unique():
            w_df[i][j] = {}
            for q in np.arange(0,100,incremental):
                w_df[i][j][q] = 0.0
    
    for i in owned_data.CITY.unique():
        for j in owned_data.year.unique():
            for q in np.arange(0,100,incremental):
                rental_cy=rental_data.loc[((rental_data['CITY']==i)) & (rental_data['year']==j)]
                owned_cy=owned_data.loc[((owned_data['CITY']==i)) & (owned_data['year']==j)]
                try:
                    rental_den=rental_cy.loc[(rental_cy['RENT']>np.percentile(owned_cy['RENT'], q))  & (rental_cy['RENT']<=np.percentile(owned_cy['RENT'],q+incremental))]
                    owned_den=owned_cy.loc[(owned_cy['RENT']>np.percentile(owned_cy['RENT'], q))  & (owned_cy['RENT']<=np.percentile(owned_cy['RENT'],q+incremental))]
                    if rental_cy.shape[0]==0:
                        density=0
                    else:
                        density=rental_den.shape[0]/rental_cy.shape[0]
                    weight_value=density/(incremental/100)
                    w_df[i][j][q] = weight_value
                except IndexError:
                    pass

    
    owned_data = owned_data.reset_index()
    median = {}
    for i in owned_data.CITY.unique():
        median[i] = {}
        for j in owned_data.year.unique():
            median[j] = {}
            
    
    for i in owned_data.CITY.unique():
        for j in owned_data.year.unique():
            for q in np.arange(0,100,incremental):
                owned_cy=owned_data.loc[((owned_data['CITY']==i)) & (owned_data['year']==j)]
                try:
                    owned_den=owned_cy.loc[(owned_cy['RENT']>np.percentile(owned_cy['RENT'], q))  & (owned_cy['RENT']<=np.percentile(owned_cy['RENT'],q+incremental))]
                    for a in owned_den.index:
                        owned_data.loc[owned_data.index == a, 'R/V Weighted'] = w_df[i][j][q] * owned_data.loc[owned_data.index == a, 'rent_to_price']
                except IndexError:
                    pass
            median[i][j] = owned_data.loc[((owned_data['CITY']==i)) & (owned_data['year']==j)]['R/V Weighted'].median()

    print(pd.DataFrame.from_dict(median))

    owned_data['price_to_rent'] =  owned_data['VALUE'] / (1.0 * owned_data['RENT'] * 12.0)
    for i in owned_data.year.unique():
        sns.distplot(owned_data.loc[owned_data['year']==i,'price_to_rent' ], kde = True, hist = False,kde_kws={'clip': (0.0, 50.0)}, label = i)
    sns.plot.show()
    
    
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 11:54:58 2020

@author: jjanko
"""
import pandas as pd

def get_net_yields(owned_data, rental_data):
    
    insurance = 0.375 / 100.0
    repairs = 0.6 / 100.0
    capex = 1.15 / 100.0
    property_manager = 5.9 / 100.0
    credit_loss = 0.73 / 100.0 
    tax =0.0
    vacancy = 0.0 
    
    #owned_data.index[owned_data['CITY'] == i].tolist()
    
    #states variable
    #original tax files are:
    #(1)Property tax 1990
    #(2)Property tax 2000
    #(3)Property tax 2005-2009
    #(4)Property tax 2010-2014
    
    #I aggragate county level tax rates to state level by using median\average
    #I assign tax rate according to the following rule:
    #(1) 1990 data: 1985-1995
    #(2) 2000 data: 1996-2004
    #(3) 2005-2009 data: 2005-2009
    #(4) 2010-2015 data: 2010-2017
    owned_data=owned_data.reset_index().drop(['index'],axis=1)
    rental_data=rental_data.reset_index().drop(['index'],axis=1)
    owned_data['states']=owned_data['CITY']
    rental_data['states']=rental_data['CITY']
    diction={'Anaheim':'California',
                                              'Atlanta': 'Georgia',
                                            'Baltimore':  'Maryland',
                                            'Boston':  'Massachusetts', 
                                            'Chicago': 'Illinois',
                                            'Cleveland ':'Ohio',
                                              'Dallas':'Texas',
                                            'Detroit':'Michigan',
                                              'Houston':'Texas',
                                            'Kansas City': 'Missouri',
                                          'Los Angeles':'California',
                                              'Miami': 'Florida',
                                         'Minneapolis':'Minnesota',	
                                           'Nassau-Suffolk':'New York',
                                                  'New York': 'New York',
                                                'Newark':'New Jersey',	
                                               'Oakland':'California',
                                        'Oklahoma City':'Oklahoma',
                                      'Philadelphia':'Pennsylvania',
                                               'Phoenix':'Arizona',
                                       'Pittsburgh':'Pennsylvania',
                                           'Riverside': 'California',
                                                'San Diego':'California',
                                               'San Fransico':'California',
                                                'San Jose':'California',
                                                'Washington':'DC',
                                             'Seatle':'Washington',
                                              'St. Louis':'Missouri',
                                                  'Tampa':'Florida'}
    
    owned_data['states']=owned_data.states.map(diction)   
    rental_data['states']=rental_data.states.map(diction) 
    owned_data['tax']=0
    rental_data['tax']=0
    
    #include tax data
    tax_file=r'T:\PhD Students\tax\tax_data.xlsx'
    tax_dta=pd.read_excel(tax_file)

    for i in owned_data['states'].unique():
        owned_data['tax'].loc[(owned_data['states']==i) & (owned_data['year']<=1995) &
                  (owned_data['year']>=1985)]=tax_dta.loc[(tax_dta['State']==i),
                  'Avg resid. Property tax per $1,000 of value in 1990'].tolist()[0]
        
        owned_data['tax'].loc[(owned_data['states']==i) & (owned_data['year']<=2004) &
                  (owned_data['year']>=1996)]=tax_dta.loc[(tax_dta['State']==i),
                  'Avg resid. Property tax per $1,000 of value in 2000'].tolist()[0]
        
        owned_data['tax'].loc[(owned_data['states']==i) & (owned_data['year']<=2009) &
                  (owned_data['year']>=2005)]=tax_dta.loc[(tax_dta['State']==i),
                  'Median RET Rate Per $1,000 of Value for 2005-2009'].tolist()[0]
        
        owned_data['tax'].loc[(owned_data['states']==i) & (owned_data['year']<=2017) &
                  (owned_data['year']>=2010)]=tax_dta.loc[(tax_dta['State']==i),
                  'Average RET Rate Per $1,000 of Value for 2010-2014'].tolist()[0]
        
        
    for j in rental_data['states'].unique():
        rental_data['tax'].loc[(rental_data['states']==j) & (rental_data['year']<=1995) &
                  (rental_data['year']>=1985)]=tax_dta.loc[(tax_dta['State']==j),
                  'Avg resid. Property tax per $1,000 of value in 1990'].tolist()[0]
        
        rental_data['tax'].loc[(rental_data['states']==j) & (rental_data['year']<=2004) &
                  (rental_data['year']>=1996)]=tax_dta.loc[(tax_dta['State']==j),
                  'Avg resid. Property tax per $1,000 of value in 2000'].tolist()[0]
        
        rental_data['tax'].loc[(rental_data['states']==j) & (rental_data['year']<=2009) &
                  (rental_data['year']>=2005)]=tax_dta.loc[(tax_dta['State']==j),
                  'Median RET Rate Per $1,000 of Value for 2005-2009'].tolist()[0]
        
        rental_data['tax'].loc[(rental_data['states']==j) & (rental_data['year']<=2017) &
                  (rental_data['year']>=2010)]=tax_dta.loc[(tax_dta['State']==j),
                  'Average RET Rate Per $1,000 of Value for 2010-2014'].tolist()[0]

 
    
    
    
    tax = owned_data['tax'].copy() / 100.0
    
    owned_data['costs'] = (insurance + repairs + capex + tax) * owned_data['VALUE'] + (property_manager + credit_loss) * owned_data['RENT'] 
              
    owned_data['Net Yields'] = 0.0
              
    owned_data['Net Yields'] = owned_data['RENT'] - owned_data['costs'] 
              
    owned_data['Net Yields'] = owned_data['Net Yields'] / owned_data['VALUE']
    
    return owned_data, rental_data
    
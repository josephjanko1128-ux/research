# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 15:15:13 2019

@author: jjanko
"""

import os
import pandas as pd
import numpy as np
import HelperFunctions

def msi_codes():
    msi_identifier = pd.read_excel(r'C:\Users\jjanko\Desktop\KeyVar.xlsx')
    msi_codes_1985 = msi_identifier[msi_identifier.columns[0:2]].dropna(axis = 0)
    msi_codes_1985['count'] = 0
    msi_codes_1985.set_axis(['code','city','count'], axis = 1, inplace = True)
    msi_codes_2015 = msi_identifier[msi_identifier.columns[4:6]].dropna(axis = 0)
    msi_codes_2015['count'] = 0
    msi_codes_2015.set_axis(['code','city','count'], axis = 1, inplace = True)
    msi_codes_2017 = msi_identifier[msi_identifier.columns[2:4]].dropna(axis = 0)
    msi_codes_2017['count'] = 0
    msi_codes_2017.set_axis(['code','city','count'], axis = 1, inplace = True)
    
    codes = pd.concat([msi_codes_1985, msi_codes_2015, msi_codes_2017], axis = 0).drop_duplicates()
    return codes

if __name__ == "__main__":
    
    codes = msi_codes()
    
    same_smsa = {'35620':5600,'31080':4480,'16980':1600,'19100':1920,'37980':6160,'26420':3360,'47900':8840,'33100':5000,'12060':520,'14460':1120,'41860':7360,'19820':2160,'40140':6780,'38060':6200,'42660':7600,'19740':2080,'38300':6280,'38900':6440,'17140':1640,'17460':1680,'28140':3760,'33340':5080,'32820':4920,'35380':5560,'39580':6640,'33460':5120,'45300':8280,'12580':720,'41700':7240,'29820':4120,'41940':7400,'36420':5880,'40060':6760,'13820':1000,'40380':6840}
    same_smsa_back = {'5600': 35620, '4480': 31080, '1600': 16980, '1920': 19100, '6160': 37980, '3360': 26420, '8840': 47900, '5000': 33100, '520': 12060, '1120': 14460, '7360': 41860, '2160': 19820, '6780': 40140, '6200': 38060, '7600': 42660, '2080': 19740, '6280': 38300, '6440': 38900, '1640': 17140, '1680': 17460, '3760': 28140, '5080': 33340, '4920': 32820, '5560': 35380, '6640': 39580, '5120': 33460, '8280': 45300, '720': 12580, '7240': 41700, '4120': 29820, '7400': 41940, '5880': 36420, '6760': 40060, '1000': 13820, '6840': 40380}
    
    eisfeldt_top_30 = {"6280": "Pittsburgh","7040": "St. Louis","3760": "Kansas City","3360": "Houston","1920": "Dallas","5880": "Oklahoma City","1680": "Cleveland ","6160": "Philadelphia","520": "Atlanta","5120": "Minneapolis","7600": "Seatle","720": "Baltimore","5380": "Nassau-Suffolk","5680": "Virginia Beach","1600": "Chicago","8280": "Tampa","8840": "Washington","5000": "Miami","7360": "San Fransico","1120": "Boston","7320": "San Diego","7400": "San Jose","360": "Anaheim","2160": "Detroit","5640": "Newark","5600": "New York","5775": "Oakland","4480": "Los Angeles","6200": "Phoenix","6780": "Riverside"}

    
    
    value_freq = {}
    
    filepath = r'T:\PhD Students\ftp_data_census'
    for item in os.listdir(filepath):
        if item[0] == 'n' or item[0] == 'm':
            data = pd.read_csv(os.path.join(filepath, item))
            year = int(item.split(".")[0][1:])
            if year != 1111985:
                if year >=  2015:
                    year_freq = data['OMB13CBSA'].value_counts().to_dict()
                else:
                    year_freq = data['SMSA'].value_counts().to_dict()
                
                for i in year_freq.keys():
                    codes.loc[codes.code == i,'count'] = codes.loc[codes.code == i,'count'].copy() + year_freq[i]
                    
    """      
    for z in same_smsa_back.keys():
        try:
            codes.loc[codes.code == int(z),'count'] = codes.loc[codes.code == int(z),'count'].values[0] + codes.loc[codes.code == same_smsa_back[z],'count'].values[0]
        except IndexError:
            pass
    """ 
    ranking = codes.sort_values('count', ascending = False).head(30) 
    vals = ranking['code'].tolist()
    
    #sort by eisfeldt top 30
    vals = []
    for iterate in eisfeldt_top_30.keys():
        vals.append(float(iterate))
    
    
    _vals = []
    for v in vals:
        if str(int(v)) in same_smsa_back.keys():
            _vals.append(same_smsa_back[str(int(v))])
    
    hedonic_model_data = pd.DataFrame()
    sample = {}
    for item in os.listdir(filepath):
        if item[0] == 'n' or item[0] == 'm':
            data = pd.read_csv(os.path.join(filepath, item))
            year = int(item.split(".")[0][1:])
            if year not in sample.keys():
                sample[year] = 0.0
            if year >=  2015:
                year_freq = data['OMB13CBSA'].value_counts().to_dict()
                filtered = data.loc[data['OMB13CBSA'].isin(_vals)]
                sample[year] = len(filtered) + sample[year]
            else:
                year_freq = data['SMSA'].value_counts().to_dict()
                filtered = data.loc[data['SMSA'].isin(vals)]
                sample[year] = len(filtered) + sample[year]
                
            filtered.loc[:,'year'] = year
            filtered.loc[:,'log rent'] = np.log(filtered.loc[:,'RENT'])
            
            if year >= 2015:
                output = filtered[['year','CONDO','TENURE','OMB13CBSA' ,'log rent', 'TOTROOMS', 'BATHROOMS', 'ACPRIMARY','BLD','YRBUILT', 'BEDROOMS']]
                output = HelperFunctions.check_col_float(['CONDO','TOTROOMS', 'BATHROOMS', 'ACPRIMARY','BLD','YRBUILT', 'BEDROOMS'], output)
                output.loc[:,'ROOMS'] = output.loc[:,'TOTROOMS'] 
                output.loc[:,'BATHS'] = output.loc[:,'BATHROOMS'] 
                output.loc[:,'AIRSYS'] = output.loc[:,'ACPRIMARY'] 
                output.loc[:,'TYPE'] = output.loc[:,'BLD']
                output.loc[:,'BUILT'] = output.loc[:,'YRBUILT']
                output.loc[:,'MSA'] = output.loc[:,'OMB13CBSA']
                output.loc[:,'BEDRMS'] = output.loc[:,'BEDROOMS']
                output['NUNIT2'] = 'none'
                for itera in same_smsa.keys():
                    output.loc[output.MSA == int(itera),'MSA'] = same_smsa[itera]
            else:
                try:
                    output = filtered[['year','NUNIT2','CONDO','TENURE','SMSA' ,'log rent', 'ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS']]
                    output = HelperFunctions.check_col_float(['NUNIT2','CONDO','ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS'], output)
                    output.loc[:,'MSA'] = output.loc[:,'SMSA']
                except KeyError:
                    output = filtered[['year','nunit2','CONDO','TENURE','SMSA' ,'log rent', 'rooms', 'BATHS', 'airsys', 'type', 'BUILT','BEDRMS']]
                    output = HelperFunctions.check_col_float(['nunit2','CONDO','rooms', 'BATHS', 'airsys', 'type', 'BUILT','BEDRMS'], output)
                    output.loc[:,'MSA'] = output.loc[:,'SMSA']
                    output.loc[:,'ROOMS'] = output.loc[:,'rooms']
                    output.loc[:,'AIRSYS'] = output.loc[:,'airsys']
                    output.loc[:,'TYPE'] = output.loc[:,'type']
                    output.loc[:,'NUNIT2'] = output.loc[:,'nunit2']
                    
                    
                    
            output = output[['year','NUNIT2','CONDO','TENURE','MSA' ,'log rent', 'ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS']]
                
            if item[0] == 'm':
                output.to_csv(os.path.join( r'T:\PhD Students\filtered_data_top30','m' + str(year) + '.csv' ))
            else:
                output.to_csv(os.path.join( r'T:\PhD Students\filtered_data_top30','n' + str(year) + '.csv' ))
            

            if len(hedonic_model_data.index) == 0:
                hedonic_model_data = output.copy()
            else:
                hedonic_model_data = pd.concat([hedonic_model_data, output.copy()], axis = 0)
    hedonic_model_data.to_hdf(os.path.join(r'T:\PhD Students','hedonic_data.h5'), key = 'df')


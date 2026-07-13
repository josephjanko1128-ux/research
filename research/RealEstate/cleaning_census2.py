# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 16:30:07 2019
@author: jjanko
"""

import os
import pandas as pd


def getDirectories(root_dir):
    df_dir = []
    for item in os.listdir(root_dir):
        item_full_path = os.path.join(root_dir, item)
        if os.path.isdir(item_full_path):
            df_dir.append(item_full_path)
    return df_dir

def getFlatFiles(filepath):
    
    
    for item in os.listdir(filepath):
        if os.path.isdir(os.path.join(filepath, item)) and ('CSV' in item):
            
            if ('National' in item) and ('CSV' in item) :
                print(item)
                file_to_read = os.listdir(os.path.join(filepath, item))[0]
                national_file = os.path.join(filepath, item, file_to_read) 
            elif ('Metro' in item) and ('CSV' in item):
                print(item)
                file_to_read = os.listdir(os.path.join(filepath, item) )[0]
                metro_file = os.path.join(filepath, item, file_to_read)
                
    if '2013' not in national_file:
        national_file = pd.read_csv(national_file,chunksize=500)
    else:
        #handle error in 2013 data file
        r1 = pd.read_csv(national_file, nrows = 1, header = None).values.tolist()[0]
        r2 = pd.read_csv(national_file, skiprows =1, nrows = 1, header = None).values.tolist()[0]
        h = r1 + r2
        national_file = pd.read_csv(national_file, skiprows =2, header = None, names = h, chunksize = 500)

    try:
        metro_file = pd.read_csv(metro_file,chunksize=500)
    except:
        metro_file = -1

        
    return national_file, metro_file

def check_col_float(header_list, df):
    for col in header_list:
        try:
            df.loc[:,col] = df.loc[:,col]
        except AttributeError:
            pass
        except KeyError:
            try:
                df[:,col.upper()] = df[:,col.lower()]
            except AttributeError:
                df[:,col.upper()] = df[:,col.lower()]
    return df

def check_col_float2(header_list, df):
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

def filter_data(file, filename):
    
    msi_identifier = pd.read_excel(r'C:\Users\jjanko\Desktop\KeyVar.xlsx')
    year = int(filename.split('\\')[-1])
    
    if year not in [2015,2017]:
        msi_codes = msi_identifier[msi_identifier.columns[0:2]].dropna(axis = 0)
    elif year == 2015:
        msi_codes = msi_identifier[msi_identifier.columns[4:6]].dropna(axis = 0)
    else:
        msi_codes = msi_identifier[msi_identifier.columns[2:4]].dropna(axis = 0)

        
    available_codes = msi_codes[msi_codes.columns[0]].unique().tolist()
    
    year = int(filename.split('\\')[-1])

    
    filtered_file = pd.DataFrame()
    
    
    for data_chunk in file:
        #check to see if their is a msi code
        #filter_rows = data_chunk
        #filter by the msi codes
        filter_rows = pd.DataFrame()

        if year not in [2015,2017]:
            try:
                data_chunk.loc[:,['SMSA']] = data_chunk['SMSA'].apply(lambda x: float(x.strip("'")))
            except AttributeError:
                pass
            
            filter_rows = data_chunk.loc[data_chunk['SMSA'].isin(available_codes)]
        else:
            try:
                data_chunk.loc[:,['OMB13CBSA']] = data_chunk['OMB13CBSA'].apply(lambda x: float(x.strip("'")))
            except AttributeError:
                pass
            filter_rows = data_chunk.loc[data_chunk['OMB13CBSA'].isin(available_codes)]
        
        #add filtered row to new df dataframe
        if len(filter_rows.index) != 0:
            if len(filtered_file.index) == 0:
                filtered_file = filter_rows.copy()
            else:
                filtered_file = pd.concat([filtered_file, filter_rows.copy()], axis = 0)
        
    return filtered_file

def clean_var(df, year):
    df.loc[:,'year'] = year
    
    if 'VACANC' in df.columns.tolist():
        df.loc[:,'VACANCY'] = df.loc[:,'VACANC']
    
    
    if year >= 2015:
        
        df = df[['year','RENT','HINCP','WINBARS','RENTCNTRL','WINBARS','MARKETVAL','CONDO','TENURE','OMB13CBSA' , 'TOTROOMS', 'BATHROOMS', 'ACPRIMARY','BLD','YRBUILT', 'BEDROOMS','WEIGHT']]
        df = df.loc[:,~df.columns.duplicated()]
        df = check_col_float2(['RENT','HINCP','WINBARS','RENTCNTRL','MARKETVAL','CONDO','TOTROOMS', 'BATHROOMS', 'ACPRIMARY','BLD','YRBUILT', 'BEDROOMS','WEIGHT','TENURE'], df)
        df.loc[:,'ROOMS'] = df.loc[:,'TOTROOMS'] 
        df.loc[:,'BATHS'] = df.loc[:,'BATHROOMS'] 
        df.loc[:,'AIRSYS'] = df.loc[:,'ACPRIMARY'] 
        df.loc[:,'TYPE'] = df.loc[:,'BLD']
        df.loc[:,'BUILT'] = df.loc[:,'YRBUILT']
        df.loc[:,'SMSA'] = df.loc[:,'OMB13CBSA']
        df.loc[:,'BEDRMS'] = df.loc[:,'BEDROOMS']
        df.loc[:,'VALUE'] = df.loc[:,'MARKETVAL']
        df.loc[:,'RCNTRL'] = df.loc[:,'RENTCNTRL']
        df.loc[:,'ZINC2'] = df.loc[:,'HINCP']
        df.loc[:,'EBAR'] = df.loc[:,'WINBARS']
        df.loc[:,'WEIGHT'] = df.loc[:,'WEIGHT']
        df['NUNIT2'] = 'none'

    else:
        try:
            df = df[['year','RENT','ZINC2','EBAR','RCNTRL','VALUE','NUNIT2','CONDO','TENURE','SMSA' , 'ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS','WEIGHT', 'VACANCY']]
            df = check_col_float2(['ZINC2','EBAR','RCNTRL','VALUE','RCNTRL','NUNIT2','CONDO','ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS','WEIGHT','TENURE', 'VACANCY'], df)
            df.loc[:,'MSA'] = df.loc[:,'SMSA']
        except KeyError:
            df = df[['year','RENT','zinc2','EBAR','rcntrl','VALUE','nunit2','CONDO','TENURE','SMSA' , 'rooms', 'BATHS', 'airsys', 'type', 'BUILT','BEDRMS','weight', 'VACANCY']]
            df = check_col_float2(['RENT','zinc2','EBAR','rcntrl','VALUE','nunit2','CONDO','rooms', 'BATHS', 'airsys', 'type', 'BUILT','BEDRMS','weight','TENURE', 'VACANCY'], df)
            df.loc[:,'MSA'] = df.loc[:,'SMSA']
            df.loc[:,'ROOMS'] = df.loc[:,'rooms']
            df.loc[:,'AIRSYS'] = df.loc[:,'airsys']
            df.loc[:,'TYPE'] = df.loc[:,'type']
            df.loc[:,'NUNIT2'] = df.loc[:,'nunit2']
            df.loc[:,'ZINC2'] = df.loc[:,'zinc2']
            df.loc[:,'RCNTRL'] = df.loc[:,'rcntrl']
            df.loc[:,'WEIGHT'] = df.loc[:,'weight']
     
    df = df[['year','RENT','ZINC2','EBAR','RCNTRL','VALUE','NUNIT2','CONDO','TENURE','SMSA' , 'ROOMS', 'BATHS', 'AIRSYS', 'TYPE', 'BUILT','BEDRMS','WEIGHT','VACANCY']]
    
    
    return df

if __name__ == "__main__":
     
    samples = {}
    sample_n = {}
    sample_m = {}
    
    root_dir = r'T:\PhD Students\ftp_data_census3'
    years_data = getDirectories(root_dir)
    
    for years in years_data:

        year = int(years.split('\\')[-1])
        
        if year >= 1985 and year <= 2013:
            if year not in samples.keys():
                samples[year] = 0.0
                sample_n[year] = 0.0
                sample_m[year] = 0.0
            if year >= 1:
                nfile, mfile = getFlatFiles(years)
                
                
                clean_nfile_ = filter_data(nfile, years)
                clean_nfile = clean_var(clean_nfile_, year)
                out = clean_nfile.copy()
                #clean_nfile.to_hdf(os.path.join('\\'.join(years.split('\\')[0:-1]),'n' + str(year) + '.h5' ),key = 'df')
                samples[year] = len(clean_nfile)
                sample_n[year] = len(clean_nfile)
                if mfile != -1:
                    clean_mfile_ = filter_data(mfile, years)
                    samples[year] = len(clean_mfile_) + samples[year]
                    sample_m[year] = len(clean_mfile_)
                    clean_mfile = clean_var(clean_mfile_, year)
                    out = pd.concat([clean_nfile, clean_mfile], axis = 0)
                    #clean_mfile.to_hdf(os.path.join('\\'.join(years.split('\\')[0:-1]),'m' + str(year) + '.h5' ),key = 'df')
                out.to_hdf(os.path.join('\\'.join(years.split('\\')[0:-1]),'o' + str(year) + '.h5' ),key = 'df', mode = 'w')
    print(pd.DataFrame.from_dict(samples, orient = 'index'))
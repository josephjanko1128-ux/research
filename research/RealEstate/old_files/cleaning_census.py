import os
import pandas as pd
import HelperFunctions



def getDirectories(root_dir):
    output_dir = []
    for item in os.listdir(root_dir):
        item_full_path = os.path.join(root_dir, item)
        if os.path.isdir(item_full_path):
            output_dir.append(item_full_path)
    return output_dir

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
            df.loc[:,col] = df[col].apply(lambda x: float(x.strip("'"))).copy()
        except AttributeError:
            pass
        except KeyError:
            try:
                df[col.upper()] = df[col.lower()].apply(lambda x: float(x.strip("'"))).copy()
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
            

        if year >= 2015:
            filter_heads = ['TENURE','RENT','HINCP','RENTCNTRL', 'WINBARS','MARKETVAL']
            
        else:
            filter_heads = ['TENURE','RENT', 'ZINC2','RCNTRL', 'EBAR','VALUE'] 
            
        filter_rows = check_col_float(filter_heads, filter_rows)
            
        
        


        #filter for rent control
        if year >= 2015:
            filter_rows = filter_rows.loc[filter_rows['RENTCNTRL'].isin([2,-6])]
        else:
            filter_rows = filter_rows.loc[filter_rows['RCNTRL'].isin([2,-6])]
        
        #filter for tenure status
        filter_rows = filter_rows.loc[filter_rows['TENURE'].isin([1,2])].copy()
       
        filter_rows = filter_rows.loc[filter_rows['RENT'] != -6. ]
        filter_rows = filter_rows.loc[filter_rows['RENT'] > 0  ]
        
        #filter for ratio of household income to annual rent
        if year >= 2015:
            filter_rows = filter_rows.loc[filter_rows['HINCP'] != -6. ]
            
            filter_rows = filter_rows.loc[(filter_rows['HINCP'] /(12. * filter_rows['RENT'])) <= 100. ] 
        else:
            filter_rows = filter_rows.loc[filter_rows['ZINC2'] != -6. ]
            filter_rows = filter_rows.loc[(filter_rows['ZINC2'] /(12. * filter_rows['RENT'])) <= 100. ]       
            
        #filter for data errors in house value field
        
        if year >= 2015:
            #filter_rows = filter_rows.loc[filter_rows['MARKETVAL'] != -6. ]
            filter_rows = filter_rows[(filter_rows['HINCP'] /filter_rows['MARKETVAL']) <= 2. ] 
        else:
            #filter_rows = filter_rows.loc[filter_rows['VALUE'] != -6. ]
            filter_rows = filter_rows[(filter_rows['ZINC2'] /filter_rows['VALUE']) <= 2. ]    
        
                         
        
        
        #add filtered row to new output dataframe
        if len(filter_rows.index) != 0:
            if len(filtered_file.index) == 0:
                filtered_file = filter_rows.copy()
            else:
                filtered_file = pd.concat([filtered_file, filter_rows.copy()], axis = 0)
        
    return filtered_file
    
            
    
        
if __name__ == "__main__":
     
    """
    2015-2017
    HINCP- Household Income past 12 months
    FINCP- Family Income (past 12 months)
    WINBARS- windowns with metal bars
    RENT- monthly rent amount
    RENTCNTRL- rent control
    MARKETVAL- current market value of house unit
    
    
    Before 2015
    ZINC2- Household income
    ZINC- family income
    EBAR- windows covered with metal bars
    RCNTRL- indicates rent control
    RENT- monthly rent amount
    VALUE- Current market value of this housing unit
    
    """
    samples = {}
    sample_n = {}
    sample_m = {}
    
    root_dir = r'T:\PhD Students\ftp_data_census'
    years_data = getDirectories(root_dir)
    
    for years in years_data:

        year = int(years.split('\\')[-1])
        if year not in samples.keys():
            samples[year] = 0.0
            sample_n[year] = 0.0
            sample_m[year] = 0.0
        if year >= 1:
            nfile, mfile = getFlatFiles(years)
            
            
            clean_nfile = filter_data(nfile, years)
            clean_nfile.to_csv(os.path.join('\\'.join(years.split('\\')[0:-1]),'n' + str(year) + '.csv' ))
            samples[year] = len(clean_nfile)
            sample_n[year] = len(clean_nfile)
            if mfile != -1:
                clean_mfile = filter_data(mfile, years)
                samples[year] = len(clean_mfile) + samples[year]
                sample_m[year] = len(clean_mfile)
                clean_mfile.to_csv(os.path.join('\\'.join(years.split('\\')[0:-1]),'m' + str(year) + '.csv' ))
    print(pd.DataFrame.from_dict(samples, orient = 'index'))
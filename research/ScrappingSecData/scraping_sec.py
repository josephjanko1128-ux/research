# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 08:14:46 2021

@author: jjanko
"""



from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve
import os
import pandas as pd
import textract

#########################################################################################################################################
#Helper functions

def num_there(s):
    return any(i.isdigit() for i in s)

#########################################################################################################################################

#Administrative Proceedings Archive
def get_administrative_proceedings():

    output_path = os.path.join(r'C:\Users\jjanko\Desktop\sec_scrap2','admistrative_proceedings' )
    
    base_url  = "https://www.sec.gov/litigation/admin/adminarchive/adminarc"
    
    i = 2021
    while i >= 1995:

        if not os.path.exists(os.path.join(output_path, str(i))):
            os.makedirs(os.path.join(output_path, str(i)))
        
        if i == 2020:
            url = base_url + str(i) + '.htm'
        elif i == 2021:
            url = 'https://www.sec.gov/litigation/admin.htm'
        else:
            url = base_url + str(i) + '.shtml'
        req = Request(url)
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, features="lxml")
        for link in soup.findAll('a', href=True):
            if 'waiver' not in str(link['href']).lower():
                if 'pdf' in link['href'] and num_there(link.get_text()) and '-' in str(link.get_text()):
                    try:
                        url2 =  'https://www.sec.gov/' + link['href']
                        output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.pdf')
                        urlretrieve(url2, output_path_file)
                    except:
                        pass
                        #the link is not in a pdf format
                    
                if 'htm' in link['href'] and num_there(link.get_text()) and '-' in str(link.get_text()):
                    
                    try:
                        url2 =  'https://www.sec.gov/' + link['href']
                        req = Request(url2)      
                        html_page = urlopen(req)
                        soup = BeautifulSoup(html_page, features="lxml")
                        txt = soup.get_text()
                        output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                        file1 = open(output_path_file, "w")
                        file1.write(txt)
                        file1.close()
                    except:
                        pass
                    
                if 'txt' in link['href'] and num_there(link.get_text()) and '-' in str(link.get_text()):
                    
                    try:
                        url2 =  'https://www.sec.gov/' + link['href']
                        req = Request(url2)      
                        html_page = urlopen(req)
                        soup = BeautifulSoup(html_page, features="lxml")
                        txt = soup.get_text()
                        output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                        file1 = open(output_path_file, "w")
                        file1.write(txt)
                        file1.close()
                    except:
                        pass
                
        i = i - 1 
    
#########################################################################################################################################    

#Accounting and Auditing Enforcement Releases archives
def get_accounting_auditing():
    
    output_path = os.path.join(r'C:\Users\jjanko\Desktop\sec_scrap2','accounting_auditing_enforcement_releases' )
    
    base_url  = "https://www.sec.gov/divisions/enforce/friactions/friactions"
    
    i = 2021
    while i >= 1999:
        if not os.path.exists(os.path.join(output_path, str(i))):
            os.makedirs(os.path.join(output_path, str(i)))
        
        if i == 2020:
            url = base_url + str(i) + '.htm'
        elif i == 2021:
            url = "https://www.sec.gov/divisions/enforce/friactions.htm"
        else:
            url = base_url + str(i) + '.shtml'
        req = Request(url)
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, features="lxml")
        for link in soup.findAll('a', href=True):
            if 'pdf' in link['href'] and num_there(link.get_text()) and 'AAER' in str(link.get_text()):
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.pdf')
                    urlretrieve(url2, output_path_file)
                except:
                    pass
                    #the link is not in a pdf format
                
            if 'htm' in link['href'] and num_there(link.get_text()) and 'AAER' in str(link.get_text()):
                
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    req = Request(url2)      
                    html_page = urlopen(req)
                    soup = BeautifulSoup(html_page, features="lxml")
                    txt = soup.get_text()
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                    file1 = open(output_path_file, "w")
                    file1.write(txt)
                    file1.close()
                except:
                    pass
                
            if 'txt' in link['href'] and num_there(link.get_text()) and 'AAER' in str(link.get_text()):
                
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    req = Request(url2)      
                    html_page = urlopen(req)
                    soup = BeautifulSoup(html_page, features="lxml")
                    txt = soup.get_text()
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                    file1 = open(output_path_file, "w")
                    file1.write(txt)
                    file1.close()
                except:
                    pass
                    
        i = i - 1 

#########################################################################################################################################

#Litigation Releases Archive
def get_litigation():
    
    output_path = os.path.join(r'C:\Users\jjanko\Desktop\sec_scrap2','litigation_releases' )
    
    base_url  = "https://www.sec.gov/litigation/litreleases/litrelarchive/litarchive"
    
    i = 2021
    while i >= 1995:
        if not os.path.exists(os.path.join(output_path, str(i))):
            os.makedirs(os.path.join(output_path, str(i)))
        
        if i == 2020:
            url = base_url + str(i) + '.htm'
        elif i == 2021:
            url = 'https://www.sec.gov/litigation/litreleases.htm'
        else:
            url = base_url + str(i) + '.shtml'
            
        req = Request(url)
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, features="lxml")
        for link in soup.findAll('a', href=True):
            
            if 'pdf' in link['href'] and num_there(link.get_text()) and 'lr' in link['href']:
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.pdf')
                    urlretrieve(url2, output_path_file)
                except:
                    pass
                    #the link is not in a pdf format
                
            if 'htm' in link['href'] and num_there(link.get_text()) and 'lr' in link['href']:
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    req = Request(url2)      
                    html_page = urlopen(req)
                    soup = BeautifulSoup(html_page, features="lxml")
                    txt = soup.get_text()
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                    file1 = open(output_path_file, "w")
                    file1.write(txt)
                    file1.close()
                except:
                    pass
                
            if 'txt' in link['href'] and num_there(link.get_text()) and 'lr' in link['href']:
                
                try:
                    url2 =  'https://www.sec.gov/' + link['href']
                    req = Request(url2)      
                    html_page = urlopen(req)
                    soup = BeautifulSoup(html_page, features="lxml")
                    txt = soup.get_text()
                    output_path_file = os.path.join(output_path,str(i), str(link.get_text()) + '.txt')
                    file1 = open(output_path_file, "w")
                    file1.write(txt)
                    file1.close()
                except:
                    pass
                
        i = i - 1 
        
#########################################################################################################################################
def get_results():
    
    rootDir = r'C:\Users\jjanko\Desktop\sec_scrap2'
    df = pd.DataFrame(columns = ['Release Type', 'Year', 'FileName', '13B' , 'FCPA', 'Foreign Corrupt', 'dd-1','dd-2', 'dd-3', '30A', 'foreign corrupt practices act'])
    error_files = []
    
    subDir = ['accounting_auditing_enforcement_releases', 'litigation_releases', 'admistrative_proceedings']
    for sub in subDir:
        subDirName = os.path.join(rootDir, sub)
        year_folder = [x[0] for x in os.walk(subDirName)]
        for subyear in year_folder:
            if subyear.split('\\')[-1].isnumeric():
                f_read = os.listdir(subyear)
                for fil in f_read:
                    try:
                        fil_path = os.path.join(subyear, fil)
                        text = str(textract.process(fil_path)).lower().replace(' ','').replace('\n','')
                        found = False
                        foundFCPA = False
                        foundForeignCorrupt = False
                        found_dd1 = False
                        found_dd2 = False
                        found_dd3 = False
                        found_30a = False
                        found_foreign_corrupt_act= False
                        
                        if '13(b)' in text and 'violation' in text:
                            found = True
                        if 'fcpa' in text:
                            foundFCPA = True
                        if 'foreigncorrupt' in text:
                            foundForeignCorrupt = True
                        if 'dd-1' in text:
                            found_dd1 = True
                        if 'dd-2' in text:
                            found_dd2 = True
                        if 'dd-3' in text:
                            found_dd3 = True                            
                        if '30a' in text:
                            found_30a = True     
                        if 'foreigncorruptpracticesact' in text:
                            found_foreign_corrupt_act= True
                        
                        df.loc[len(df)] = [sub, subyear.split('\\')[-1], fil, found, foundFCPA,foundForeignCorrupt,found_dd1,found_dd2,found_dd3,found_30a,found_foreign_corrupt_act]
                        #get bribery results
                        
                    except:
                        error_files.append(fil_path)
                        
    df.to_csv(os.path.join(rootDir,'unfiltered_output.csv'))
    
    df.loc[df['13B']==True].to_csv(os.path.join(rootDir,'filtered_output.csv'))
    
    return df, error_files
    
        

#########################################################################################################################################
if __name__ == "__main__":

    #get_administrative_proceedings()
    #get_accounting_auditing()
    #get_litigation()
    df, error_files = get_results()
    

                    

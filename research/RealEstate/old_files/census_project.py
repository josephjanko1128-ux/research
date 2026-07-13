# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 19:00:08 2019

@author: jjanko
"""

#import modules

import os
from io import BytesIO
from zipfile import ZipFile
import requests, zipfile, io
import csv



class DataDirectory():
    
    def __init__(self):
        self.years = []
        self.links = []
        for i in range(1985,2019,2):
            self.years.append(i)
        self.links = {'2017':"http://www2.census.gov/programs-surveys/ahs/2017/AHS%202017%20National%20PUF%20v3.0%20CSV.zip?#",\
                      '2015':"http://www2.census.gov/programs-surveys/ahs/2015/AHS%202015%20National%20PUF%20v3.0%20CSV.zip?#",\
                      '2013':"http://www2.census.gov/programs-surveys/ahs/2013/AHS%202013%20National%20PUF%20v1.3%20CSV.zip?#",\
                      '2011':"http://www2.census.gov/programs-surveys/ahs/2011/AHS%202011%20National%20PUF%20v2.0%20CSV.zip?#",\
                      '2009':"http://www2.census.gov/programs-surveys/ahs/2009/AHS%202009%20National%20PUF%20v1.1%20CSV.zip?#",\
                      '2007':"http://www2.census.gov/programs-surveys/ahs/2007/AHS%202007%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '2005':"http://www2.census.gov/programs-surveys/ahs/2005/AHS%202005%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '2003':"http://www2.census.gov/programs-surveys/ahs/2003/AHS%202003%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '2001':"http://www2.census.gov/programs-surveys/ahs/2001/AHS%202001%20National%20PUF%20v1.1%20CSV.zip?#",\
                      '1999':"http://www2.census.gov/programs-surveys/ahs/1999/AHS%201999%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '1997':"http://www2.census.gov/programs-surveys/ahs/1997/AHS%201997%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '1995':"http://www2.census.gov/programs-surveys/ahs/1995/AHS%201995%20National%20PUF%20v1.1%20CSV.zip?#",\
                      '1993':"http://www2.census.gov/programs-surveys/ahs/1993/AHS%201993%20National%20PUF%20v1.1%20CSV.zip?#",\
                      '1991':"http://www2.census.gov/programs-surveys/ahs/1991/AHS%201991%20National%20PUF%20v1.1%20CSV.zip?#",\
                      '1989':"http://www2.census.gov/programs-surveys/ahs/1989/AHS%201989%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '1987':"http://www2.census.gov/programs-surveys/ahs/1987/AHS%201987%20National%20PUF%20V1.1%20CSV.zip?#",\
                      '1985':"http://www2.census.gov/programs-surveys/ahs/1985/AHS%201985%20National%20PUF%20v1.1%20CSV.zip?#"}
    
    def checkforDirect(self):
        currentDataDirect = os.path.join(os.getcwd(), "NetYieldData")
        self.workingFolder = currentDataDirect
        if not os.path.exists(currentDataDirect):
            os.mkdir(currentDataDirect)
            for i in self.years:
                os.mkdir(os.path.join(self.workingFolder, str(i)))
        
        
    def get_zip(self,file_url):
        url = requests.get(file_url)
        zipfile = ZipFile(BytesIO(url.content))
        zip_names = zipfile.namelist()
        if len(zip_names) == 1:
            file_name = zip_names.pop()
            extracted_file = zipfile.open(file_name)
            return extracted_file
        return [zipfile.open(file_name) for file_name in zip_names]
            
    def getLinksforData(self):
        
        for i in self.years:
            print(i)
            url = self.links[str(i)]
            
            r = requests.get(url, stream =True)
            check = zipfile.is_zipfile(io.BytesIO(r.content))
            z = zipfile.ZipFile(io.BytesIO(r.content))
            while not check:
                r = requests.get(url, stream =True)
                check = zipfile.is_zipfile(io.BytesIO(r.content))
            else:
                z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(os.path.join(self.workingFolder, str(i)))
        

            
        
        
        

class NetYieldPanelData():
    
    def __init__(self):
        pass
    
    
if __name__ == "__main__":
    
    #create the net yield data
    data = DataDirectory()
    data.checkforDirect()
    y = data.getLinksforData()
    """
    with open(y[1],'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            print(row)
    """
            
    
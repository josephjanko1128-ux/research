# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 15:38:22 2019

@author: jjanko
"""

from ftplib import FTP
import os, zipfile
import shutil 
import time



"""
years = []
for i in range(1985,2019,2):
    years.append(i)
"""

years = []
for i in range(2007,2019,2):
    years.append(i)
    
ftp = FTP("ftp2.census.gov")
ftp.login()
ftp.cwd(r"programs-surveys/ahs/")

for i in years:
    
    

    fiList = ftp.nlst(str(i))

    for j in fiList:
        print(j)
        if ('SAS' not in j) and ('tables' not in j) and ('factsheets' not in j) and ('infographs' not in j):
            if 'zip' not in j:
                ftp.retrbinary('RETR ' + j, open(j.split('/')[1], 'wb').write)
                if not os.path.exists(os.path.join(r'M:\python\ftp_data_census',str(i))):
                    os.mkdir(os.path.join(r'M:\python\ftp_data_census',str(i)))
                shutil.move(os.path.join(os.getcwd(), j.split('/')[1]),os.path.join(r'M:\python\ftp_data_census',str(i),j.split('/')[1]))
            if ('zip' in j) and ('CSV' in j):
                ftp.retrbinary('RETR ' + j, open(j.split('/')[1], 'wb').write)
                if not os.path.exists(os.path.join(r'M:\python\ftp_data_census',str(i))):
                    os.mkdir(os.path.join(r'M:\python\ftp_data_census',str(i)))
                zp = zipfile.ZipFile(os.path.join(os.getcwd(), j.split('/')[1]))
                if not os.path.exists(os.path.join(r'M:\python\ftp_data_census',str(i),j.split('/')[1])):
                    os.mkdir(os.path.join(r'M:\python\ftp_data_census',str(i),j.split('/')[1]))                
                zp.extractall(os.path.join(r'M:\python\ftp_data_census', str(i),j.split('/')[1]))
                zp.close()

ftp.quit()
ftp.close()
time.sleep(5)
del ftp

    
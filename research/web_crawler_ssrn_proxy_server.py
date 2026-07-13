# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 07:09:31 2019

@author: jjanko
"""


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import os


def get_proxy():
    p_list = {}
    res = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(res.text,"lxml")
    table_data = [i.text for i in soup.find_all('td')]
    count = 0
    for i in table_data:
        if i.find('.') != -1:
            p_list[i] = {'port': table_data[count + 1], 'code': table_data[count + 2], 'country':table_data[count + 3],\
                   'anonymity':table_data[count + 4],'google':table_data[count + 5],'https':table_data[count + 6],\
                   'last_checked':table_data[count + 7] }        
        count = count + 1
    return p_list

if __name__ == '__main__':
    os.chdir(os.getcwd())
    proxyList = get_proxy()
    
    for i in proxyList.keys():
        if proxyList[i]['https']  == 'yes':
            firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            PROXY = i + ":" + str(proxyList[i]['port'])
            firefox_capabilities['proxy'] = {"proxyType": "MANUAL","httpProxy": PROXY,"ftpProxy": PROXY,"sslProxy": PROXY}
            
    
            
            driver = webdriver.Firefox(executable_path=r"C:\Users\jjanko\Documents\Python Scripts\geckodriver.exe", capabilities=firefox_capabilities)
            driver.get("http://www.iplocation.net/find-ip-address")
            input("Please enter an input \n")
            driver.quit()
        
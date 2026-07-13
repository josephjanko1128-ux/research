# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 17:18:28 2019

@author: jjanko
"""

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




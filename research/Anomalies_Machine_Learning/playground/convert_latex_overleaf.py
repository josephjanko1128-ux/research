# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 07:54:56 2021

@author: jjanko
"""

import pandas as pd
import os


cd = os.getcwd()

#file_convert = r'D:\janko_machine_learning\playground\backtests\outputs\output_results_latex_scaled_24_12.txt'
file_convert = r'D:\janko_machine_learning\playground\backtests_spy\outputs\output_results_latex_24_12.txt'

File_object = open(file_convert,"r")

fl = File_object.readlines()

File_object.close()

c= []
for f in fl:
    if 'begin{table}' in f:
        cleaned_fl = '\\begin{table}[H]\n'
        c.append(cleaned_fl)
    elif 'end{table}' in f:
        c.append(f)
        c.append('\n')
    elif 'begin{tabular}' in f:
        c.append('\\begin{adjustbox}{max width=\\textwidth} \n')
        c.append(f)
    elif 'end{tabular}' in f:
        c.append(f)
        c.append('\\end{adjustbox} \n')
    elif 'caption' in f and '_' in f:
        fc = f.replace('_', ' ')
        fc = fc.replace('{','{\\: ' )
        c.append(fc)
    else:
        c.append(f)

of = open(os.path.join(cd, 'outputs_overleaf',file_convert.split('\\')[-1] ), 'w+')
of.writelines(c)
of.close()

        

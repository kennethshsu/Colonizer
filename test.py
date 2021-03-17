#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 15:27:38 2021

@author: qikechen
"""

# write to csv file
import csv

# field names  
fields = range(1,5)
    
# data rows of csv file
x = [[1,2,3,4,5,6],[7,8,9,0,0,0]]

rows = x
    
# name of csv file  
filename = "test.csv"
    
# writing to csv file  
with open(filename, 'w') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)  
                
    # writing the fields  
    csvwriter.writerow(fields)  
        
    # writing the data rows  
    csvwriter.writerows(rows)
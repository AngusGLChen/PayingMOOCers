'''
Created on Sep 17, 2015

@author: Angus
'''

import math

def ToAnalyzeUpWork(path):
    
    step = 5
    result = {}
    
    fp = open(path, "r")
    fp.readline()
    lines = fp.readlines()
    for line in lines:
        array = line.split(",")
        budget = float(array[2])
        index = budget / 5
        index = math.ceil(index)
        if index in result.keys():
            result[index] += 1
        else:
            result[index] = 1
        print str(budget) + "\t" + str(index)
    
    for element in result:
        print str(result[element])






####################################################
path = "/Users/Angus/Downloads/50$_upwork_excel_tasks_15_9_2015 - Sheet1.csv"
ToAnalyzeUpWork(path)
print "Finished."
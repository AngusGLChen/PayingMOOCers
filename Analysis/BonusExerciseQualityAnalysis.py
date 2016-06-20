'''
Created on Oct 6, 2015

@author: Angus
'''

import os
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import seaborn as sea

def BonusExerciseQualityAnalysis1(accuracy_path, quality_path):
    
    ##################################################################
    # Gather the accuracy results
    correctness_map = {}
    
    result_files = os.listdir(accuracy_path)
    for result_file in result_files:
        
        if "_unsorted" in result_file or ".DS_Store" in result_file:
            continue
        
        file_array = result_file.split("_")
        week = file_array[0].replace("week","")
        
        fp = open(accuracy_path + result_file, "r")
        lines = fp.readlines()
               
        
        for line in lines:
            line = line.replace("\n","")
            array = line.split("\t")
            id = array[0]
            result = array[1]
            
            if result == "True":
                if correctness_map.has_key(week):
                    correctness_map[week].add(id)
                else:
                    correctness_map[week] = set()
                    correctness_map[week].add(id)
        fp.close()
    
    print "The number of correct responses for each week..."
    for week in correctness_map.keys():
        print str(week) + "\t" + str(len(correctness_map[week]))
    print
    
    ##################################################################
    # Gather the quality results
    fp = open(quality_path + "smells.csv", "r")
    fp.readline()
    fp.readline()
    fp.readline()    
    lines = fp.readlines()
    
    # For testing
    element_set = set()
    
    quality_map = {}
    
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(",")
        
        week_array = array[1].split("\\")
        
        week = week_array[len(week_array) - 2]
        week = week[week.index("_")+1:len(week)]
        
        id = week_array[len(week_array) - 1]
        quality_type = array[len(array) - 2]
        risk_value = int(array[len(array) - 1])
              
        element_set.add(quality_type)
        
        if id not in correctness_map[week]:
            continue
        
        if quality_map.has_key(quality_type):
            if quality_map[quality_type].has_key(week):
                if quality_map[quality_type][week].has_key(id):
                    quality_map[quality_type][week][id] += risk_value
                else:
                    quality_map[quality_type][week][id] = risk_value
            else:
                quality_map[quality_type][week] = {}
                quality_map[quality_type][week][id] = risk_value
        else:
            quality_map[quality_type] = {}
            quality_map[quality_type][week] = {}
            quality_map[quality_type][week][id] = risk_value
            
    fp.close()
    
    '''
    for element in element_set:
        print element
    print
    '''

    ##################################################################
    '''
    # Analysis
    quality_type = "HiddenWorksheets"
    for week in quality_map[quality_type]:
        num_error = 0
        
        if week == "7":
            for id in quality_map[quality_type][week]:            
                if id in correctness_map[week]:
                    if quality_map[quality_type][week][id] > 1:
                        print id + "\t" + str(quality_map[quality_type][week][id])
                        num_error += 1
            print "The number of low-quality responses is: " + str(num_error)        
        
        
        print "For week " + str(week) + "..."
        for id in quality_map[quality_type][week]:            
            if id in correctness_map[week]:
                print id + "\t" + str(quality_map[quality_type][week][id])
                num_error += 1
        print "The number of low-quality responses is: " + str(num_error)
        
        
        print
    '''
    ##################################################################
    # Analysis
    
    perfect_response_map = {}
    for week in correctness_map.keys():
        perfect_response_map[week] = set()
        for id in correctness_map[week]:
            perfect_response_map[week].add(id)
    
    for quality_type in quality_map.keys():
        
        if quality_type == "FixedNumbers":            
            for week in quality_map[quality_type]:
                if week == "1":
                    for id in quality_map[quality_type][week]:
                        if quality_map[quality_type][week][id] > 3:
                            if id in perfect_response_map[week]:
                                perfect_response_map[week].remove(id)
                else:
                    if week == "4":
                        for id in quality_map[quality_type][week]:
                            if quality_map[quality_type][week][id] > 1:
                                if id in perfect_response_map[week]:
                                    perfect_response_map[week].remove(id)
                    else:
                        for id in quality_map[quality_type][week]:                        
                            if id in perfect_response_map[week]:
                                perfect_response_map[week].remove(id)
        else:
            if quality_type == "HiddenWorksheets":            
                for week in quality_map[quality_type]:
                    if week == "7":
                        for id in quality_map[quality_type][week]:
                            if quality_map[quality_type][week][id] > 1:
                                print "week7\t" + id
                                if id in perfect_response_map[week]:
                                    perfect_response_map[week].remove(id)
                    else:
                        for id in quality_map[quality_type][week]:                        
                            if id in perfect_response_map[week]:
                                perfect_response_map[week].remove(id)
            else:
                for week in quality_map[quality_type]:
                    for id in quality_map[quality_type][week]:                        
                        if id in perfect_response_map[week]:
                            if week == "7":
                                print "week7\t" + id
                            perfect_response_map[week].remove(id)
                        
    print "The number of perfect responses for each week..."
    for week in perfect_response_map.keys():
        print week + "\t" + str(len(perfect_response_map[week]))
    
    ##################################################################
    # Analysis
    '''
    max_code_smell_map = {}
    
    # Gather the quality results
    fp = open(quality_path + "smells.csv", "r")
    fp.readline()
    fp.readline()
    fp.readline()    
    lines = fp.readlines()
    
    quality_map = {}
    
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(",")
        
        week_array = array[1].split("\\")
        
        week = week_array[len(week_array) - 2]
        week = week[week.index("_")+1:len(week)]
        
        id = week_array[len(week_array) - 1]
        quality_type = array[len(array) - 2]
        risk_value = int(array[len(array) - 1])
        
        if id not in correctness_map[week]:
            continue
        
        if week not in max_code_smell_map.keys():
            max_code_smell_map[week] = {} 
        
        if id not in max_code_smell_map[week].keys():
            max_code_smell_map[week][id] = 0
        
        max_code_smell_map[week][id] += risk_value
        

    print           
    for week in max_code_smell_map.keys():
        if week == "7":
            print max_code_smell_map[week]
        max = -1
        max_id = ""
        for id in max_code_smell_map[week].keys():
            if max < max_code_smell_map[week][id]:
                max = max_code_smell_map[week][id]
                max_id = id
        #print week + "\t" + str(max) + "\t" + max_id
        print max
    '''    
    ##################################################################
    # Analysis
    
    average_code_smell_map = {}
    for week in ["1","2","3","4","5","7"]:
        average_code_smell_map[week] = {}
    
    for quality_type in quality_map.keys():
        
        if quality_type == "FixedNumbers":            
            for week in quality_map[quality_type]:
                if week == "1":
                    for id in quality_map[quality_type][week]:
                        if id in correctness_map[week]:
                            if quality_map[quality_type][week][id] > 3:
                                if not average_code_smell_map[week].has_key(id):
                                    average_code_smell_map[week][id] = 0
                                average_code_smell_map[week][id] += quality_map[quality_type][week][id] - 3                                
                else:
                    if week == "4":
                        for id in quality_map[quality_type][week]:
                            if id in correctness_map[week]:
                                if quality_map[quality_type][week][id] > 1:
                                    if not average_code_smell_map[week].has_key(id):
                                        average_code_smell_map[week][id] = 0
                                    average_code_smell_map[week][id] += quality_map[quality_type][week][id] - 1                                    
                    else:
                        for id in quality_map[quality_type][week]:
                            if id in correctness_map[week]:
                                if quality_map[quality_type][week][id] > 0:                  
                                    if not average_code_smell_map[week].has_key(id):
                                        average_code_smell_map[week][id] = 0
                                    average_code_smell_map[week][id] += quality_map[quality_type][week][id]                                    
        else:
            if quality_type == "HiddenWorksheets":            
                for week in quality_map[quality_type]:
                    if week == "7":
                        for id in quality_map[quality_type][week]:
                            if id in correctness_map[week]:
                                if quality_map[quality_type][week][id] > 1:                       
                                    if not average_code_smell_map[week].has_key(id):
                                        average_code_smell_map[week][id] = 0
                                    average_code_smell_map[week][id] += quality_map[quality_type][week][id] - 1                                    
                    else:
                        for id in quality_map[quality_type][week]:                        
                            if id in correctness_map[week]:
                                if quality_map[quality_type][week][id] > 0:                      
                                    if not average_code_smell_map[week].has_key(id):
                                        average_code_smell_map[week][id] = 0
                                    average_code_smell_map[week][id] += quality_map[quality_type][week][id]                                    
            else:
                for week in quality_map[quality_type]:
                    for id in quality_map[quality_type][week]:                        
                        if id in correctness_map[week]:                        
                            if not average_code_smell_map[week].has_key(id):
                                average_code_smell_map[week][id] = 0
                            average_code_smell_map[week][id] += quality_map[quality_type][week][id]
                            
    
    print ""           
    print "The averge number of code smells for each week..."

    # For boxplot
    
    plot_arrays = []
    for week in ["1","2","3","4","5"]:
        array = []
        for id in average_code_smell_map[week]:
            array.append(np.log10(average_code_smell_map[week][id]))

        plot_arrays.append(array)
        print week + "\t" + str(len(array))
    plt.boxplot(plot_arrays)
    
    '''
    # For error bar
    plot_array = []
    for week in ["1","2","3","4","5"]:
        
        sorted_array = sorted(average_code_smell_map[week].items(), key=lambda d:d[1])
        length = len(sorted_array)
        lower_bound = int(round(length/2 - 1.96 * numpy.sqrt(length)/2))
        upper_bound = int(round(1 + length/2 + 1.96 * numpy.sqrt(length)/2))
        
        sum = 0
        for i in range(lower_bound, upper_bound + 1):
            sum += sorted_array[i][1]
        sum = round(sum / float(upper_bound - lower_bound + 1),2)
        plot_array.append(sum)
        print week + "\t" + str(upper_bound - lower_bound + 1) + "\t" + str(length) + "\t" + str(sum)
    '''
    #plt.plot(plot_array)
        
        
    #plt.show()
    
    
                
            
            
    
  
  
  
  
  
  
  
  
  
  
    
    


####################################################

def BonusExerciseQualityAnalysis2(accuracy_path, quality_path):
    
    ##################################################################
    # Gather accuracy results
    quality_analysis_map = {}
    
    
    result_files = os.listdir(accuracy_path)
    for result_file in result_files:
        
        if "_unused" in result_file or ".DS_Store" in result_file:
            continue
        
        file_array = result_file.split("_")
        week = file_array[0].replace("week","")
        
        fp = open(accuracy_path + result_file, "r")
        lines = fp.readlines()
        
        for line in lines:
            line = line.replace("\n","")
            array = line.split("\t")
            id = array[0]
            result = array[1]
            
            if not quality_analysis_map.has_key(week):
                quality_analysis_map[week] = {}
            
            if not quality_analysis_map[week].has_key(result):
                quality_analysis_map[week][result] = {}
                
            quality_analysis_map[week][result][id] = 0
        fp.close()
    
    ##################################################################
    # Gather quality results
    fp = open(quality_path + "smells.csv", "r")
    fp.readline()
    fp.readline()
    fp.readline()    
    lines = fp.readlines()
    
    quality_map = {}
    
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(",")
        
        week_array = array[1].split("\\")
        
        week = week_array[len(week_array) - 2]
        week = week[week.index("_")+1:len(week)]
        
        id = week_array[len(week_array) - 1]
        quality_type = array[len(array) - 2]
        risk_value = int(array[len(array) - 1])
        
        if quality_map.has_key(quality_type):
            if quality_map[quality_type].has_key(week):
                if quality_map[quality_type][week].has_key(id):
                    quality_map[quality_type][week][id] += risk_value
                else:
                    quality_map[quality_type][week][id] = risk_value
            else:
                quality_map[quality_type][week] = {}
                quality_map[quality_type][week][id] = risk_value
        else:
            quality_map[quality_type] = {}
            quality_map[quality_type][week] = {}
            quality_map[quality_type][week][id] = risk_value
            
    fp.close()
    
    ##################################################################
    # Analysis
    for quality_type in quality_map.keys():
        
        if quality_type == "FixedNumbers":            
            for week in quality_map[quality_type]:
                if week == "1":
                    for id in quality_map[quality_type][week]:
                        if quality_map[quality_type][week][id] <= 3:
                            quality_map[quality_type][week][id] = 0
                        else:
                            quality_map[quality_type][week][id] -= 3
                            
                else:
                    if week == "4":
                        for id in quality_map[quality_type][week]:
                            if quality_map[quality_type][week][id] <= 1:
                                quality_map[quality_type][week][id] = 0
                            else:
                                quality_map[quality_type][week][id] -= 1
        else:
            if quality_type == "HiddenWorksheets":            
                for week in quality_map[quality_type]:
                    if week == "7":
                        for id in quality_map[quality_type][week]:
                            if quality_map[quality_type][week][id] <= 1:
                                quality_map[quality_type][week][id] = 0
                            else:
                                quality_map[quality_type][week][id] -= 1
    
    ##################################################################
    # Analysis
    
    for quality_type in quality_map.keys():
        for week in quality_map[quality_type]:
            for id in quality_map[quality_type][week]:
                if id in quality_analysis_map[week]["True"]:
                    quality_analysis_map[week]["True"][id] += quality_map[quality_type][week][id]
                else:
                    if id in quality_analysis_map[week]["False"]:
                        quality_analysis_map[week]["False"][id] += quality_map[quality_type][week][id]
                    # else:
                        # print "Error"
                        
    # For boxplot
    
    plot_arrays = []
    plot_data = {}
    # for week in ["1","2","3", "4", "5", "7"]:
    for week in ["7"]:
        for type in ["True", "False"]:
            array = []
            for id in quality_analysis_map[week][type]:
                
                if quality_analysis_map[week][type][id] > 0:
                    array.append(quality_analysis_map[week][type][id])
                 
            # 2rd version - 95% - boxplot
            '''
            array.sort()
            length = len(array)
            lower_bound = int(round(length/2 - 1.96 * numpy.sqrt(length)/2))
            upper_bound = int(round(1 + length/2 + 1.96 * numpy.sqrt(length)/2))
            final_array = []
            for i in range(lower_bound, upper_bound + 1):
                final_array.append(array[i])
            '''
            
            # 1st version - 100% - boxplot
            plot_arrays.append(array)
            print str(week) + "\t" + type + "\t" + str(len(array)) + "\t" + str(np.median(array))
            plot_data[week + "-" + type] = array
            # 2rd version - 95% - boxplot    
            # plot_arrays.append(final_array)
            
            # print week + "\t" + type + "\t" + str(len(final_array))
    
    # 1st version - 100% - boxplot
    # pylab.boxplot(plot_arrays)
    # pylab.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], ["W1-C", "W1-W", "W2-C", "W2-W", "W3-C", "W3-W", "W4-C", "W4-W", "W5-C", "W5-W", "W7-C", "W7-W"])
    
    data = pd.DataFrame({k : pd.Series(v) for k, v in plot_data.iteritems()})
    
    ax = sea.violinplot(data=data)
    ax.set(yscale="log")

    

        
    
    
    
    
    '''
    # For error bar
    for type in ["True", "False"]:
        plot_x = []
        plot_y = []
        for week in ["1","2","3","4","5", "7"]:
            array = []
            for id in quality_analysis_map[week][type]:
                
                #if quality_analysis_map[week][type][id] > 0:
                array.append(quality_analysis_map[week][type][id])
            
            # 2rd version - 95% - boxplot
            array.sort()
            length = len(array)
            lower_bound = int(round(length/2 - 1.96 * numpy.sqrt(length)/2))
            upper_bound = int(round(1 + length/2 + 1.96 * numpy.sqrt(length)/2))
            final_array = []
            for i in range(lower_bound, upper_bound + 1):
                final_array.append(array[i])
            
            # 1st version - 100% - error bar
        
            sum = 0
            for value in array:
                sum += value
            sum /= float(len(array))
            
            
            # 2rd version - 95% - error bar
            sum = 0
            for value in final_array:
                sum += value
            sum /= float(len(array))
            
            plot_x.append(week)
            plot_y.append(sum)
            
            print week + "\t" + type + "\t" + str(len(array)) + "\t" + str(round(numpy.log(sum), 2))
        
        if type == "True":
            plt.plot(plot_x, plot_y, color='b', marker='o', label='Correct')
        if type == "False":
            plt.plot(plot_x, plot_y, color='g', marker='o', label='Incorrect')
    plt.legend(loc='upper left')
    '''
    
    
     
    plt.show()
    
    
                
            
            
    
  
  
  
  
  
  
  
  
  
  
    
    


####################################################
accuracy_path = "/Users/Angus/Data/EdX/EX101x/Bonus/Bonus Exercise/Checking_results/"
quality_path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
BonusExerciseQualityAnalysis2(accuracy_path, quality_path)
print "Finished."
























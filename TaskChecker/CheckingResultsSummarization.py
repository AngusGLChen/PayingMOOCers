'''
Created on Oct 1, 2015

@author: Angus
'''

import os

def AnalyzeCheckingResults(path):
    
    correctness_map = {}
    
    result_files = os.listdir(path + "Checking_results/")
    for result_file in result_files:
        
        if "_unsorted" in result_file or ".DS_Store" in result_file:
            continue
        
        file_array = result_file.split("_")
        week = file_array[0].replace("week","")
        
        fp = open(path + "Checking_results/" + result_file, "r")
        lines = fp.readlines()
        
        num_correct = 0        
        
        for line in lines:
            line = line.replace("\n","")
            array = line.split("\t")
            response_id = array[0]
            result = array[1]
            
            if result == "True":
                num_correct += 1
                
        correctness_map[week] = num_correct
        fp.close()
        
    all_response_map = {}
    
    all_response_folder = os.listdir(path + "Response/")
    for response_folder in all_response_folder:
        folder_array = response_folder.split("_")
        week = folder_array[1]
        num_files = 0
        
        folder_path = path + "Response/" + response_folder + "/"
        if os.path.isdir(folder_path):
            all_response_files = os.listdir(folder_path)
            for file in all_response_files:
                if file != ".DS_Store" and "~$" not in file:
                    num_files += 1
                
                    
            all_response_map[week] = num_files
        
    for week in all_response_map:
        print week + "\t" + str(all_response_map[week]) + "\t" + str(correctness_map[week]) +"\t" + str(round(float(correctness_map[week])/all_response_map[week]*100, 2))
        print 
   





####################################################
path = "/Users/Angus/Data/EdX/EX101x/Bonus/Bonus Exercise/"
AnalyzeCheckingResults(path)
print "Finished."













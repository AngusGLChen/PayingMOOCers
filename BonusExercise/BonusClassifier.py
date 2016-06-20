'''
Created on Jun 21, 2015

@author: Angus
'''

import os
import shutil
import re

def BonusPreprocess(path):
    
    if not os.path.isdir(path):
        return False
    
    week_array = [1,2,3,4,5,7]
    file_type_array = ["xls","xlsx","xlsm","xlsb", "csv"]
    
    all_path = path + "All/"    
    if os.path.isdir(all_path):
        shutil.rmtree(all_path)    
    os.mkdir(all_path)
    
    selected_path = path + "Selected/"    
    if os.path.isdir(selected_path):
        shutil.rmtree(selected_path)    
    os.mkdir(selected_path)
    
    # Copy from functional mailbox to All folder
    functional_path = path + "Functional Mailbox/"
    functional_files = os.listdir(functional_path)
    print "Functional files number is: " + str(len(functional_files))
    for file in functional_files:
        file_type = str.lower(file.split(".")[len(file.split("."))-1])        
        full_file_name = os.path.join(functional_path, file)        
        if (os.path.isfile(full_file_name)) and file_type in file_type_array:
            shutil.copy(full_file_name, all_path)
            
    # Copy from gmail mailbox to All folder
    gmail_path = path + "Gmail/"
    gmail_files = os.listdir(gmail_path)
    print "Gmail files number is: " + str(len(gmail_files))
    for file in gmail_files:
        file_type = str.lower(file.split(".")[len(file.split("."))-1])
        full_file_name = os.path.join(gmail_path, file)        
        if os.path.isfile(full_file_name) and file_type in file_type_array:
            shutil.copy(full_file_name, all_path)
        
    files = os.listdir(all_path)
    
    for week in week_array:   
                
        tags = []
        tags.append("week_" + str(week))
        tags.append("week" + str(week))
        tags.append("week " + str(week))
        tags.append("wk_" + str(week))
        tags.append("wk" + str(week))
        tags.append("wk " + str(week))
        
        for file in files:            
            
            file_name = str.lower(file[file.index(")_")+2:len(file)])
            file_type = str.lower(file.split(".")[len(file.split("."))-1])
            
            for tag in tags:
                if tag in file_name:
                    if not os.path.isfile(all_path + file):
                        print file
                    
                    if os.path.isfile(all_path + file) and file_type in file_type_array:                 
                        os.rename(all_path + file, selected_path + file)                        
            
            if os.path.isfile(all_path + file) and week==1 and ("1.7" in file or "1-7" in file or "17" in file or "1_7" in file):
                os.rename(all_path + file, selected_path + file)
                
            if os.path.isfile(all_path + file) and week==2 and "2.9" in file:
                os.rename(all_path + file, selected_path + file)
                
            if os.path.isfile(all_path + file) and week==3 and "3.9" in file:
                os.rename(all_path + file, selected_path + file)
                
            if os.path.isfile(all_path + file) and week==4 and "4.8" in file:
                os.rename(all_path + file, selected_path + file)
                
            if os.path.isfile(all_path + file) and week==5 and "5.5" in file:
                os.rename(all_path + file, selected_path + file)
                
            if os.path.isfile(all_path + file) and week==7 and "7.6" in file:
                os.rename(all_path + file, selected_path + file)

def BonusClassifier(path):
    
    week_array = [1,2,3,4,5,7]
    all_path = path + "All/"
    selected_path = path + "Selected/"
    
    # To record the email, week, file_count
    email_record_path = path + "bonus_email_map.txt"
    if os.path.isfile(email_record_path):
        os.remove(email_record_path)
    email_record_file = open(email_record_path, 'wb')
    
    all_files = os.listdir(all_path)
    for file in all_files:
        shutil.copy(all_path + file, selected_path + file)
        
    selected_files = os.listdir(selected_path)
    all_count = 0       
    
    for week in week_array:   
                
        tags = []
        tags.append("week_" + str(week))
        tags.append("week" + str(week))
        tags.append("week " + str(week))
        tags.append("wk_" + str(week))
        tags.append("wk" + str(week))
        tags.append("wk " + str(week))
        
        week_path = path + "/Response/Week_" + str(week) + "/"
        if os.path.isdir(week_path):
            shutil.rmtree(week_path)            
        os.mkdir(week_path) 
        
        file_count = 0        
        
        for file in selected_files:
            
            remark = False
            
            if ")_" in file:
                
                file_name = str.lower(file[file.index(")_")+2:len(file)])
                file_type = str.lower(file.split(".")[len(file.split("."))-1])
            
                email = str.lower(file[0:file.index(")_")-1])
                while "(" in email:
                    email = email[email.index("(")+1:len(email)]                                   
            
                for tag in tags:
                    if tag in file_name:                    
                        if os.path.isfile(selected_path + file):
                            shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)                                       
                            email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                            file_count += 1
                            remark = True
                            break
                        
                if not remark:        
                    if os.path.isfile(selected_path + file) and week==1 and ("1.7" in file or "1-7" in file or "17" in file or "1_7" in file):
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
                    if os.path.isfile(selected_path + file) and week==2 and "2.9" in file:
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
                    if os.path.isfile(selected_path + file) and week==3 and "3.9" in file:
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
                    if os.path.isfile(selected_path + file) and week==4 and "4.8" in file:
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
                    if os.path.isfile(selected_path + file) and week==5 and "5.5" in file:
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
                    if os.path.isfile(selected_path + file) and week==7 and "7.6" in file:
                        shutil.copy(selected_path + file, week_path + str(file_count) + "." + file_type)
                        email_record_file.write(email + "," + str(week) + "," + str(file_count) + "\n")
                        file_count += 1
                        continue
                
        print "Week " + str(week) + ": " + str(file_count)
        all_count += file_count
                
    email_record_file.close()
    print "All files number is: " + str(all_count)



path = "/Users/Angus/Data/EdX/EX101x/Bonus/"
# BonusPreprocess(path)
BonusClassifier(path)
print "Finished."




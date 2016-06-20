'''
Created on Jul 24, 2015

@author: Angus
'''

import os
import json
import time,datetime
from sets import Set
  
def cmp_datetime(a_datetime, b_datetime):    
    a_datetime = a_datetime.replace("T", " ")
    a_datetime = a_datetime.replace("Z", "")
    b_datetime = b_datetime.replace("T", " ")
    b_datetime = b_datetime.replace("Z", "")
    
    format="%Y-%m-%d %H:%M:%S";
    a_time = datetime.datetime.strptime(a_datetime,format)
    b_time = datetime.datetime.strptime(b_datetime,format)
    
    if a_time < b_time:
        return False
    elif a_time >= b_time:
        return True 
       
    
def user_mode(path):
    
    files = os.listdir(path)
    
    # 1. course table
    course_id = ""
    course_name = ""
    course_start_time = ""
    course_end_time = ""
    
    # 2. user_pii table
    user_mail_map = {}
    
    # 3. course_user table
    course_user_map = {}
    
    # Enrolled learners set
    enrolledLearner_set = Set()
    
    # Processing course_structure data                
    for file in files:             
        if "course_structure" in file:           
            fp = open(path + file, "r")     
            lines = fp.readlines()
            jsonLine = ""   
            for line in lines:                
                line = line.replace("\n", "")
                jsonLine += line
            
            # To extract course_id     
            course_id_array = file.split("-")
            course_id = course_id_array[0] + "/" + course_id_array[1] + "/" + course_id_array[2]

            jsonObject = json.loads(jsonLine)
            for record in jsonObject:
                if jsonObject[record]["category"] == "course":                    
                    course_name = jsonObject[record]["metadata"]["display_name"]
                    course_start_time = jsonObject[record]["metadata"]["start"]
                    course_end_time = jsonObject[record]["metadata"]["end"]                    
             
            # Output course table
            course_table_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "courses.csv"            
            if os.path.isfile(course_table_path):
                os.remove(course_table_path)
            
            course_table_file = open(course_table_path, 'wb')
            course_table_file.write(course_id + "," + course_name + "," + course_start_time + "," + course_end_time + "\n")
            course_table_file.close()
    
    # Processing student_courseenrollment data  
    for file in files:       
        if "student_courseenrollment" in file:
            fp = open(path + file, "r")
            fp.readline()
            lines = fp.readlines()
            
            # Output global_user table
            global_user_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "global_user.csv"
            if os.path.isfile(global_user_path):
                os.remove(global_user_path)            
            
            global_user_file = open(global_user_path, 'wb')
                        
            for line in lines:
                record = line.split("\t")
                global_user_id = record[1]
                course_id = record[2]
                time = record[3]
                course_user_id = course_id + "_" + global_user_id
                    
                if cmp_datetime(course_end_time, time):           
                    enrolledLearner_set.add(global_user_id)
                           
                    # Both of the "active" and "inactive" learners will be recorded    
                    global_user_file.write(global_user_id + "," + course_id + "," + course_user_id + "\n")
                    course_user_map[global_user_id] = course_user_id    
            
            global_user_file.close()
        
            print "The number of enrolled learners is: " + str(len(enrolledLearner_set)) + "\n"
  
    # Processing auth_user data  
    for file in files:               
        if "auth_user-" in file:
            fp = open(path + file, "r")
            fp.readline()
            lines = fp.readlines()
                        
            for line in lines:
                record = line.split("\t")
                if record[0] in enrolledLearner_set:
                    user_mail_map[record[0]] = record[4]
                    
    # Processing certificates_generatedcertificate data
    num_uncertifiedLearners = 0
    num_certifiedLearners = 0    
    for file in files:       
        if "certificates_generatedcertificate" in file:
            fp = open(path + file, "r")
            fp.readline()
            lines = fp.readlines()
            
            # Output course_user table
            course_user_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "course_user.csv"
            if os.path.isfile(course_user_path):
                os.remove(course_user_path)
                            
            course_user_file = open(course_user_path, 'wb')
                        
            for line in lines:
                record = line.split("\t")
                global_user_id = record[1]
                final_grade = record[3]
                enrollment_mode = record[14].replace("\n", "")
                certificate_status = record[7]                         
                
                if course_user_map.has_key(global_user_id):
                    num_certifiedLearners += 1
                    course_user_file.write(course_user_map[global_user_id] + "," + final_grade + "," + enrollment_mode + "," + certificate_status + "\n")
                else:
                    num_uncertifiedLearners += 1
                    
            course_user_file.close()

            print "The number of uncertified learners is: " + str(num_uncertifiedLearners)
            print "The number of certified learners is: " + str(num_certifiedLearners) + "\n"    
    
    # Processing auth_userprofile data
    num_user_pii = 0                    
    for file in files:       
        if "auth_userprofile" in file:
            fp = open(path + file, "r")
            fp.readline()
            lines = fp.readlines()
            
            # Output user_pii table
            user_pii_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "user_pii.csv"
            if os.path.isfile(user_pii_path):
                os.remove(user_pii_path)            
            
            user_pii_file = open(user_pii_path, 'wb')
                        
            for line in lines:
                record = line.split("\t")
                global_user_id = record[1]
                gender = record[7]
                year_of_birth = record[9]
                level_of_education = record[10]
                country = record[13]
                                
                if global_user_id in enrolledLearner_set:
                    num_user_pii += 1
                    user_pii_file.write(global_user_id + "," + gender + "," + year_of_birth + "," + level_of_education + "," + country + "," + user_mail_map[global_user_id] + "\n")            
            
            user_pii_file.close()

            print "The number of records in the user_pii file is: " + str(len(lines))
            print "The number of selected user_pii records is: " + str(num_user_pii) + "\n"
 
    print "User mode finished."


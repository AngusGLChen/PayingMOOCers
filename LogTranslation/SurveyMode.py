'''
Created on Jul 27, 2015

@author: Angus
'''

import os,re
from sets import Set

def survey_mode(path):
      
    files = os.listdir(path)
    
    course_id = ""
    id_map = {}
    
    response_id_set = set()
        
    # Output survey_description table
    survey_description_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "survey_description.sql"            
    if os.path.isfile(survey_description_path):
        os.remove(survey_description_path)            
    survey_description_file = open(survey_description_path, 'wb')
    
    survey_description_file.write("\r\n" + "USE EX101x;" + "\r\n")
    survey_description_file.write("\r\n" + "DROP TABLE IF EXISTS survey_description; CREATE TABLE survey_description (question_id varchar(255) NOT NULL, course_id varchar(255), question_type varchar(255), description text, PRIMARY KEY (question_id), FOREIGN KEY (course_id) REFERENCES courses(course_id)) ENGINE=MyISAM;" + "\r\n")  
    
    # Output survey_response table
    survey_response_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "survey_response.sql"            
    if os.path.isfile(survey_response_path):
        os.remove(survey_response_path)            
    survey_response_file = open(survey_response_path, 'wb')
    
    survey_response_file.write("\r\n" + "USE EX101x;" + "\r\n")
    survey_response_file.write("\r\n" + "DROP TABLE IF EXISTS survey_response; CREATE TABLE survey_response (response_id varchar(255) NOT NULL, course_user_id varchar(255), question_id varchar(255), answer text, PRIMARY KEY (response_id), FOREIGN KEY (course_user_id) REFERENCES global_user(course_user_id)) ENGINE=MyISAM;" + "\r\n")

    # Processing course_structure data   
    for file in files:        
        if "course_structure" in file:                      
            # To extract course_id     
            course_id_array = file.split("-")
            course_id = course_id_array[0] + "/" + course_id_array[1] + "/" + course_id_array[2]
    
    # Processing ID information
    for file in files:        
        if "2015T1_EX101x" in file:
            sub_path = path + file + "/"
            sub_files = os.listdir(sub_path)
            for sub_file in sub_files:               
                if "edX_user_id" in sub_file:
                    id_path = sub_path + sub_file + "/"
                    id_files = os.listdir(id_path)
                    for id_file in id_files:
                        if "DelftX-EX101x-1T2015-anon-ids.csv" in id_file:
                            fp = open(id_path + id_file, "r")
                            fp.readline()
                            lines = fp.readlines()
                            for line in lines:
                                array = line.split(",")
                                global_id = array[0].replace("\"","")
                                anonymized_id = array[1].replace("\"","")
                                id_map[anonymized_id] = global_id         
    
    # Processing Pre-survey information         
    for file in files:        
        if "2015T1_EX101x" in file:
            sub_path = path + file + "/"
            sub_files = os.listdir(sub_path)
            for sub_file in sub_files:    
                if "Pre" in sub_file:
                    pre_path = sub_path + sub_file + "/Thieme_data_recovery/"
                    pre_files = os.listdir(pre_path)
                    for pre_file in pre_files:
                        if "survey_updated" in pre_file:
                            print "Processing Pre-survey..."
                            fp = open(pre_path + pre_file, "r")
                            
                            # To process question_id line
                            question_id_line = fp.readline()
                            question_id_array = question_id_line.split(",")
                            
                            print "The number of question ids is: " + str(len(question_id_array))
                            
                            # To process question description line
                            question_line = fp.readline()                            
                            question_line = question_line.replace("\",NA,\"","\",\"NA\",\"")
                            question_array = question_line.split("\",\"")
                            
                            print "The number of questions is: " + str(len(question_array))
                            
                            #print question_id_array[211]
                            #print question_array[211]                   
                            
                            for i in range(22,211):
                                question_id = course_id + "_pre_" + question_id_array[i].replace("\"","")
                                question_array[i] = question_array[i].replace("\'", "\\'")
                                write_string = "\r\n" + "insert into survey_description (question_id, course_id, question_type, description) values"
                                write_string += "('%s','%s','%s','%s');\r\n" % (question_id, course_id, "pre", question_array[i])                               
                                survey_description_file.write(write_string)
                            
                            response_lines = fp.readlines()
                            num_multipleID = 0
                            for response_line in response_lines:
                                response_line = response_line.replace("\",NA,\"","\",\"NA\",\"")
                                
                                subRegex = re.compile("\(([^\(\)]*)\)")
                                matches = subRegex.findall(response_line)
                                if not len(matches) == 0:
                                    for match in matches:
                                        response_line = response_line.replace(match, "")
                                        
                                response_array = response_line.split("\",\"")
                                duplicate_mark = response_array[218].replace("\"","").replace("\n","")
                                
                                if response_array[217] in id_map.keys() and duplicate_mark == "no":                                    
                                    course_user_id = course_id + "_" + id_map[response_array[217]]
                                    for i in range(22,211):
                                        question_id = course_id + "_" + "pre" + "_" + question_id_array[i].replace("\"","")
                                        response_id = course_user_id + "_" + "pre" + "_" + question_id_array[i].replace("\"","")
                                        
                                        if response_id not in response_id_set:                                        
                                            response_array[i] = response_array[i].replace("\'", "\\'")
                                            write_string = "\r\n" + "insert into survey_response (response_id, course_user_id, question_id, answer) values"
                                            write_string += "('%s','%s','%s','%s');\r\n" % (response_id, course_user_id, question_id, response_array[i])                               
                                            survey_response_file.write(write_string)
                                            
                                            response_id_set.add(response_id)
                                        # else:
                                        #    print response_id + "\t" + response_array[103] + "\t" + question_array[i]
                                else:
                                    num_multipleID += 1
                                    # print response_line
                            
                            print "Pre - The number of response is: " + str(len(response_lines))
                            print "Pre - The number of response with multiple/empty IDs is: " + str(num_multipleID)
                            print ""
                            
    
    # Processing Post-survey information 
    for file in files:        
        if "2015T1_EX101x" in file:
            sub_path = path + file + "/"
            sub_files = os.listdir(sub_path)
            for sub_file in sub_files:
                if "Post" in sub_file:
                    post_path = sub_path + sub_file + "/"
                    post_files = os.listdir(post_path)
                    for post_file in post_files:
                        if "20150526_EX101x_Post.csv" in post_file:
                            fp = open(post_path + post_file, "r")
                            
                            # To process question_id line
                            question_id_line = fp.readline()
                            question_id_array = question_id_line.split(",")
                            print "The number of question ids is: " + str(len(question_id_array))
                                                             
                            # To process question description line
                            question_line = fp.readline()                            
                            
                            # question_line = question_line.replace("\",NA,\"","\",\"NA\",\"")
                            # question_array = question_line.split("\",\"")
                            
                            question_array = question_line.split(",")
                            print "The number of questions is: " + str(len(question_array))
                            
                            #print question_id_array[131]
                            #print question_array[10]  
                            
                            for i in range(26,131):
                                question_id = course_id + "_post_" + question_id_array[i].replace("\"","")
                                # print question_id
                                question_array[i] = question_array[i].replace("\'", "\\'")
                                write_string = "\r\n" + "insert into survey_description (question_id, course_id, question_type, description) values"
                                write_string += "('%s','%s','%s','%s');\r\n" % (question_id, course_id, "post", question_array[i])                               
                                survey_description_file.write(write_string)
                            
                            response_lines = fp.readlines()
                            num_multipleID = 0
                            for response_line in response_lines:
                                
                                original_line = response_line
                                
                                subRegex = re.compile("\"[^\"]*\"")
                                matches = subRegex.findall(response_line)
                                if not len(matches) == 0:
                                    for match in matches:                                        
                                        response_line = response_line.replace(match, "")
       
                                response_array = response_line.split(",")
                                
                                # print response_array[10]
                                
                                if response_array[10] in id_map.keys():                                    
                                    course_user_id = course_id + "_" + id_map[response_array[10]]
                                    for i in range(26,131):
                                        question_id = course_id + "_post_" + question_id_array[i].replace("\"","")                                        
                                        response_id = course_user_id + "_post_" + question_id_array[i].replace("\"","")                                
                                        
                                        if response_id not in response_id_set:
                                            response_array[i] = response_array[i].replace("\'", "\\'")
                                            write_string = "\r\n" + "insert into survey_response (response_id, course_user_id, question_id, answer) values"
                                            write_string += "('%s','%s','%s','%s');\r\n" % (response_id, course_user_id, question_id, response_array[i])                               
                                            survey_response_file.write(write_string)
                                            
                                            response_id_set.add(response_id)                                            
                                        # else:
                                        #    print response_id + "\t" + response_array[118] + "\t" + question_array[i]                           
                                    
                                else:
                                    num_multipleID += 1                                
                            
                            print "Post - The number of response is: " + str(len(response_lines))
                            print "Post - The number of response with multiple/empty IDs is: " + str(num_multipleID)
          
    survey_description_file.close()
    survey_response_file.close()
    
            

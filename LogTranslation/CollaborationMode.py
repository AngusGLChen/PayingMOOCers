'''
Created on Jul 24, 2015

@author: Angus
'''

import os
import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time,datetime
from time import *

def collaboration_mode(path):
    
    files = os.listdir(path)

    # Output collaborations SQL file
    collaborations_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "collaborations.sql"
    if os.path.isfile(collaborations_path):
        os.remove(collaborations_path)
        
    collaborations_file = open(collaborations_path, 'wb')
    
    collaborations_file.write("\r\n" + "USE EX101x;" + "\r\n")
    collaborations_file.write("\r\n" + "DROP TABLE IF EXISTS collaborations; CREATE TABLE collaborations (collaboration_id varchar(255) NOT NULL, course_user_id varchar(255), collaboration_type varchar(255), collaboration_title text, collaboration_content text, collaboration_timestamp datetime, collaboration_parent_id varchar(255), collaboration_thread_id varchar(255), PRIMARY KEY (collaboration_id), FOREIGN KEY (course_user_id) REFERENCES global_user(course_user_id)) ENGINE=MyISAM;" + "\r\n")

    # Course information
    course_end_time = ""
    
    # Processing course_structure data                
    for file in files:             
        if "course_structure" in file:           
            fp = open(path + file, "r")            
            lines = fp.readlines()
            jsonLine = ""   
            for line in lines:
                line = line.replace("\n", "")
                jsonLine += line

            jsonObject = json.loads(jsonLine)
            for record in jsonObject:
                if jsonObject[record]["category"] == "course":
                    course_end_time = jsonObject[record]["metadata"]["end"]
                    
                    format="%Y-%m-%d %H:%M:%S"
                       
                    course_end_time = course_end_time[0:19]
                    course_end_time = course_end_time.replace("T", " ")                    
                    course_end_time = datetime.datetime.strptime(course_end_time,format)
    
    # Processing forum data      
    for file in files:
        if ".mongo" in file:
            fp = open(path + file,"r")   
            for line in fp:
                jsonObject = json.loads(line)
                   
                collaboration_id = jsonObject["_id"]["$oid"]                
                course_user_id = jsonObject["course_id"] + "_" + jsonObject["author_id"]                

                collaboration_type = jsonObject["_type"]
                if collaboration_type == "CommentThread":
                    collaboration_type += "_" + jsonObject["thread_type"]                
                if "parent_id" in jsonObject:
                    if jsonObject["parent_id"] != "":
                        collaboration_type = "Comment_Reply"
                
                collaboration_title = ""
                if "title" in jsonObject:
                    collaboration_title=jsonObject["title"]
                
                collaboration_content = jsonObject["body"]
                
                collaboration_timestamp = jsonObject["created_at"]["$date"]
                collaboration_timestamp = strftime("%Y-%m-%d %H:%M:%S",gmtime(collaboration_timestamp/1000))
                collaboration_timestamp = datetime.datetime.strptime(collaboration_timestamp,"%Y-%m-%d %H:%M:%S")
                
                collaboration_parent_id = ""
                if "parent_id" in jsonObject:
                    collaboration_parent_id = jsonObject["parent_id"]["$oid"]
                
                collaboration_thread_id = ""    
                if "comment_thread_id" in jsonObject:
                    collaboration_thread_id = jsonObject["comment_thread_id"]["$oid"]                
                
                collaboration_title = collaboration_title.replace("\n", " ")
                collaboration_title = collaboration_title.replace("\\", "\\\\")
                collaboration_title = collaboration_title.replace("\'", "\\'")
                
                collaboration_content = collaboration_content.replace("\n", " ")
                collaboration_content = collaboration_content.replace("\\", "\\\\")
                collaboration_content = collaboration_content.replace("\'", "\\'")
                
                if collaboration_timestamp < course_end_time:           
                    write_string = "\r\n" + "insert into collaborations(collaboration_id, course_user_id, collaboration_type, collaboration_title, collaboration_content, collaboration_timestamp, collaboration_parent_id, collaboration_thread_id) values"
                    write_string += "('%s','%s','%s','%s','%s','%s','%s', '%s');\r\n" % (collaboration_id, course_user_id, collaboration_type, collaboration_title, collaboration_content, collaboration_timestamp, collaboration_parent_id, collaboration_thread_id)  
                    collaborations_file.write(write_string)                                
                
            fp.close()
            
    # Close collaborations_file   
    collaborations_file.close()
       
    print "Collaboration mode finished."






        


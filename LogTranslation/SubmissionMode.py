'''
Created on Jul 24, 2015

@author: Angus
'''

import os
import json
import re

from sets import Set
import datetime

def getNextDay(current_day_string):
    format="%Y-%m-%d";
    current_day = datetime.datetime.strptime(current_day_string,format)
    oneday = datetime.timedelta(days=1)
    next_day = current_day + oneday   
    return str(next_day)[0:10]

def submission_mode(path):

    files = os.listdir(path)
    
    # Processing course_structure data               
    for file in files:   
        if "course_structure" in file:                       
            fp = open(path + file,"r")            
            lines = fp.readlines()
            jsonLine = ""   
            for line in lines:
                line = line.replace("\n","")
                jsonLine += line
                
            # Problem collection
            problem_collection = []

            children_parent_map = {}            
            block_type_map = {}
            
            # Output problems table
            problems_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "problems.csv"
            if os.path.isfile(problems_path):
                os.remove(problems_path)
            
            problems_file = open(problems_path, 'wb')         
                        
            jsonObject = json.loads(jsonLine)
            for record in jsonObject:
                if jsonObject[record]["category"] == "course":
                    # To obtain the course_start time
                    course_start_date = jsonObject[record]["metadata"]["start"]
                    course_start_date = course_start_date[0:course_start_date.index("T")]
                    # To obtain the course_end time
                    course_end_date = jsonObject[record]["metadata"]["end"]
                    course_end_date = course_end_date[0:course_end_date.index("T")]
                else:
                    resourse_id = record
                                        
                    # Record all the problems id
                    if jsonObject[resourse_id]["category"] == "problem":
                        problem_collection.append(resourse_id)   
                    
                    # Children to parent relation                    
                    for child in jsonObject[resourse_id]["children"]:
                        children_parent_map[child] = resourse_id                                                 
                    
                    # Types of blocks to which problems belong
                    if jsonObject[resourse_id]["category"] == "sequential":
                        if "display_name" in jsonObject[resourse_id]["metadata"]:
                            block_type = jsonObject[resourse_id]["metadata"]["display_name"]
                            block_type_map[resourse_id] = block_type                                      
                        
            # To locate problem_type for each problem
            for problem in problem_collection:                
                
                problem_parent = children_parent_map[problem]                
                while not block_type_map.has_key(problem_parent):
                    problem_parent = children_parent_map[problem_parent]
                    
                problem_type = block_type_map[problem_parent]
                problems_file.write(problem + "," + problem_type + "\n")
                
            problems_file.close()
    
    # Processing events data
    
    submission_event_collection = []
    submission_event_collection.append("problem_check")
    submission_event_collection.append("problem_check_fail")
    submission_event_collection.append("problem_reset") # event_source: browser
    submission_event_collection.append("problem_rescore")
    submission_event_collection.append("problem_rescore_fail")
    submission_event_collection.append("problem_save") # event_source: browser
    submission_event_collection.append("show_answer")
    submission_event_collection.append("save_problem_fail")
    submission_event_collection.append("save_problem_success")
    submission_event_collection.append("problem_graded")

    submission_id_set = Set()
    assessments = {}
    
    current_date = course_start_date
    course_end_date = getNextDay(course_end_date)
    
    # Output submissions table
    submissions_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "submissions.csv"
    if os.path.isfile(submissions_path):
        os.remove(submissions_path)
            
    submissions_file = open(submissions_path, 'wb')
    
    # Output assessments table
    assessments_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "assessments.csv"
    if os.path.isfile(assessments_path):
        os.remove(assessments_path)
            
    assessments_file = open(assessments_path, 'wb')
    
    while True:
        
        if current_date == course_end_date:
            break;
        
        for file in files:
            if current_date in file:
                fp = open(path + file,"r")                
                lines = fp.readlines()
                
                print file
                        
                for line in lines:                              
                    jsonObject = json.loads(line)
                
                    if jsonObject["event_type"] in submission_event_collection:
                        
                        course_id = jsonObject["context"]["course_id"]
                          
                        # Some log records have empty user_id value  
                        if jsonObject["context"]["user_id"] != "":
                            
                            course_user_id = course_id + "_" + str(jsonObject["context"]["user_id"]) 
                            
                            problem_id = ""
                        
                            grade = ""
                            max_grade = ""                     
                        
                            if isinstance(jsonObject["event"], dict):                     
                                problem_id = jsonObject["event"]["problem_id"]
                                
                                # The fields "grade" and "max_grade" are specific to submission event "problem_check"
                                if jsonObject["event"].has_key("grade") and jsonObject["event"].has_key("max_grade"):
                                    grade = jsonObject["event"]["grade"]
                                    max_grade = jsonObject["event"]["max_grade"]                       
                        
                            if isinstance(jsonObject["event"], unicode):                                                      
                                regex = re.compile("input_[a-zA-Z0-9-_]+")
                                problem_id_array = regex.findall(jsonObject["event"])
                                if not len(problem_id_array) == 0:                                
                                    problem_id = problem_id_array[0]                                
                                
                                    subRegex = re.compile("-[a-zA-Z0-9]*_[a-zA-Z0-9]*-")
                                    if not len(subRegex.findall(problem_id)) == 0:
                                        original_course_id = subRegex.findall(problem_id)[0]
                                        changed_course_id = original_course_id.replace("_",".")
                                        problem_id = problem_id.replace(original_course_id, changed_course_id)
                                    
                                    problem_id = problem_id.replace("input_", "")
                                    problem_id = problem_id[0:problem_id.index("_")]
                                    xml_array = problem_id.split("-")
                                
                                    problem_id = xml_array[0] + "://" + xml_array[1] + "/" + xml_array[2] + "/" + xml_array[3] + "/" + xml_array[4]                           
                                                         
                            if problem_id != "":
                                
                                submission_id = course_user_id + "_" + problem_id
                            
                                # For submissions
                                if not submission_id in submission_id_set:
                                    submission_id_set.add(submission_id)
                                    submissions_file.write(str(submission_id) + "," + course_user_id + "," + problem_id + "\n")
                            
                                # For assessments
                                if jsonObject["event_source"] == "server":
                                    assessments[submission_id] = {"course_user_id":course_user_id, "max_grade":max_grade, "grade":grade}                  
                
        current_date = getNextDay(current_date)
        
    for assessment in assessments:
        assessments_file.write(str(assessment) + "," + assessments[assessment]["course_user_id"] + "," 
                               + str(assessments[assessment]["max_grade"]) + "," + str(assessments[assessment]["grade"]) + "\n")
                                     
    
    submissions_file.close()
    assessments_file.close()
    
    print "Submission mode finished."


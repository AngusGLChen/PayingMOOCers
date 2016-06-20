'''
Created on Sep 9, 2015

@author: Angus
'''

import os
import json
import time,datetime
import operator
import random
from sets import Set

def getDayDiff(beginDate,endDate):  
    format="%Y-%m-%d"  
    bd = datetime.datetime.strptime(beginDate,format)  
    ed = datetime.datetime.strptime(endDate,format)      
    oneday = datetime.timedelta(days=1)  
    count = 0
    while bd != ed:  
        ed = ed - oneday  
        count += 1
    return count

def getNextDay(current_day_string):
    format="%Y-%m-%d";
    current_day = datetime.datetime.strptime(current_day_string,format)
    oneday = datetime.timedelta(days=1)
    next_day = current_day + oneday   
    return str(next_day)[0:10]

def cmp_datetime(a_datetime, b_datetime):
    if a_datetime < b_datetime:
        return -1
    elif a_datetime > b_datetime:
        return 1
    else:
        return 0 

def EdXMatching(path):
    
    email_user_map = {}
    
    # Processing user_pii.csv file
    user_pii_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "user_pii.csv"
    user_pii_fp = open(user_pii_path,"r")
    for line in user_pii_fp:
        line = line.replace("\n", "")
        array = line.split(",")
        global_user_id = array[0]
        email = array[5]        
        email = str.lower(email)        
        email_user_map[email] = global_user_id
    
    user_pii_fp.close()    
    print "The number of enrolled learners is: " + str(len(email_user_map)) + "\n"  
    return email_user_map

def InsertBonusMark(path):
       
    email_user_map = EdXMatching(path)
    
    # Output bonus_mark sql file
    bonus_mark_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "bonus_mark.sql"
    if os.path.isfile(bonus_mark_path):
        os.remove(bonus_mark_path)
        
    bonus_mark_file = open(bonus_mark_path, 'wb')
    bonus_mark_file.write("\r\n" + "USE EX101x;" + "\r\n")    
    bonus_mark_file.write("\r\n" + "ALTER TABLE global_user ADD bonus_mark BOOLEAN DEFAULT FALSE;" + "\r\n") 
    
    # Processing bonus_email file    
    email_set = Set()    
    num_bonus_learners = 0  
    num_ineffective_email = 0
    
    num_bonus_exercise = 0
    num_effective_bonus_exercise = 0
    
    week_activeLearner_map = {}
                    
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = array[1]
        
        #if week == "7":
        #    print email
         
        if email not in email_set:
            email_set.add(email)
            if email_user_map.has_key(email):         
                global_user_id = email_user_map[email]                                    
                write_string = "\r\n" + "UPDATE global_user SET bonus_mark = TRUE WHERE global_user_id ="
                write_string += "'" + global_user_id + "';\r\n"
                bonus_mark_file.write(write_string)
                
                num_bonus_learners += 1
                
            else:
                num_ineffective_email += 1
        
        if week in week_activeLearner_map.keys():
            week_activeLearner_map[week] += 1
        else:
            week_activeLearner_map[week] = 1
        
        num_bonus_exercise += 1
        if email_user_map.has_key(email):
            num_effective_bonus_exercise += 1
        

    bonus_mark_file.close()
    
    print "The number of emails contained in the bonus email file is: " + str(len(email_set))
    print "The number of bonus learners is: " + str(num_bonus_learners)    
    print "The number of ineffective emails is: " + str(num_ineffective_email)
    print "The number of bonus exercise is: " + str(num_bonus_exercise)
    print "The number of effective bonus exercise is: " + str(num_effective_bonus_exercise) + "\n"
    
    for week in week_activeLearner_map.keys():
        print str(week) + "\t" + str(week_activeLearner_map[week])
    print ""
    
def InsertDedicatedBonusMark(path):
       
    email_user_map = EdXMatching(path)
    
    # Output dedicated bonus_mark sql file
    bonus_table_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "dedicated_bonus_mark.sql"
    if os.path.isfile(bonus_table_path):
        os.remove(bonus_table_path)
        
    bonus_table_file = open(bonus_table_path, 'wb')
    bonus_table_file.write("\r\n" + "USE EX101x;" + "\r\n")    
    bonus_table_file.write("\r\n" + "ALTER TABLE global_user ADD dedicated_bonus_mark BOOLEAN DEFAULT FALSE;" + "\r\n") 
    
    # Processing bonus_email file    
    email_week_map = {}
    num_dedicated_bonus_learner = 0
                    
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = array[1]
        
        if email_user_map.has_key(email):            
            if email not in email_week_map.keys():                    
                email_week_map[email] = set(week)
            else:
                email_week_map[email].add(week)
                
    for email in email_week_map:
        if len(email_week_map[email]) >= 3:
            global_user_id = email_user_map[email]                                    
            write_string = "\r\n" + "UPDATE global_user SET dedicated_bonus_mark = TRUE WHERE global_user_id ="
            write_string += "'" + global_user_id + "';\r\n"
            bonus_table_file.write(write_string)
            num_dedicated_bonus_learner += 1

    bonus_table_file.close()
    
    print "The number of dedicated bonus learners is: " + str(num_dedicated_bonus_learner) + "\n"
    
def AnalyzeCheckedBonusDistribution(path):
    
    # Output result
    output_path = path + "/checked_bonus_result.txt"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    # Course information
    course_id = ""
    course_start_date = ""
    course_end_date = ""    
    
    # Bonus exercise information
    bonus_id_set = set()
        
    files = os.listdir(path)
       
    # Processing course_structure data               
    for file in files:             
        if "course_structure" in file:
            
            course_id_array = file.split("-")
            course_id = course_id_array[0] + "/" + course_id_array[1] + "/" + course_id_array[2]
                       
            fp = open(path + file,"r")            
            lines = fp.readlines()
            jsonLine = ""   
            for line in lines:
                line = line.replace("\n","")
                jsonLine += line
            
            jsonObject = json.loads(jsonLine)
            for record in jsonObject:
                if jsonObject[record]["category"] == "course":
                    # To obtain the course_start_date
                    course_start_date = jsonObject[record]["metadata"]["start"]
                    course_start_date = course_start_date[0:course_start_date.index("T")]
                    # To obtain the course_end_date
                    course_end_date = jsonObject[record]["metadata"]["end"]
                    course_end_date = course_end_date[0:course_end_date.index("T")]
                else:              
                    resourse_id = record
                    if "display_name" in jsonObject[record]["metadata"]:
                        name = jsonObject[record]["metadata"]["display_name"]
                        if "Bonus Exercise" in name:
                            if "visible_to_staff_only" in jsonObject[record]["metadata"]:
                                if jsonObject[record]["metadata"]["visible_to_staff_only"] != True:                                
                                    array = resourse_id.split("/")
                                    resourse_id = array[len(array)-1]                                
                                    bonus_id_set.add(resourse_id)
                                                                                              
                            else:
                                array = resourse_id.split("/")
                                resourse_id = array[len(array)-1]                                
                                bonus_id_set.add(resourse_id)                            
    
    current_date = course_start_date   
    course_end_next_date = getNextDay(course_end_date)  
    
    user_event_logs = {}
    updated_user_event_logs = {}
    
    format="%Y-%m-%d %H:%M:%S" 
    
    while True:
        
        if current_date == course_end_next_date:
            break;
        
        for file in files:           
            if current_date in file:
           
                print file
                
                user_event_logs.clear()                
                user_event_logs = updated_user_event_logs.copy()                
                updated_user_event_logs.clear()                
                
                fp = open(path + file,"r")
                lines = fp.readlines()
                        
                for line in lines:
                    
                    jsonObject = json.loads(line)
                    
                    global_user_id = jsonObject["context"]["user_id"]
                    course_user_id = course_id + "_" + str(global_user_id)
                    event_type = jsonObject["event_type"]
                    
                    time = jsonObject["time"]
                    event_time = jsonObject["time"]
                    event_time = event_time[0:19]
                    event_time = event_time.replace("T", " ")                                
                    event_time = datetime.datetime.strptime(event_time,format)                                 
                                        
                    if user_event_logs.has_key(course_user_id):
                        user_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type})
                    else:
                        user_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type}]
                
                fp.close()                                             
   
                for user in user_event_logs.keys():
                    
                    course_user_id = user                    
                    event_logs = user_event_logs[user]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))                    
                    
                    final_time = ""
                    
                    start_time = ""
                    end_time = ""
                    element_id = ""
                                      
                    for log in event_logs:
                        
                        event_type = log["event_type"]
                        
                        if start_time == "":
                            
                            if "/" == event_type[len(event_type) - 1]:
                                
                                array = event_type.split("/")
                                element_id = array[len(array)-2]
                                
                                if element_id in bonus_id_set:                                    
                                    event_time = log["event_time"]
                                    start_time = event_time                                
                        else:
                            
                            event_time = log["event_time"]                                    
                            end_time = event_time
                            
                            duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                            
                            # Output results
                            output_file.write(course_user_id + "," + element_id + "," + str(duration) + "\n")
                            
                            start_time = ""
                            end_time = ""
                            element_id = ""
                            
                            final_time = end_time                        
                        
                    if final_time != "":
                        new_logs = []                
                        for log in event_logs:                 
                            if log["event_time"] > final_time:
                                new_logs.append(log)
                                
                        updated_user_event_logs[user] = new_logs
                        
                                     
        current_date = getNextDay(current_date)
        
    output_file.close()

def InsertCheckedBonusMark(path):
    
    checked_bonus_learner_set = set()
    
    path = path + "/checked_bonus_result.txt"
    fp = open(path, "r")
    for line in fp:
        line = line.replace("\n","")
        array = line.split(",")
        
        course_user_id = array[0]
        duration = float(array[2])
        
        if duration > 20:
            checked_bonus_learner_set.add(course_user_id)
            
    print "The number of checked bonus learners is: " + str(len(checked_bonus_learner_set))

    # Output checked_bonus_mark sql file
    checked_bonus_mark_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "checked_bonus_mark.sql"
    if os.path.isfile(checked_bonus_mark_path):
        os.remove(checked_bonus_mark_path)
        
    checked_bonus_mark_file = open(checked_bonus_mark_path, 'wb')
    checked_bonus_mark_file.write("\r\n" + "USE EX101x;" + "\r\n")    
    checked_bonus_mark_file.write("\r\n" + "ALTER TABLE global_user ADD checked_bonus_mark BOOLEAN DEFAULT FALSE;" + "\r\n") 
        
    for user in checked_bonus_learner_set:
        course_user_id = user
        
        write_string = "\r\n" + "UPDATE global_user SET checked_bonus_mark = TRUE WHERE course_user_id ="
        write_string += "'" + course_user_id + "';\r\n"
        checked_bonus_mark_file.write(write_string)
    
    checked_bonus_mark_file.close()       
    
def OutputBonusTable(path):
       
    email_user_map = EdXMatching(path)
    
    # Output bonus table file
    bonus_table_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "bonus.sql"
    if os.path.isfile(bonus_table_path):
        os.remove(bonus_table_path)
        
    bonus_table_file = open(bonus_table_path, 'wb')
    bonus_table_file.write("\r\n" + "USE EX101x;" + "\r\n")    
    bonus_table_file.write("\r\n" + "DROP TABLE IF EXISTS bonus_exercise; CREATE TABLE bonus_exercise (bonus_exercise_id varchar(255) NOT NULL, course_user_id varchar(255), week INT, exercise_id INT, PRIMARY KEY (bonus_exercise_id), FOREIGN KEY (course_user_id) REFERENCES global_user(course_user_id)) ENGINE=MyISAM;" + "\r\n")

    # Processing bonus_email file
    course_id = "DelftX/EX101x/1T2015"
                    
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = array[1]
        exercise_id = array[2]
         
        if email_user_map.has_key(email):                                     
            global_user_id = email_user_map[email]
            
            course_user_id = course_id + "_" + global_user_id
            bonus_exercise_id = course_user_id + "_" + str(week) + "_" + str(exercise_id)         
            
            write_string = "\r\n" + "insert into bonus_exercise(bonus_exercise_id, course_user_id, week, exercise_id) values"
            write_string += "('%s','%s','%s','%s');\r\n" % (bonus_exercise_id, course_user_id, week, exercise_id)  
            bonus_table_file.write(write_string)        

    bonus_table_file.close()
    
def OutputLearnerBonusTable(path):
    
    learner_bonus_map = {}
    
    # Output learner-bonus table file
    output_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "learner_bonus.txt"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, "w")
    output_file.write("learner\t[week1,week2,week3,week4,week5,week6,week7,week8]" + "\n")
    
    email_id_map = {}
    id_set = set()
    
    # To gather the bonus_email information
    bonus_email_path = path + "bonus_email_map.txt"
    bonus_email_fp = open(bonus_email_path, "r")   
    for line in bonus_email_fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = int(array[1])
        
        if email_id_map.has_key(email):
            id = email_id_map[email]
            learner_bonus_map[id][week - 1] = 1
            
        else:
            
            id = ""            
            while (id=="" or id in id_set):         
                array = random.sample(range(100000), 1)
                id = array[0]
            
            email_id_map[email] = id
            id_set.add(id)
            
            learner_bonus_map[id] = [0, 0, 0, 0, 0, 0, 0, 0]
            learner_bonus_map[id][week - 1] = 1
                
    for learner in learner_bonus_map.keys():        
        output_file.write(str(learner) + "\t" + str(learner_bonus_map[learner]) + "\n")
   
        
        
    
    







####################################################    
path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
InsertBonusMark(path)
#InsertDedicatedBonusMark(path)
#OutputBonusTable(path)

#AnalyzeCheckedBonusDistribution(path)
#InsertCheckedBonusMark(path)

#OutputLearnerBonusTable(path)
print "Finished."




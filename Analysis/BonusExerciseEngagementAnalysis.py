'''
Created on Oct 8, 2015

@author: Angus
'''

import os, json, csv
import time,datetime
import operator

import mysql.connector

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import ttest_ind, mannwhitneyu

def EdXMatching(path):
    
    email_user_map = {}
    user_email_map = {}
    user_country = {}
    
    # Processing user_pii.csv file
    user_pii_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "user_pii.csv"
    user_pii_fp = open(user_pii_path,"r")
    for line in user_pii_fp:
        line = line.replace("\n", "")
        array = line.split(",")
        global_user_id = array[0]
        country = array[4]
        email = array[5]        
        email = str.lower(email)        
               
        email_user_map[email] = global_user_id
        user_email_map[global_user_id] = email
        user_country[global_user_id] = country
    
    user_pii_fp.close()
    
    # Translate the country information
    # 1. To translate the country shorten name into full name
    country_name_map = {}
    match_path = path + "match_countries.csv"
    fp = open(match_path, "r")
    for line in fp:
        shorten_name = line[0:2]
        full_name = str.lower(line[3:len(line)].replace("\n", "").replace("\"","").strip())
        country_name_map[shorten_name] = full_name
    fp.close()
    
    # 2. To gather the list of developed countries
    developed_country_set = set()
    developed_country_path = path + "oecd"
    fp = open(developed_country_path, "r")
    for line in fp:
        country = str.lower(line.replace("\n", "").strip())
        developed_country_set.add(country)
    fp.close()
    
    # 3. To decide whether a country is developed or developing
    for user in user_country.keys():
        country = user_country[user]
        
        if country in ["NULL", ""] or country not in country_name_map.keys():
            user_country[user] = "NULL"
            continue

        country_fullname = country_name_map[country]        
        if country_fullname in developed_country_set:
            user_country[user] = "True"
        else:
            user_country[user] = "False"  
    
    
    #print "The number of enrolled learners is: " + str(len(email_user_map)) + "\n"  
    return (email_user_map, user_email_map, user_country)

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
    
def ProcessCourseStructure(path):
    
    files = os.listdir(path)
    
    # Course information  
    course_start_date = ""
    course_end_date = ""
    
    resource_week_map = {}
    bonus_id_set = set()
       
    # Processing course_structure data               
    for file in files:             
        if "course_structure" in file:
                                   
            fp = open(path + file,"r")            
            lines = fp.readlines()
            jsonLine = ""   
            for line in lines:
                line = line.replace("\n","")
                jsonLine += line     
            
            children_parent_map = {}            
            resource_time_map = {}            
            resource_without_time = []       
            
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
                    
                    # Children to parent relation                    
                    for child in jsonObject[resourse_id]["children"]:
                        children_parent_map[child] = resourse_id                                     
                                                
                    # Time information about resources
                    if "start" in jsonObject[resourse_id]["metadata"]:
                        resource_start_time = jsonObject[resourse_id]["metadata"]["start"]
                        resource_time_map[resourse_id] = resource_start_time
                    else:
                        resource_without_time.append(resourse_id)
                        
                    # For bonus exercises
                    if "display_name" in jsonObject[record]["metadata"]:
                        name = jsonObject[record]["metadata"]["display_name"]
                        if "Bonus Exercise" in name:
                            if "visible_to_staff_only" not in jsonObject[record]["metadata"]:
                                array = resourse_id.split("/")
                                resourse_id = array[len(array)-1]                          
                                bonus_id_set.add(resourse_id)
                                                         
            # To determine the start_time for all resource 
            for resource in resource_without_time:
                
                resource_start_time = ""
                             
                while resource_start_time == "":                     
                    resource_parent = children_parent_map[resource]
                    while not resource_time_map.has_key(resource_parent):
                        resource_parent = children_parent_map[resource_parent]
                    resource_start_time = resource_time_map[resource_parent]
                
                resource_time_map[resource] = resource_start_time
            
            # To determine the relevant week for all resource            
            for resource in resource_time_map:
                
                resource_start_time = resource_time_map[resource]
                resource_start_time = resource_start_time[0:resource_start_time.index("T")]            
                week = getDayDiff(course_start_date, resource_start_time) / 7
                
                # To record resource-week-relation
                resource_week_map[resource] = week
                
    return (course_start_date, course_end_date, resource_week_map, bonus_id_set)     
                    
def GenerateEngagementSequence(path):
    
    course_start_date, course_end_date, resource_week_map, bonus_id_set = ProcessCourseStructure(path)
    
    # Process events data
    files = os.listdir(path)
    
    current_date = course_start_date   
    course_end_next_date = getNextDay(course_end_date)
    
    # Log video event types
    video_event_types = []
    
    video_event_types.append("play_video")
    video_event_types.append("edx.video.played")
    
    video_event_types.append("stop_video")
    video_event_types.append("edx.video.stopped")    
    
    video_event_types.append("pause_video")
    video_event_types.append("edx.video.paused")
       
    navigation_event_types = []
    navigation_event_types.append("page_close")
    navigation_event_types.append("seq_goto")
    navigation_event_types.append("seq_next")
    navigation_event_types.append("seq_prev")
    
    user_event_logs = {}
    updated_user_event_logs = {}
    
    engagement_record = {}
    
    while True:
        
        if current_date == course_end_next_date:
            break;
        
        for file in files:           
            if current_date in file:
           
                print file

                # For video-watching events
                user_event_logs.clear()
                
                # Deep copy
                user_event_logs = updated_user_event_logs.copy()        
                updated_user_event_logs.clear()
                                
                fp = open(path + file,"r")
                lines = fp.readlines()
                
                # Record events
                for line in lines:
                    
                    jsonObject = json.loads(line)
                    
                    # For video events
                    if jsonObject["event_type"] in video_event_types:

                        global_user_id = jsonObject["context"]["user_id"]
                        
                        if global_user_id != "":
                            
                            course_id = jsonObject["context"]["course_id"]
                            course_user_id = course_id + "_" + str(global_user_id)
                        
                            video_id = ""
                        
                            event_time = jsonObject["time"]
                            event_time = event_time[0:19]
                            event_time = event_time.replace("T", " ")
                            format="%Y-%m-%d %H:%M:%S"
                            event_time = datetime.datetime.strptime(event_time,format)
                        
                            event_type = jsonObject["event_type"]
                            
                            #############################################################
                            # This sub-condition does not exist in log data
                            if isinstance(jsonObject["event"], dict):
                                video_id = jsonObject["event"]["id"]
                                print video_id
                                if "currentTime" in jsonObject:
                                    videoCurrentTime = jsonObject["event"]["currentTime"]
                                    print videoCurrentTime
                            #############################################################                            
                                                    
                            if isinstance(jsonObject["event"], unicode):
                                event_jsonObject = json.loads(jsonObject["event"])
                                video_id = event_jsonObject["id"]                                                           
                        
                            # To record events 
                            if user_event_logs.has_key(course_user_id):
                                user_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type, "video_id":video_id})
                            else:
                                user_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type, "video_id":video_id}]
                    
                    # For navigation events                                    
                    if jsonObject["event_type"] in navigation_event_types:
                        
                        global_user_id = jsonObject["context"]["user_id"]
                        
                        if global_user_id != "":
                            course_id = jsonObject["context"]["course_id"]
                            course_user_id = course_id + "_" + str(global_user_id)                                                
                        
                            event_time = jsonObject["time"]
                            event_time = event_time[0:19]
                            event_time = event_time.replace("T", " ")
                            format="%Y-%m-%d %H:%M:%S"
                            event_time = datetime.datetime.strptime(event_time,format)
                        
                            event_type = jsonObject["event_type"]                  
                                                      
                            if user_event_logs.has_key(course_user_id):
                                user_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type})
                            else:
                                user_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type}]
                    
                    # For other events
                    if jsonObject["event_type"] not in video_event_types and jsonObject["event_type"] not in navigation_event_types:
                        global_user_id = jsonObject["context"]["user_id"]
                        if global_user_id != "":
                            course_id = jsonObject["context"]["course_id"]
                            course_user_id = course_id + "_" + str(global_user_id)
                        
                            event_time = jsonObject["time"]
                            event_time = event_time[0:19]
                            event_time = event_time.replace("T", " ")
                            format="%Y-%m-%d %H:%M:%S"
                            event_time = datetime.datetime.strptime(event_time,format)
                        
                            event_type = jsonObject["event_type"] 
                    
                            if user_event_logs.has_key(course_user_id):
                                user_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type})
                            else:
                                user_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type}]
                    
                                                                        
                # Process events       
                for user in user_event_logs.keys():
                    
                    course_user_id = user
                    resource_id = ""
                    
                    event_logs = user_event_logs[user]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
                    
                    # For video-watching events
                    video_start_time = ""
                    final_time = ""
                    
                    # For bonus-checking events 
                    bonus_start_time = ""
                    bonus_exercise_id = ""
                                      
                    for log in event_logs:
                        
                        ##########################################################
                        # For video-watching events
                        if log["event_type"] in ["play_video", "edx.video.played"]:
                            video_start_time = log["event_time"]
                            resource_id = log["video_id"]
                            resource_id = resource_id.replace("-", "://", 1)
                            resource_id = resource_id.replace("-", "/")
                        
                        if video_start_time != "":
                                                    
                            if log["event_time"] > video_start_time + datetime.timedelta(hours=0.5):
                                video_start_time = ""
                                resource_id = ""
                                final_time = log["event_time"]
                            else:
                                                                
                                # 1. Pause/Stop situation
                                if log["event_type"] in ["pause_video", "edx.video.paused", "stop_video", "edx.video.stopped"] and resource_id == log["video_id"]:                                    
                                    
                                    watch_duration = (log["event_time"] - video_start_time).seconds
                                    finish_time = log["event_time"]
                                                                     
                                    if watch_duration > 5:
                                        
                                        if course_user_id not in engagement_record.keys():
                                            engagement_record[course_user_id] = []
                                        
                                        week = resource_week_map[resource_id]                    
                                        
                                        engagement_record[course_user_id].append({"resource_id":resource_id, "event_type": "watch_video", "duration":watch_duration, "week":week, 
                                                                        "finish_time":finish_time})
                                    
                                    # For video general information
                                    video_start_time = ""
                                    resource_id = ""
                                    final_time = log["event_time"]
                                    
                                    continue
                                    
                                # 2. Page changed/Session closed
                                if log["event_type"] in navigation_event_types:
                                    finish_time = log["event_time"]
                                    watch_duration = (finish_time - video_start_time).seconds                                    
                                                                    
                                    if watch_duration > 5:
                                        
                                        if course_user_id not in engagement_record.keys():
                                            engagement_record[course_user_id] = []
                                                                            
                                        week = resource_week_map[resource_id]                    
                                        
                                        engagement_record[course_user_id].append({"resource_id":resource_id, "event_type": "watch_video", "duration":watch_duration, "week":week, 
                                                                        "finish_time":finish_time})                          
                                    
                                    # For video general information
                                    video_start_time = ""
                                    resource_id = ""
                                    final_time = log["event_time"]
                                    
                                    continue
                        
                        ##########################################################
                        # For bonus-checking events
                                                
                        event_type = log["event_type"]
                        
                        if bonus_start_time == "":
                            
                            if "/" == event_type[len(event_type) - 1]:
                                array = event_type.split("/")
                                bonus_exercise_id = array[len(array)-2]
                                                                
                                if bonus_exercise_id in bonus_id_set:               
                                    bonus_start_time = log["event_time"]                         
                        else:
                            
                            finish_time = log["event_time"]                                    
                                                        
                            duration = (finish_time - bonus_start_time).days * 24 * 60 * 60 + (finish_time - bonus_start_time).seconds
                            
                            if duration > 0:
                                
                                bonus_exercise_id = "i4x://DelftX/EX101x/sequential/" + bonus_exercise_id
                                week = resource_week_map[bonus_exercise_id]
                                
                                if course_user_id not in engagement_record.keys():
                                    engagement_record[course_user_id] = []
                                
                                engagement_record[course_user_id].append({"resource_id":bonus_exercise_id, "event_type": "check_bonus", "duration":duration, "week":week, "finish_time":finish_time})
                            
                            bonus_start_time = ""
                            bonus_exercise_id = ""
                            
                            final_time = finish_time
                        
                    if final_time != "":
                        new_logs = []                
                        for log in event_logs:                 
                            if log["event_time"] > final_time:
                                new_logs.append(log)
                                
                        updated_user_event_logs[user] = new_logs
                
        current_date = getNextDay(current_date)
    
    
    print "--------------------------------------------------"
    
    # Output the video-watching & bonus-exercise-checking sequence
    output_path = path + "bonus_exercise_engagement_video_watching"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    writer = csv.writer(output_file)   
    
    for course_user_id in engagement_record.keys():        
        for record in engagement_record[course_user_id]:
            resource_id = record["resource_id"]
            resource_id = resource_id.replace("-", "://", 1)
            resource_id = resource_id.replace("-", "/")         
            writer.writerow([course_user_id, resource_id, record["event_type"], record["duration"], record["week"], record["finish_time"]])

    output_file.close()

def AnalyzeEngagementSequence1(path):
    
    course_start_date, course_end_date, resource_week_map, bonus_id_set = ProcessCourseStructure(path)
    
    check_week = 1
    check_bonus_id = ""
    
    engagement_record = {}
    check_bonus_learner_set = set()
    before_after_time = {}
    
    week_bonus_learner_map = {}
    
    # 0. Gather the list of bonus learners
    email_user_map, user_email_map, user_country = EdXMatching(path)
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = int(array[1])
         
        if email_user_map.has_key(email):         
            global_user_id = email_user_map[email]
            course_user_id = "DelftX/EX101x/1T2015_" + global_user_id
            
            if not week_bonus_learner_map.has_key(week):
                week_bonus_learner_map[week] = set()
            
            week_bonus_learner_map[week].add(course_user_id)
    fp.close()
    
    print "The number of BE learners each week..."
    for week in [1, 2, 3, 4, 5, 7]:
        print str(week) + "\t" + str(len(week_bonus_learner_map[week]))
    print
    
    # 1. Search for the bonus exercise id
    for bonus_id in bonus_id_set:
        bonus_id = "i4x://DelftX/EX101x/sequential/" + bonus_id
        if resource_week_map[bonus_id] == check_week:
            check_bonus_id = bonus_id

    # 2. Read engagement file
    input_path = path + "bonus_exercise_engagement_video_watching_0"
    fp = open(input_path, "r")
    lines = fp.readlines()
    for line in lines:
        line = line.replace("\n","")
        array = line.split(",")
        course_user_id = array[0]
        resource_id = array[1]
        event_type = array[2]
        duration = int(array[3])
        week = int(array[4])
        
        event_time = array[5]   
        format="%Y-%m-%d %H:%M:%S "
        event_time = datetime.datetime.strptime(event_time, format)
        
        if not engagement_record.has_key(course_user_id):
            engagement_record[course_user_id] = []
        engagement_record[course_user_id].append({"course_user_id":course_user_id, "resource_id":resource_id, "event_type":event_type, "duration":duration, "week":week, "event_time":event_time})
      
    # 3. Calculate the before/after time that each learner checked the bonus exercise
    for user in engagement_record.keys():
                    
        course_user_id = user
        event_logs = engagement_record[course_user_id]
        event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
        
        before_time = 0
        after_time = 0        
        bonus_check = False
        
        for event_log in event_logs:
            
            if not bonus_check:                
                if event_log["resource_id"] == check_bonus_id:
                    bonus_check = True
                    check_bonus_learner_set.add(course_user_id)
                else:
                    if event_log["week"] == check_week:
                        before_time += event_log["duration"] 
                    else:
                        after_time += event_log["duration"]
            else:                
                after_time += event_log["duration"]
        if bonus_check or before_time > 0:
            
            #################################################################
            # To exclude learners who actually made bonus exercise submission
            if course_user_id not in week_bonus_learner_map[check_week]:
            
                before_after_time[course_user_id] = {"before_time":before_time, "after_time":after_time}
    
       
    num_learner = len(before_after_time)
    lower_bound = int(num_learner * 0.00)
    upper_bound = int(num_learner * 1.00)
    
    sorted_before_after_time = sorted(before_after_time.items(), key=lambda d:d[1]["before_time"])
    
    # Check the distribution
    before_time_array = []
    after_time_array = []
    for i in range(lower_bound, upper_bound):
        before_time_array.append(sorted_before_after_time[i][1]["before_time"]/60)
        after_time_array.append(sorted_before_after_time[i][1]["after_time"]/60)
        
    #plt.hist(before_time_array)
    #plt.show()
    
         
    # 4. Divide learners into two groups
    
    output_path = path + "engagement-1"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w') 
    
    groups = [{},{}]
    
    for i in range(lower_bound, upper_bound):
        if i < lower_bound + (upper_bound-lower_bound)/2:
            groups[0][sorted_before_after_time[i][0]] = sorted_before_after_time[i][1]["after_time"]
        else:
            groups[1][sorted_before_after_time[i][0]] = sorted_before_after_time[i][1]["after_time"]
    
    for group in groups:
        
        checked_array = []
        unchecked_array = []
        
        for course_user_id in group:
            
            if course_user_id in check_bonus_learner_set:
                checked_array.append(group[course_user_id])
                output_file.write(course_user_id + "\n")
            else:
                unchecked_array.append(group[course_user_id])
                
        amount_checked = 0
        amount_unchecked = 0
        
        avg_checked = 0
        avg_unchecked = 0
        
        for value in checked_array:
            amount_checked += value
        if len(checked_array) > 0:
            avg_checked = round(float(amount_checked)/len(checked_array)/3600, 2)
        
        for value in unchecked_array:
            amount_unchecked += value
        if len(unchecked_array) > 0:
            avg_unchecked = round(float(amount_unchecked)/len(unchecked_array)/3600, 2)
        
        print 
        print "The engagement of checked group is: " + str(avg_checked) + "\t" + str(len(checked_array))
        print "The engagement of unchecked group is: " + str(avg_unchecked) + "\t" + str(len(unchecked_array))
        print mannwhitneyu(checked_array, unchecked_array)
        print "\n"
    
    output_file.close()
    
def AnalyzeEngagementSequence2(path):
    
    course_start_date, course_end_date, resource_week_map, bonus_id_set = ProcessCourseStructure(path)
    
    check_week = 7
    check_bonus_id = ""
    
    engagement_record = {}
    candidate_bonus_learner_set = set()
    check_bonus_learner_set = set()
    before_after_time = {}
    
    week_bonus_learner_map = {}
    
    # 0. Gather the list of bonus learners
    email_user_map, user_email_map, user_country = EdXMatching(path)
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = int(array[1])
         
        if email_user_map.has_key(email):         
            global_user_id = email_user_map[email]
            course_user_id = "DelftX/EX101x/1T2015_" + global_user_id
            
            if not week_bonus_learner_map.has_key(week):
                week_bonus_learner_map[week] = set()
            
            week_bonus_learner_map[week].add(course_user_id)
    fp.close()
    
    # 1. Search for the bonus exercise id
    for bonus_id in bonus_id_set:
        bonus_id = "i4x://DelftX/EX101x/sequential/" + bonus_id
        if resource_week_map[bonus_id] == check_week:
            check_bonus_id = bonus_id
    
    # 2. Read candidate bonus learner file
    candidate_input_path = path + "engagement-" + str(check_week-2)
    candidate_fp = open(candidate_input_path, "r")
    lines = candidate_fp.readlines()
    for line in lines:
        line = line.replace("\n","")
        candidate_bonus_learner_set.add(line)
    candidate_fp.close()
    
    # 3. Read engagement file
    engagement_input_path = path + "bonus_exercise_engagement_video_watching_0"
    engagement_fp = open(engagement_input_path, "r")
    lines = engagement_fp.readlines()
    for line in lines:
        line = line.replace("\n","")
        array = line.split(",")
        course_user_id = array[0]
        resource_id = array[1]
        event_type = array[2]
        duration = int(array[3])
        week = int(array[4])
        
        event_time = array[5]   
        format="%Y-%m-%d %H:%M:%S "
        event_time = datetime.datetime.strptime(event_time, format)
        
        if course_user_id not in candidate_bonus_learner_set:
            continue
        
        if not engagement_record.has_key(course_user_id):
            engagement_record[course_user_id] = []
            
        engagement_record[course_user_id].append({"course_user_id":course_user_id, "resource_id":resource_id, "event_type":event_type, "duration":duration, "week":week, "event_time":event_time})
    engagement_fp.close()
    
    # 3. Calculate the before/after time that each learner checked the bonus exercise
    for user in engagement_record.keys():
                    
        course_user_id = user
        event_logs = engagement_record[course_user_id]
        event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
        
        before_time = 0
        after_time = 0        
        bonus_check = False
        
        for event_log in event_logs:
            
            if not bonus_check:                
                if event_log["resource_id"] == check_bonus_id:
                    bonus_check = True
                    check_bonus_learner_set.add(course_user_id)
                else:
                    if event_log["week"] == check_week:
                        before_time += event_log["duration"] 
                    else:
                        after_time += event_log["duration"]
            else:                
                after_time += event_log["duration"]
        if bonus_check or before_time > 0:
            
            #################################################################
            # To exclude learners who actually made bonus exercise submission
            if course_user_id not in week_bonus_learner_map[check_week]:
            
                before_after_time[course_user_id] = {"before_time":before_time, "after_time":after_time}
    
       
    num_learner = len(before_after_time)
    lower_bound = int(num_learner * 0.00)
    upper_bound = int(num_learner * 1.00)
    
    sorted_before_after_time = sorted(before_after_time.items(), key=lambda d:d[1]["before_time"])
    
    # Check the distribution
    before_time_array = []
    for i in range(lower_bound, upper_bound):
        before_time_array.append(sorted_before_after_time[i][1]["before_time"]/60)
        
    #plt.hist(before_time_array)
    #plt.show()
    
    
    # 4. Divide learners into two groups
    
    output_path = path + "engagement-" + str(check_week)
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w') 
    
    groups = [{},{}]
    
    for i in range(lower_bound, upper_bound):
        if i < lower_bound + (upper_bound-lower_bound)/2:
            groups[0][sorted_before_after_time[i][0]] = sorted_before_after_time[i][1]["after_time"]
        else:
            groups[1][sorted_before_after_time[i][0]] = sorted_before_after_time[i][1]["after_time"]
    
    for group in groups:
        
        checked_array = []
        unchecked_array = []
        
        for course_user_id in group:
            
            if course_user_id in check_bonus_learner_set:
                checked_array.append(group[course_user_id])
                output_file.write(course_user_id + "\n")
            else:
                unchecked_array.append(group[course_user_id])
                
        amount_checked = 0
        amount_unchecked = 0
        
        for value in checked_array:
            amount_checked += value
        avg_checked = round(float(amount_checked)/len(checked_array)/3600, 2)
        
        for value in unchecked_array:
            amount_unchecked += value
        avg_unchecked = round(float(amount_unchecked)/len(unchecked_array)/3600, 2)
        
        print 
        print "The engagement of checked group is: " + str(avg_checked) + "\t" + str(len(checked_array))
        print "The engagement of unchecked group is: " + str(avg_unchecked) + "\t" + str(len(unchecked_array))
        print mannwhitneyu(checked_array, unchecked_array)
        print "\n"
    
    output_file.close()
    
    
    
    
    
        
        
                    
        
        
        
    
    
    
    




####################################################   



path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
#GenerateEngagementSequence(path)
#AnalyzeEngagementSequence1(path)
AnalyzeEngagementSequence2(path)
print "Finished."




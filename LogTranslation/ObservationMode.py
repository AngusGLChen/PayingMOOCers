'''
Created on Jul 24, 2015

@author: Angus
'''

import os
import json
import csv

import time,datetime
import operator

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

def observation_mode(path):
  
    files = os.listdir(path)
    
    # Course information
    course_id = ""
    course_start_date = ""
    course_end_date = ""
    
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
            
            children_parent_map = {}
            
            resource_time_map = {}
            resource_type_map = {}
            
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
                    
                    # Types information about resources
                    resource_type_map[resourse_id] = jsonObject[resourse_id]["category"]                      
                                                         
            # To determine the start_time for all resource 
            for resource in resource_without_time:
                
                resource_start_time = ""
                             
                while resource_start_time == "":                     
                    resource_parent = children_parent_map[resource]
                    while not resource_time_map.has_key(resource_parent):
                        resource_parent = children_parent_map[resource_parent]
                    resource_start_time = resource_time_map[resource_parent]
                
                resource_time_map[resource] = resource_start_time      
            
            # Output resource table
            resources_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "resources.csv"
            if os.path.isfile(resources_path):
                os.remove(resources_path)
                            
            resources_file = open(resources_path, 'wb')
            
            # To determine the relevant week for all resource            
            for resource in resource_time_map:
                
                resource_start_time = resource_time_map[resource]
                resource_start_time = resource_start_time[0:resource_start_time.index("T")]            
                week = getDayDiff(course_start_date, resource_start_time) / 7 + 1
                
                # To output each resource record               
                resources_file.write(resource + "," + resource_type_map[resource] + "," + str(week) + "," + course_id + "\n")
                            
            resources_file.close()
    
    # Processing events data
    
    # (a) For video-watching events
    current_date = course_start_date   
    course_end_next_date = getNextDay(course_end_date)
    
    video_event_types = []
    
    video_event_types.append("play_video")
    video_event_types.append("edx.video.played")
    
    video_event_types.append("stop_video")
    video_event_types.append("edx.video.stopped")    
    
    video_event_types.append("pause_video")
    video_event_types.append("edx.video.paused")
        
    video_event_types.append("seek_video")
    video_event_types.append("edx.video.position.changed")
    
    video_event_types.append("speed_change_video")
    
    navigation_event_types = []
    navigation_event_types.append("page_close")
    navigation_event_types.append("seq_goto")
    navigation_event_types.append("seq_next")
    navigation_event_types.append("seq_prev")
    
    user_video_event_logs = {}
    updated_user_video_event_logs = {}
    
    observations = {}
    
    # (b) For session separation
    # Output sessions table
    sessions_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "sessions.csv"
    if os.path.isfile(sessions_path):
        os.remove(sessions_path)
                            
    sessions_file = open(sessions_path, 'wb')
    
    user_all_event_logs = {}
    sessions = {}
    
    # For debugging
    video_learner_set = set()
    session_learner_set = set()
    
    while True:
        
        if current_date == course_end_next_date:
            break;
        
        for file in files:           
            if current_date in file:
           
                print file

                # (a) For video-watching events
                user_video_event_logs.clear()
                # Deep copy
                user_video_event_logs = updated_user_video_event_logs.copy()
                print "-----" + str(len(user_video_event_logs))         
                updated_user_video_event_logs.clear()
                print "-----" + str(len(user_video_event_logs)) + "\n"
                
                # (b) For session separation                
                user_all_event_logs.clear()
                
                fp = open(path + file,"r")
                lines = fp.readlines()
                        
                for line in lines:
                    
                    jsonObject = json.loads(line)
                    
                    # For video events
                    if jsonObject["event_type"] in video_event_types:
                        
                        if not jsonObject.has_key("session"):
                            print jsonObject["event_type"]
                        
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
                        
                            # For seek event
                            new_time = 0
                            old_time = 0
                        
                            # For speed change event
                            new_speed = 0
                            old_speed = 0
                        
                            # This sub-condition does not exist in log data
                            if isinstance(jsonObject["event"], dict):
                                video_id = jsonObject["event"]["id"]
                                print video_id
                                #if "currentTime" in jsonObject:
                                #    videoCurrentTime = jsonObject["event"]["currentTime"]
                                #    print videoCurrentTime

                        
                            if isinstance(jsonObject["event"], unicode):
                                event_jsonObject = json.loads(jsonObject["event"])
                                video_id = event_jsonObject["id"]
                            
                                # For video seek event
                                if "new_time" in event_jsonObject and "old_time" in event_jsonObject:
                                    new_time = event_jsonObject["new_time"]
                                    old_time = event_jsonObject["old_time"]                                                                      
                                                                                
                                # For video speed change event           
                                if "new_speed" in event_jsonObject and "old_speed" in event_jsonObject:
                                    new_speed = event_jsonObject["new_speed"]
                                    old_speed = event_jsonObject["old_speed"]
                        
                            # To record video seek event                
                            if event_type in ["seek_video","edx.video.position.changed"]:
                                if new_time is not None and old_time is not None:                              
                                    if user_video_event_logs.has_key(course_user_id):
                                        user_video_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type, "video_id":video_id, "new_time":new_time, "old_time":old_time})
                                    else:
                                        user_video_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type, "video_id":video_id, "new_time":new_time, "old_time":old_time}]
                                continue
                        
                            # To record video speed change event                
                            if event_type in ["speed_change_video"]:
                                if user_video_event_logs.has_key(course_user_id):
                                    user_video_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type, "video_id":video_id, "new_speed":new_speed, "old_speed":old_speed})
                                else:
                                    user_video_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type, "video_id":video_id, "new_speed":new_speed, "old_speed":old_speed}]
                                continue                                                                      
                         
                            if user_video_event_logs.has_key(course_user_id):
                                user_video_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type, "video_id":video_id})
                            else:
                                user_video_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type, "video_id":video_id}]
                    
                    # For navigation events                                    
                    if jsonObject["event_type"] in navigation_event_types:
                        
                        if not jsonObject.has_key("session"):
                            print jsonObject["event_type"]
                        
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
                                                      
                            if user_video_event_logs.has_key(course_user_id):
                                user_video_event_logs[course_user_id].append({"event_time":event_time, "event_type":event_type})
                            else:
                                user_video_event_logs[course_user_id] = [{"event_time":event_time, "event_type":event_type}]
                              
                    # For session separation
                    global_user_id = jsonObject["context"]["user_id"]
                    if global_user_id != "":
                        course_id = jsonObject["context"]["course_id"]
                        course_user_id = course_id + "_" + str(global_user_id)
                        
                        event_time = jsonObject["time"]
                        event_time = event_time[0:19]
                        event_time = event_time.replace("T", " ")
                        format="%Y-%m-%d %H:%M:%S"
                        event_time = datetime.datetime.strptime(event_time,format)
                        
                        if jsonObject["event_source"] == "mobile":
                            print "mobile"
                            
                        if jsonObject.has_key("session"):                            
                            session_id = jsonObject["session"]                        
                            if session_id != "":                                
                                if user_all_event_logs.has_key(course_user_id):
                                    user_all_event_logs[course_user_id].append({"event_time":event_time, "session_id":session_id})
                                else:
                                    user_all_event_logs[course_user_id] = [{"event_time":event_time, "session_id":session_id}]                                                             
                                                                        
                # (a) For video-watching events       
                for user in user_video_event_logs.keys():
                    
                    course_user_id = user
                    resource_id = ""
                    
                    event_logs = user_video_event_logs[user]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
                    
                    video_start_time = ""
                    final_time = ""
                    
                    # For video seek event
                    times_forwardSeek = 0
                    duration_forwardSeek = 0
                    times_backwardSeek = 0
                    duration_backwardSeek = 0
                    
                    # For video speed change event
                    speed_change_last_time = ""
                    times_speedUp = 0
                    times_speedDown = 0               
                    
                    # For video pause event                   
                    pause_check = False
                    pause_start_time = 0
                    duration_pause = 0                    
                                      
                    for log in event_logs:
                        
                        if log["event_type"] in ["play_video", "edx.video.played"]:
                            
                            video_start_time = log["event_time"]
                            resource_id = log["video_id"]

                            if pause_check:
                                
                                duration_pause = (log["event_time"] - pause_start_time).seconds
                                observation_id = course_user_id + "_" + resource_id+ "_" + str(pause_start_time)
                                
                                if duration_pause > 2 and duration_pause < 600:
                                    if observation_id in observations:
                                        if "times_pause" in observations[observation_id]:
                                            observations[observation_id]["times_pause"] = observations[observation_id]["times_pause"] + 1                                        
                                        else:
                                            observations[observation_id]["times_pause"] = 1                                        
                                        
                                        if "duration_pause" in observations[observation_id]:
                                            observations[observation_id]["duration_pause"] = observations[observation_id]["duration_pause"] + duration_pause
                                        else:
                                            observations[observation_id]["duration_pause"] = duration_pause
                                
                                pause_check = False
                                                        
                            continue 
                        
                        if video_start_time != "":                                                    
                           
                            if log["event_time"] > video_start_time + datetime.timedelta(hours=0.5):
                                
                                video_start_time = ""
                                resource_id = ""
                                final_time = log["event_time"]
                                
                            else:                               
                                
                                # 0. Seek situation
                                if log["event_type"] in ["seek_video", "edx.video.position.changed"] and resource_id == log["video_id"]:                                                                       
                                    # Forward seek event
                                    if log["new_time"] > log["old_time"]:
                                        times_forwardSeek += 1
                                        duration_forwardSeek += log["new_time"] - log["old_time"]
                                    # Backward seek event                                    
                                    if log["new_time"] < log["old_time"]:
                                        times_backwardSeek += 1
                                        duration_backwardSeek += log["old_time"] - log["new_time"]
                                    continue
                                
                                # 1. Speed change
                                if log["event_type"] == "speed_change_video" and resource_id == log["video_id"]:
                                    if speed_change_last_time == "":
                                        speed_change_last_time = log["event_time"]
                                        old_speed = log["old_speed"]
                                        new_speed = log["new_speed"]                                        
                                        if old_speed < new_speed:
                                            times_speedUp += 1
                                        if old_speed > new_speed:
                                            times_speedDown += 1
                                    else:
                                        if (log["event_time"] - speed_change_last_time).seconds > 10:
                                            speed_change_last_time = log["event_time"]
                                            old_speed = log["old_speed"]
                                            new_speed = log["new_speed"]                                        
                                            if old_speed < new_speed:
                                                times_speedUp += 1
                                            if old_speed > new_speed:
                                                times_speedDown += 1
                                    continue
                                
                                # 2. Pause/Stop situation
                                if log["event_type"] in ["pause_video", "edx.video.paused", "stop_video", "edx.video.stopped"] and resource_id == log["video_id"]:                                    
                                    
                                    watch_duration = (log["event_time"] - video_start_time).seconds
                                    
                                    finish_time = log["event_time"]
                                    observation_id = course_user_id + "_" + resource_id + "_" + str(finish_time)
                                 
                                    if watch_duration > 5:                                        
                                        observations[observation_id] = {"course_user_id":course_user_id, "resource_id":resource_id, "type": "video", "watch_duration":watch_duration,
                                                                        "times_forwardSeek":times_forwardSeek, "duration_forwardSeek":duration_forwardSeek, 
                                                                        "times_backwardSeek":times_backwardSeek, "duration_backwardSeek":duration_backwardSeek,
                                                                        "times_speedUp":times_speedUp, "times_speedDown":times_speedDown,
                                                                        "finish_time":finish_time}
                                        
                                        # For debugging
                                        video_learner_set.add(course_user_id)
                                            
                                        if log["event_type"] in ["pause_video", "edx.video.paused"]:
                                            pause_check = True
                                            pause_start_time = finish_time
                                    
                                    # For video seek event
                                    times_forwardSeek = 0
                                    duration_forwardSeek = 0
                                    times_backwardSeek = 0
                                    duration_backwardSeek = 0
                                    
                                    # For video speed change event
                                    speed_change_last_time = ""
                                    times_speedUp = 0
                                    times_speedDown = 0
                                    
                                    # For video general information                                  
                                    video_start_time =""
                                    resource_id = ""
                                    final_time = log["event_time"]
                                    
                                    continue
                                    
                                # 3/4  Page changed/Session closed
                                if log["event_type"] in navigation_event_types:
                                    finish_time = log["event_time"]

                                    watch_duration = (finish_time - video_start_time).seconds 
                                                                       
                                    observation_id = course_user_id + "_" + resource_id + "_" + str(finish_time)
                                
                                    if watch_duration > 5:                                        
                                        observations[observation_id] = {"course_user_id":course_user_id, "resource_id":resource_id, "type": "video", "watch_duration":watch_duration,
                                                                        "times_forwardSeek":times_forwardSeek, "duration_forwardSeek":duration_forwardSeek, 
                                                                        "times_backwardSeek":times_backwardSeek, "duration_backwardSeek":duration_backwardSeek,
                                                                        "times_speedUp":times_speedUp, "times_speedDown":times_speedDown,
                                                                        "finish_time":finish_time}
                                        
                                        # For debugging
                                        video_learner_set.add(course_user_id)
                                    
                                    # For video seek event
                                    times_forwardSeek = 0
                                    duration_forwardSeek = 0
                                    times_backwardSeek = 0
                                    duration_backwardSeek = 0
                                    
                                    # For video speed change event
                                    speed_change_last_time = ""
                                    times_speedUp = 0
                                    times_speedDown = 0
                                    
                                    # For video general information
                                    video_start_time = ""                                    
                                    resource_id = ""
                                    final_time = log["event_time"]
                                    
                                    continue
                        
                    if final_time != "":
                        new_logs = []                
                        for log in event_logs:                 
                            if log["event_time"] > final_time:
                                new_logs.append(log)
                                
                        updated_user_video_event_logs[user] = new_logs                
                     
                # (b) For session separation
                for user in user_all_event_logs.keys():
                    
                    course_user_id = user                    
                    event_logs = user_all_event_logs[user]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
                      
                    session_id = ""
                    start_time = ""
                    end_time = ""
                    
                    for i in range(len(event_logs)):
                        if session_id =="":
                            session_id = event_logs[i]["session_id"]
                            start_time = event_logs[i]["event_time"]
                            end_time = event_logs[i]["event_time"]
                        else:
                            if event_logs[i]["session_id"] == session_id:
                                if event_logs[i]["event_time"] > end_time + datetime.timedelta(hours=0.5):
                                    session_id = session_id + "_" + course_user_id
                                    if sessions.has_key(session_id):
                                        sessions[session_id]["time_array"].append({"start_time":start_time, "end_time":end_time})
                                    else:
                                        sessions[session_id] = {"course_user_id":course_user_id, "time_array":[{"start_time":start_time, "end_time":end_time}]}
                                        
                                    session_id = event_logs[i]["session_id"]
                                    start_time = event_logs[i]["event_time"]                                
                                    end_time = event_logs[i]["event_time"]
                                
                                else:
                                    end_time = event_logs[i]["event_time"]
                            
                            else:
                                session_id = session_id + "_" + course_user_id
                                if sessions.has_key(session_id):
                                    sessions[session_id]["time_array"].append({"start_time":start_time, "end_time":end_time})
                                else:
                                    sessions[session_id] = {"course_user_id":course_user_id, "time_array":[{"start_time":start_time, "end_time":end_time}]}
                                    
                                session_id = event_logs[i]["session_id"]
                                start_time = event_logs[i]["event_time"]                                
                                end_time = event_logs[i]["event_time"]
                        
                        if i == len(event_logs) - 1:
                            session_id = session_id + "_" + course_user_id
                            if sessions.has_key(session_id):
                                sessions[session_id]["time_array"].append({"start_time":start_time, "end_time":end_time})
                            else:
                                sessions[session_id] = {"course_user_id":course_user_id, "time_array":[{"start_time":start_time, "end_time":end_time}]}   
        
        current_date = getNextDay(current_date)
    
    # To compress the session event_logs
    for session in sessions:
        if len(sessions[session]["time_array"]) > 1:            
            start_time = ""
            end_time = ""
            updated_time_array = []
            
            for i in range(len(sessions[session]["time_array"])):                
                if i == 0:
                    start_time = sessions[session]["time_array"][i]["start_time"]
                    end_time = sessions[session]["time_array"][i]["end_time"]
                else:
                    if sessions[session]["time_array"][i]["start_time"] > end_time + datetime.timedelta(hours=0.5):
                        updated_time_array.append({"start_time":start_time, "end_time":end_time})                        
                        start_time = sessions[session]["time_array"][i]["start_time"]
                        end_time = sessions[session]["time_array"][i]["end_time"]
                    else:
                        end_time = sessions[session]["time_array"][i]["end_time"]
                        
                if i == len(sessions[session]["time_array"]) - 1:
                    updated_time_array.append({"start_time":start_time, "end_time":end_time})
            
            sessions[session]["time_array"] = updated_time_array
            
    # Output sessions table
    for session in sessions:        
        session_id = session
        course_user_id = sessions[session]["course_user_id"]
        
        for i in range(len(sessions[session]["time_array"])):
            start_time = sessions[session]["time_array"][i]["start_time"]
            end_time = sessions[session]["time_array"][i]["end_time"]
            if start_time < end_time:
                session_learner_set.add(course_user_id)
                duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                final_session_id = session_id + "_" + str(start_time) + "_" + str(end_time)
                sessions_file.write(final_session_id + "," + course_user_id + "," + str(duration) + "\n")
    
    print "--------------------------------------------------"
    print "The number of session learners is: " + str(len(session_learner_set)) + "\n"       
        
    sessions_file.close()    
    
    # Output observations table
    observations_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Results/EX101x/" + "observations.csv"
    if os.path.isfile(observations_path):
        os.remove(observations_path)            
    observations_file = open(observations_path, 'wb')
    writer = csv.writer(observations_file)
    for observation in observations.keys():
        resource_id = observations[observation]["resource_id"]
        resource_id = resource_id.replace("-", "://", 1)
        resource_id = resource_id.replace("-", "/")
        if "times_pause" in observations[observation]:                
            writer.writerow([observation, observations[observation]["course_user_id"], resource_id, observations[observation]["type"], observations[observation]["watch_duration"],
                             observations[observation]["times_forwardSeek"], observations[observation]["duration_forwardSeek"], 
                             observations[observation]["times_backwardSeek"], observations[observation]["duration_backwardSeek"],
                             observations[observation]["times_speedUp"], observations[observation]["times_speedDown"],
                             observations[observation]["times_pause"], observations[observation]["duration_pause"],
                             observations[observation]["finish_time"]                        
                             ])   
        else:
            writer.writerow([observation, observations[observation]["course_user_id"], resource_id, observations[observation]["type"], observations[observation]["watch_duration"],
                             observations[observation]["times_forwardSeek"], observations[observation]["duration_forwardSeek"], 
                             observations[observation]["times_backwardSeek"], observations[observation]["duration_backwardSeek"],
                             observations[observation]["times_speedUp"], observations[observation]["times_speedDown"],
                             0, 0,
                             observations[observation]["finish_time"]                            
                             ])

    observations_file.close()
                
    print "Observation mode finished."
    
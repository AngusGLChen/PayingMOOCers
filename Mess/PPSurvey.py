'''
Created on Oct 16, 2015

@author: Angus
'''

import os
import mysql.connector

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

def SeekSurveyLearners():
    
    print "To seek survey learners..."   
    survey_learner_set = set()
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()

    sql_query = "SELECT survey_response.course_user_id FROM survey_response, global_user WHERE survey_response.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND survey_response.question_id=\"DelftX/EX101x/1T2015_pre_Q9.3\" AND survey_response.answer=\"1\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    for result in results:
        course_user_id = result[0]
        global_user_id = course_user_id[course_user_id.index("_")+1 : len(course_user_id)]
        survey_learner_set.add(global_user_id)
        
    print "The number of survey learners is: " + str(len(survey_learner_set)) + "\n"
    return survey_learner_set


def SeekBonusLearners(path):
    
    print "To seek bonus learners..."
    bonus_learner_set = set()
    
    email_user_map, user_email_map, user_country = EdXMatching(path)
    
    # Processing bonus_email file                 
    fp = open(path+"bonus_email_map.txt","r")   
    for line in fp:
                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])
        week = array[1]
         
        if email_user_map.has_key(email):         
            global_user_id = email_user_map[email]
            bonus_learner_set.add(global_user_id)
            
    return bonus_learner_set



####################################################
course_path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"

survey_learner_set = SeekSurveyLearners()
bonus_learner_set = SeekBonusLearners(course_path)

print 
print "To seek partition learners..."
email_user_map, user_email_map, user_country = EdXMatching(course_path)

cnt = 0
for learner in survey_learner_set:
    if learner not in bonus_learner_set:
        if user_country[learner] == "True":
            cnt += 1
            print user_email_map[learner] + ";"
        
print "The number of learners is: " + str(cnt)




































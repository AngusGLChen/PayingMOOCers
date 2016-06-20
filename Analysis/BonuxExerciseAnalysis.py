'''
Created on Sep 14, 2015

@author: Angus
'''

import os
from sets import Set
import mysql.connector
from Analysis.SeekLearners import SeekEngagedLearners

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

def ToSeekActiveLearnerByWeek():
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    # To seek active learners
    engaged_learner_set = SeekEngagedLearners()
        
    # To seek active learners by week
    course_week_learner_map = {}
    
    observation_sql_query = "SELECT observations.course_user_id, resources.relevant_week FROM observations, global_user, resources WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND observations.resource_id=resources.resource_id"
    submission_sql_query = "SELECT submissions.course_user_id, resources.relevant_week FROM submissions, global_user, problems, resources WHERE submissions.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND submissions.problem_id=problems.problem_id AND problems.problem_id=resources.resource_id"
    
    sql_array = [observation_sql_query, submission_sql_query]
    for sql_query in sql_array:    
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        for result in results:
            course_user_id = result[0]
            week = result[1]
            
            if course_user_id in engaged_learner_set:            
                if course_week_learner_map.has_key(week):
                    course_week_learner_map[week].add(course_user_id)
                else:
                    course_week_learner_map[week] = set(course_user_id)
    
    return engaged_learner_set, course_week_learner_map    
    
def BonusExerciseAnalysis1(path):
    
    # 1. How many learners did it each week? Is the dropout comparable to the course dropout?
    
    # Processing bonus_email file
    BE_email_set = set()    
    BE_week_email_map = {}             
    fp = open(path+"bonus_email_map.txt", "r")   
    for line in fp:                
        line = line.replace("\n","")        
        array = line.split(",")
        email = str.lower(array[0])      
        week = array[1]
        
        if BE_week_email_map.has_key(week):
            BE_week_email_map[week] += 1
        else:
            BE_week_email_map[week] = 1
        
        BE_email_set.add(email)
        
    engaged_learner_set, course_week_learner_map = ToSeekActiveLearnerByWeek()
    
    print "The number of Engaged learners is: " + str(len(engaged_learner_set))
    print "The number of BE learners is: " + str(len(BE_email_set))
    
    for week in ["1","2", "3","4","5","7"]:
        # print week + "\t" + str(len(BE_week_email_map[week])) + "\t" + str(len(course_week_learner_map[float(week) + 1])) + "\t" +  str(round(len(BE_week_email_map[week])/float(len(BE_email_set))*100, 2)) + "\t" + str(round(len(course_week_learner_map[float(week) + 1])/float(len(engaged_learner_set))*100, 2))
        # print week + "\t" + str(BE_week_email_map[week]) + "\t" + str(len(course_week_learner_map[float(week) + 1])) + "\t" + str(BE_week_email_map[week]/float(len(BE_email_set))) + "\t" + str(len(course_week_learner_map[float(week) + 1])/float(len(engaged_learner_set)))
        print week + "\t" + str(len(course_week_learner_map[float(week) + 1])) + "\t" + str(BE_week_email_map[week]) +"(" + str(round(BE_week_email_map[week]/float(len(course_week_learner_map[float(week) + 1]))*100, 2)) + "%)"
    
    '''
    # 2. What percentage of learners did get each exercise correct?
    
    # Processing bonus_review_results file
    selected_week_BEid_map = {}
    correctness_week_BEid_map = {}
    
    # For checking
    wrong_week_BEid_map = {}
    
    fp = open(path+"bonus_review_results1.csv", "r")
    fp.readline()
    fp.readline()
    name_line = fp.readline()    
    lines = fp.readlines()
    
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(",")
       
        week = array[1][array[1].index("_")+1 : len(array[1])-1]        
        id = array[2][1 : array[2].index(".")]
                
        # For selected_week_BEid_map
        if selected_week_BEid_map.has_key(week):
            selected_week_BEid_map[week].add(id)
        else:
            selected_week_BEid_map[week] = set(id)
        
        # 1. Correct
        correct1 = array[3].replace("\"","")
        # 2. correct if whitespaces trimmed
        correct2 = array[5].replace("\"","")
        # 3. correct if whitespaces trimmed and numbers compared as numbers
        correct3 = array[7].replace("\"","")
        # 4. correct if numbers sorted
        correct4 = array[9].replace("\"","")
        
        #if correct1 == "True" or correct2 == "True" or correct3 == "True" or correct4 == "True":
        if correct3 == "True":
            if correctness_week_BEid_map.has_key(week):
                correctness_week_BEid_map[week].add(id)
            else:
                correctness_week_BEid_map[week] = set(id)
        else:
            if wrong_week_BEid_map.has_key(week):
                wrong_week_BEid_map[week].add(id)
            else:
                wrong_week_BEid_map[week] = set(id)
              
    for week in ["1","2","3","4","5","7"]:
        num_exercise = len(selected_week_BEid_map[week])
        num_correctness = 0
        if week in correctness_week_BEid_map.keys():
            num_correctness = len(correctness_week_BEid_map[week])
                           
        print str(week) + "\t" + str(num_exercise) + "\t" + str(num_correctness) + "\t"  + str(round(float(num_correctness)/num_exercise*100, 2)) + "%"
    print ""
    
    selected_week = "7"    
    for BEid in wrong_week_BEid_map[selected_week]:
        print BEid
    '''
        
def BonusExerciseAnalysis2(path):    
    
    # 2. What percentage of learners did get each exercise correct?
    
    # Processing bonus_review_results file
    selected_week_BEid_map = {}
    correctness_week_BEid_map = {}
    
    # For checking
    wrong_week_BEid_map = {}
    
    fp = open(path+"bonus_review_results2.csv", "r")
    fp.readline()
    fp.readline()
    name_line = fp.readline()    
    lines = fp.readlines()
    
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(",")
       
        week = array[1][array[1].index("_")+1 : len(array[1])-1]     
        id = array[2][1 : array[2].index(".")]
                
        # For selected_week_BEid_map
        if selected_week_BEid_map.has_key(week):
            selected_week_BEid_map[week].add(id)
        else:
            selected_week_BEid_map[week] = set(id)
        
        correct = ""
        
        if week == "1":
            if array[3] == "True" and array[4] == "True" and array[5] == "True" and array[6] == "True":
                correct = "True"
        if week == "2":
            if array[3] == "True" and array[4] == "True" and array[5] == "True" and array[6] == "True" and array[7] == "True":
                correct = "True"
        if week == "3":
            if array[3] == "True" and array[4] == "True" and array[5] == "True":
                correct = "True"
        if week == "4":
            if array[3] == "True" and array[4] == "True":
                correct = "True"
        if week == "5":
            if array[3] == "True" and array[4] == "True" and array[5] == "True" and array[6] == "True" and array[7] == "True" and array[8] == "True":
                correct = "True"
        if week == "7":
            if array[3] == "True" and array[4] == "True" and array[5] == "True":
                correct = "True"
        
        
        if correct == "True":
            if correctness_week_BEid_map.has_key(week):
                correctness_week_BEid_map[week].add(id)
            else:
                correctness_week_BEid_map[week] = set(id)
        else:
            if wrong_week_BEid_map.has_key(week):
                wrong_week_BEid_map[week].add(id)
            else:
                wrong_week_BEid_map[week] = set(id)
              
    for week in ["1","2","3","4","5","7"]:
        num_exercise = len(selected_week_BEid_map[week])
        num_correctness = 0
        if week in correctness_week_BEid_map.keys():
            num_correctness = len(correctness_week_BEid_map[week])
                           
        print str(week) + "\t" + str(num_exercise) + "\t" + str(num_correctness) + "\t"  + str(round(float(num_correctness)/num_exercise*100, 2))  + "%"
    print "\n"
    
    selected_week = "2"    
    for BEid in wrong_week_BEid_map[selected_week]:
        print " " + BEid + " " 
  
    
    
    
    
    




####################################################
path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
BonusExerciseAnalysis1(path) 
#BonusExerciseAnalysis2(path)

print "Finished."



























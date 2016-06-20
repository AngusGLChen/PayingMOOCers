'''
Created on Sep 14, 2015

@author: Angus
'''

import mysql.connector
from sets import Set

def SeekEngagedLearners():
    
    engaged_learner_set = Set()
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    sql_query = "SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
        
    for result in results:
        course_user_id = result[0]
        engaged_learner_set.add(course_user_id)
        
    print "The number of engaged learners is: " + str(len(engaged_learner_set))
    
    return engaged_learner_set


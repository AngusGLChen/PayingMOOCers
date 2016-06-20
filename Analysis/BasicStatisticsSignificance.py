'''
Created on Sep 10, 2015

@author: Angus
'''

import mysql.connector
import scipy
from scipy.stats import mannwhitneyu

def ToComputeAverage(array):
    
    sum = 0    
    for element in array:
        sum += float(element)
    sum /= float(len(array))
    print "The average value is:" + str(round(sum,2))

def BonusExerciseTest(cursor):
    
    # To retrieve the list of the BE learner
    learner_set = set()
    non_learner_set = set()
    
    sql_query = "SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE"
    non_sql_query = "SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE"
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        learner_set.add(result[0])
    
    cursor.execute(non_sql_query)
    results = cursor.fetchall()
    for result in results:
        non_learner_set.add(result[0])
    
    print "The number of BE vs. Non-BE learners is: " + str(len(learner_set)) + "\t" + str(len(non_learner_set))
    
    # To query and perform the significant analysis
    array = []
    non_array = []
    
    sql_query = "SELECT SUM(observations.duration) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE GROUP BY observations.course_user_id"
    non_sql_query = "SELECT SUM(observations.duration) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE GROUP BY observations.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id AND assessments.grade!=0 GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id AND assessments.grade!=0 GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id)/T2.Num_attempts AS Accuracy FROM assessments, (SELECT assessments.course_user_id, COUNT(assessments.assessment_id) AS Num_attempts FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id ) AS T2 WHERE assessments.course_user_id=T2.course_user_id AND assessments.max_grade!=0 GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id)/T2.Num_attempts AS Accuracy FROM assessments, (SELECT assessments.course_user_id, COUNT(assessments.assessment_id) AS Num_attempts FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id ) AS T2 WHERE assessments.course_user_id=T2.course_user_id AND assessments.max_grade!=0 GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(collaborations.collaboration_id) FROM collaborations, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE) AS T1 WHERE collaborations.course_user_id=T1.course_user_id GROUP BY collaborations.course_user_id"
    non_sql_query = "SELECT COUNT(collaborations.collaboration_id) FROM collaborations, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=FALSE) AS T1 WHERE collaborations.course_user_id=T1.course_user_id GROUP BY collaborations.course_user_id"
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        array.append(result[0])
    
    cursor.execute(non_sql_query)
    results = cursor.fetchall()
    for result in results:
        non_array.append(result[0])
    
    print "The number of records: " + str(len(array)) + "\t" + str(len(non_array))   
    
    while len(array) != len(learner_set):
        array.append(0)
    while len(non_array) != len(non_learner_set):
        non_array.append(0)
        
    ToComputeAverage(array)
    ToComputeAverage(non_array)
    
    print scipy.stats.mannwhitneyu(array,non_array)
    
def DedicatedBonusExerciseTest(cursor):
    
    # To retrieve the list of the Dedicated BE/Non-BE learner
    learner_set = set()
    non_learner_set = set()
    
    sql_query = "SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE"
    non_sql_query = "SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE"
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        learner_set.add(result[0])
    
    cursor.execute(non_sql_query)
    results = cursor.fetchall()
    for result in results:
        non_learner_set.add(result[0])
    
    print "The number of Dedicated BE vs. Non-BE learners is: " + str(len(learner_set)) + "\t" + str(len(non_learner_set))
    
    # To query and perform the significant analysis
    array = []
    non_array = []
    
    sql_query = "SELECT SUM(observations.duration) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE GROUP BY observations.course_user_id"
    non_sql_query = "SELECT SUM(observations.duration) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE GROUP BY observations.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id AND assessments.grade!=0 GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id) FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id AND assessments.grade!=0 GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(assessments.assessment_id)/T2.Num_attempts AS Accuracy FROM assessments, (SELECT assessments.course_user_id, COUNT(assessments.assessment_id) AS Num_attempts FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id ) AS T2 WHERE assessments.course_user_id=T2.course_user_id AND assessments.max_grade!=0 GROUP BY assessments.course_user_id"
    non_sql_query = "SELECT COUNT(assessments.assessment_id)/T2.Num_attempts AS Accuracy FROM assessments, (SELECT assessments.course_user_id, COUNT(assessments.assessment_id) AS Num_attempts FROM assessments, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE) AS T1 WHERE assessments.course_user_id=T1.course_user_id GROUP BY assessments.course_user_id ) AS T2 WHERE assessments.course_user_id=T2.course_user_id AND assessments.max_grade!=0 GROUP BY assessments.course_user_id"
    
    sql_query = "SELECT COUNT(collaborations.collaboration_id) FROM collaborations, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=TRUE) AS T1 WHERE collaborations.course_user_id=T1.course_user_id GROUP BY collaborations.course_user_id"
    non_sql_query = "SELECT COUNT(collaborations.collaboration_id) FROM collaborations, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\" AND global_user.bonus_mark=TRUE AND global_user.dedicated_bonus_mark=FALSE) AS T1 WHERE collaborations.course_user_id=T1.course_user_id GROUP BY collaborations.course_user_id"
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        array.append(result[0])
    
    cursor.execute(non_sql_query)
    results = cursor.fetchall()
    for result in results:
        non_array.append(result[0])
    
    print "The number of records: " + str(len(array)) + "\t" + str(len(non_array))   
    
    while len(array) != len(learner_set):
        array.append(0)
    while len(non_array) != len(non_learner_set):
        non_array.append(0)
    
    ToComputeAverage(array)
    ToComputeAverage(non_array)
    
    print scipy.stats.mannwhitneyu(array,non_array)

def BasicStatisticsSignificance():
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    #####################################
    # For BE learners vs. Non-BE learners
    BonusExerciseTest(cursor)
    
    #####################################
    # For Dedicated BE learners vs. Non-BE learners
    DedicatedBonusExerciseTest(cursor)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


####################################################    
BasicStatisticsSignificance()
print "Finished."


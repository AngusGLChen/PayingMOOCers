'''
Created on Sep 11, 2015

@author: Angus
'''

import mysql.connector

def ToComputeCompletionRate(completed_learner_set, country_learner_set):
    
    num_completed_learners = 0
    for learner in country_learner_set:
        if learner in completed_learner_set:
            num_completed_learners += 1
    completionRate = num_completed_learners / float(len(country_learner_set))
    return round(completionRate,4)

def ToSeekComplter(cursor):
    
    completed_learner_set = set()
    sql_query = "SELECT course_user.course_user_id FROM course_user, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\") AS T WHERE course_user.course_user_id=T.course_user_id AND course_user.certificate_status=\"downloadable\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        completed_learner_set.add(result[0])
        
    print "The number of complted learners is: " + str(len(completed_learner_set))
    return completed_learner_set

def CountryAnalysis(path, cursor, completers):
    
    # 1. To gather learners' country information
    country_learner_map = {}
    num_learner = 0
    sql_query = "SELECT global_user.course_user_id, user_pii.country FROM global_user, user_pii, (SELECT DISTINCT(observations.course_user_id) FROM observations, global_user WHERE observations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\") AS T WHERE global_user.global_user_id=user_pii.global_user_id AND global_user.course_user_id=T.course_user_id AND user_pii.country!=\"NULL\" AND user_pii.country!=\"\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        course_user_id = result[0]
        country = result[1]
        num_learner += 1
        
        if country in country_learner_map.keys():
            country_learner_map[country].add(course_user_id)
        else:
            country_learner_map[country] = set(course_user_id)
    
    print "The number of learners who provided country information is: " + str(num_learner)
        
    # 2. To compute the completion rate for each country group    
    country_completionRate_map = {}
    for country in country_learner_map:
        completionRate = ToComputeCompletionRate(completers, country_learner_map[country])
        country_completionRate_map[country] = completionRate
    
    # 3. To translate the country shorten name into full name
    country_name_map = {}
    match_path = path + "match_countries.csv"
    fp = open(match_path, "r")
    for line in fp:
        shorten_name = line[0:2]
        full_name = str.lower(line[3:len(line)].replace("\n", "").replace("\"","").strip())
        country_name_map[shorten_name] = full_name
    fp.close()
    
    '''
    # 4. To gather the list of developing countries
    developing_set = set()
    developing_path = path + "developing_countries"
    fp = open(developing_path, "r")
    for line in fp:
        country = line.replace("\n", "").strip()
        developing_set.add(country)
    fp.close()
    
    # 5. To gather the list of developed countries
    developed_set = set()
    developed_path = path + "developed_countries"
    fp = open(developed_path, "r")
    for line in fp:
        country = line.replace("\n", "").strip()
        developed_set.add(country)
    fp.close()
    '''
    
    # 4. To gather the list of developed countries
    developed_country_set = set()
    developed_country_path = path + "oecd"
    fp = open(developed_country_path, "r")
    for line in fp:
        country = str.lower(line.replace("\n", "").strip())
        developed_country_set.add(country)
    fp.close()
    
    sorted_country_completionRate_map = sorted(country_completionRate_map.items(), key=lambda d:d[1], reverse=True)
    
    num_developed = 0
    num_developing = 0  
          
    for i in range(len(sorted_country_completionRate_map)):
        
        country_shorten_name = sorted_country_completionRate_map[i][0]       
        country_full_name = country_name_map[country_shorten_name]
        completionRate = sorted_country_completionRate_map[i][1]
        
        '''
        if country_full_name in developed_set:
            num_developed += 1
            print country_full_name + "****" + "\t" + str(completionRate)
        else:
            if country_full_name in developing_set:
                num_developing += 1
                print country_full_name + "*" + "\t" + str(completionRate)
            else:
                print country_full_name + "\t" + str(completionRate)               
        '''
        
        if country_full_name in developed_country_set:
            num_developed += 1
            print country_full_name + "****" + "\t" + str(completionRate)
        else:
            num_developing += 1
            print country_full_name + "*" + "\t" + str(completionRate)
            
        
    print "The numbers of developed vs. developing are:" + str(num_developed) + "\t" + str(num_developing)

def DemographicAnalysis(path):
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    # To gather the list of completed learners
    completed_learner_set = ToSeekComplter(cursor)
    
    #####################################
    # For country
    CountryAnalysis(path, cursor, completed_learner_set)

    

            
        
            
        
        
        
    
    
    
    
    
      
    
    
    
    
    
    
    






####################################################
path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
DemographicAnalysis(path)
print "Finished."

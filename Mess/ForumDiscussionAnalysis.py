'''
Created on Oct 17, 2015

@author: Angus
'''

import mysql.connector
from sets import Set

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def AnalyzeForumDiscussion():
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    sql_query = "SELECT collaborations.collaboration_type, collaborations.collaboration_id, collaborations.collaboration_title, collaborations.collaboration_content, collaborations.collaboration_thread_id, collaborations.collaboration_parent_id FROM collaborations, global_user WHERE collaborations.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\""
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    num_all_question = 0
    question_id_set = set()
    final_id_set = set()
    
    keywords = ["bonus", "1.7", "2.9", "3.9", "4.8", "5.5", "7.6"]
    
    for result in results:
        
        type = result[0]
        collaboration_id = result[1]
        title = str.lower(str(result[2]))
        content = str.lower(str(result[3]))
        
        if "question" in type:
            num_all_question += 1
            
            bonus_mark = False
            
            for keyword in keywords:
                if keyword in title or keyword in content:
                    bonus_mark = True
                    break
            
            if bonus_mark:
                question_id_set.add(collaboration_id)
                final_id_set.add(collaboration_id)
    
    print "The number of all questions is: " + str(num_all_question) 
    print "The number of bonus questions is:" + str(len(question_id_set))
    
    
    # For comment
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    for result in results:
        type = result[0]
        collaboration_id = result[1]
        title = str.lower(str(result[2]))
        content = str.lower(str(result[3]))
        thread_id = result[4]
        parent_id = result[5]
        
        if thread_id in final_id_set:
            final_id_set.add(collaboration_id)
     
    # For reply to comment        
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    for result in results:
        type = result[0]
        collaboration_id = result[1]
        title = str.lower(str(result[2]))
        content = str.lower(str(result[3]))
        thread_id = result[4]
        parent_id = result[5]
        
        if parent_id in final_id_set:
            final_id_set.add(collaboration_id)
            
    print "The number of collaborations is : " + str(len(final_id_set))
    
            

        
    '''
    cnt = 0
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    for result in results:
        type = result[0]
        collaboration_id = result[1]
        title = str.lower(str(result[2]))
        content = str.lower(str(result[3]))
        thead_id = result[4]
        parent_id = result[5]
        
        if collaboration_id in id_set or thead_id in id_set or parent_id in id_set:
            cnt += 1
    
    print cnt
    '''
        


####################################################
AnalyzeForumDiscussion()
print "Finished."
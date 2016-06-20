'''
Created on Oct 19, 2015

@author: Angus
'''

import mysql.connector
import os

def GenerateUserIDFile(path):
    
    email_userId_map = {}
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='EX101x')
    cursor = connection.cursor()
    
    sql_query = "SELECT user_pii.email, user_pii.global_user_id FROM user_pii, global_user WHERE user_pii.global_user_id=global_user.global_user_id AND global_user.course_id=\"DelftX/EX101x/1T2015\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
        
    for result in results:
        email = result[0]
        id = result[1]
        email_userId_map[email] = id
        
    output_path= path + "id_file"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output = open(output_path, "w")
    
    input_path = path + "bonus_email_map.txt"
    input = open(input_path, "r")
    for line in input:
        array = line.replace("\n", "").split(",")
        email = array[0]
        week = array[1]
        id = array[2]
        
        if email in email_userId_map.keys():
            output.write(str(email_userId_map[email]) + "," + week + "," + id + "\n")
        else:
            output.write("Unmatched" + "," + week + "," + id + "\n")
    
    
####################################################
course_path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
GenerateUserIDFile(course_path)
print "Finished"

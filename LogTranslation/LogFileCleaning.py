'''
Created on Sep 8, 2015

@author: Angus
'''

import os
import json
    
def LogFileClearning(path):
    
    files = os.listdir(path)
    for file in files:
        # Processing events log data
        if "events" in file:
            print file
        
            # Output clear-out file
            clear_out_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/Clear-out/EX101x/" + file
            if os.path.isfile(clear_out_path):
                os.remove(clear_out_path)
        
            clear_out_file = open(clear_out_path, 'wb')
        
            fp = open(path + "/" + file,"r")   
            for line in fp:
                jsonObject = json.loads(line)            
                if jsonObject["context"]["course_id"] == "DelftX/EX101x/1T2015":
                    clear_out_file.write(line)
                
            clear_out_file.close()         


####################################################    
path = "/Volumes/NETAC/EdX/EX101x/Logs/"
LogFileClearning(path)
print "Finished."       

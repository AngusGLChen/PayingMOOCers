'''
Created on Jul 24, 2015

@author: Angus
'''

import os
import LogTranslation.UserMode
import LogTranslation.CollaborationMode
import LogTranslation.SubmissionMode
import LogTranslation.ObservationMode
import LogTranslation.SurveyMode

course_path = "/Volumes/NETAC/EdX/Clear-out/EX101x/"
'''
# User mode
if os.path.isdir(course_path):
    LogTranslation.UserMode.user_mode(course_path)        

# Collaboration mode
if os.path.isdir(course_path):
    LogTranslation.CollaborationMode.collaboration_mode(course_path)

# Submission mode
if os.path.isdir(course_path):
    LogTranslation.SubmissionMode.submission_mode(course_path)    
'''
# Observation mode
if os.path.isdir(course_path):
    LogTranslation.ObservationMode.observation_mode(course_path)
'''
# Survey mode
if os.path.isdir(course_path):
    LogTranslation.SurveyMode.survey_mode(course_path)
'''
print "All finished."

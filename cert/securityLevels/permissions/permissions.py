#!/usr/bin/python2
import os
import sys
import re

file_permission = os.path.abspath("permissions.txt").replace("toyapps/out", "cert/securityLevels/permissions")

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

    
def _clean_line(line):
    return re.sub(r'\s+', '', line)

def get_category_permission(method):
    try:
        file_ptr = open(file_permission, 'r')
    except IOError, e:
        die(str(e))

    for line in file_ptr:
        line = _clean_line(line)
        if line.startswith("Permission:android.permission."):
            current_category = line.split("Permission:android.permission.")[1]
        else:
            if line.startswith(method):
                return current_category
    return method

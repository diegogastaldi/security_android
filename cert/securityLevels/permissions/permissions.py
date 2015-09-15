#!/usr/bin/python2
import os
import sys

file_permission = os.path.abspath("permissions.txt").replace("toyapps/out", "cert/securityLevels/permissions")

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)


def get_category_permission(method):
    print(method)
    try:
        file_ptr = open(file_permission, 'r')
    except IOError, e:
        die(str(e))

    for line in file_ptr:
        if line.startswith("Permission:android.permission."):
            current_category = line.split("Permission:android.permission.")[1]
        else:
            if line.startswith(method):
                print(current_category)
                return current_category
    return method

def main():
    print(get_category_permission("<android.location.LocationManager: android.location.Location getLastKnownLocation(java.lang.String)>"))

main()
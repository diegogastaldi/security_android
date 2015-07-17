#!/usr/bin/python2
import sys
import traceback
from pprint import pprint
import re
import os

file_assign_levels = os.path.abspath("assign-levels.txt").replace("toyapps/out", "cert/securityLevels")
file_security_levels = os.path.abspath("security-levels.txt").replace("toyapps/out", "cert/securityLevels")

class Check_levels(object):

    _relations = []
    _levels = []    
    _levels_methods = []

    def __init__(self):
        self._parse_security_levels()
        self._parse_assign_levels()

    def _resolve_levels(slef, tuple_list):
        result = "\n" + "Security Problems: " + "\n"
        return result

    def _get_level(self, string):
        for level in self._levels:
            if (string.find("level='" + level + "'") != -1):
                return level
        if (string.find("level=None") != -1):
            return "None"
        self._die(string + " contain a unknown level") 
        
        
    def check_levels(self, flows):
        tuple_list = []
        # Each element is a sink with its possible sources
        for flow in flows["Taints"]: 
            if (flow.startswith("Sink") or flow.startswith("Src")):
                current_levels = self._get_level(flow)
            else:
                if flow.startswith("Intent"):
                    current_levels = "None"
                else:
                    die("Unknown Type : " + flow)
            for src in flows["Taints"][flow]:
                t = (self._get_level(src), current_levels)
                tuple_list.append(t)
        pprint(tuple_list)
        return self._resolve_levels(tuple_list)

    def _die(self, text): 
        sys.stderr.write(text + "\n")
        sys.exit(1)
    
    def _clean_line(self, line):
        return re.sub(r'\s+', '', line)
        
    def _parse_security_levels(self): 
        try:
            file_ptr = open(file_security_levels, 'r')
        except IOError, e:
            self.die(str(e))
    
        for line in file_ptr:
            if line.startswith("#"):
                continue
            if (line.count("<=") != 1):
                file_ptr.close()    
                self.die(file_security_levels + ": each line must have a <=")   
            line = self._clean_line(line)
            current_levels = line.split("<=")
            self._levels.extend(current_levels)
            levels_tuple = current_levels[0], current_levels[1]
            self._relations.append(levels_tuple)
        self._relations = set(self._relations)
        self._levels = set(self._levels)
        file_ptr.close()
        return True;

    def _parse_assign_levels(self): 
        try:
            file_ptr = open(file_assign_levels, 'r')
        except IOError, e:
            self.die(str(e))
    
        for line in file_ptr:
            if line.startswith("#"):
                continue
            if (line.count("->") != 1):
                file_ptr.close()
                
            line = self._clean_line(line)
            current_method = line.split("->")
            levels_tuple = current_method[0], current_method[1]
            if not (levels_tuple[1] in self._levels):
                file_ptr.close()
                self._die(file_assign_levels + ": " + levels_tuple[1] + " is an unknown level in security-levels.txt") 
            self._levels_methods.append(levels_tuple)

    def assign_level(self, method):
        method = self._clean_line(method)
        for current_method in self._levels_methods:
            if current_method[0] == method:
                return current_method[1]
        return None

    def __repr__(self):
        return "Levels: " + str(self._levels) + "\n" + "Relations: " + str(self._relations) + "\n" + "Levels Methods: " + str(self._levels_methods) + "\n"

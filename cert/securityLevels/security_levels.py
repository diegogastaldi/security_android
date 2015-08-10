#!/usr/bin/python2
from securityLevels.partial_order import *
import sys
import traceback
from pprint import pprint
import re
import os

file_assign_levels = os.path.abspath("assign-levels.txt").replace("toyapps/out", "cert/securityLevels")
file_security_levels = os.path.abspath("security-levels.txt").replace("toyapps/out", "cert/securityLevels")

class Check_levels(object):
    _order = Partial_order()

    def __init__(self):
        self._parse_security_levels()
        self._parse_assign_levels()
    
    def _get_level(self, string):
        string = self._clean_line(string)
        for level in self._order.get_levels():
            if (string.find("level='" + level + "'") != -1):
                return level
        for var in self._order.get_vars():
            if (string.find("level='" + var + "'") != -1):
                return var
        if (string.find("intent_id")):
            var = (string.split("intent_id='")[1]).split("'")[0]
            self._order.add_var(var)
            return var
        self._die(string + " contain a unknown level") 
        
    def check_levels(self, flows):
        tuple_list = []
        # Each element is a sink with its possible sources
        for flow in flows["Taints"]: 
            if (flow.startswith("Sink") or flow.startswith("Src") or flow.startswith("Intent")):
                current_levels = self._get_level(flow)
            else:
                die("Unknown Type : " + flow)
            for src in flows["Taints"][flow]:
                t = (self._get_level(src), current_levels)
                tuple_list.append(t)
        #Parameters to algorithm
        pprint("tuple_list")
        pprint(tuple_list)
        pprint(self._order)
        return set() #tract_const_finite_semilattice(tuple_list, self._order.get_vars(), self._order.get_relations())

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
            levels_tuple = current_levels[0], current_levels[1]

            self._order.add_relation(levels_tuple)
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
            if not (levels_tuple[1] in self._order.get_levels()):
                file_ptr.close()
                self._die(file_assign_levels + ": " + levels_tuple[1] + " is an unknown level in security-levels.txt") 
            self._order.add_methods(levels_tuple)

    def assign_level(self, method):
        return self._order.assign_level(self._clean_line(method))
#!/usr/bin/python2
from securityLevels.partial_order import *
from securityLevels.tract_constr_finite_slattice import *
import sys
import traceback
from pprint import pprint
import re
import os
from securityLevels.permissions.permissions import *

file_assign_levels = os.path.abspath("assign-levels.txt").replace("toyapps/out", "cert/securityLevels")
file_security_levels = os.path.abspath("security-levels.txt").replace("toyapps/out", "cert/securityLevels")
file_exceptions = os.path.abspath("exceptions.txt").replace("toyapps/out", "cert/securityLevels")

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

class Check_levels(object):
    _order = Partial_order()
    _exceptions = set()

    def __init__(self, from_file = True):
        if (not self._parse_security_levels()):
            die("The order in " + file_security_levels + " is not a partial order")
        if from_file:
            self._parse_assign_levels()
            self._parse_exceptions()

    def get_levels_order(self):
        return self._order.get_levels()

    def get_vars_order(self):
        return self._order.get_vars()

    def _get_level(self, string, is_sink = True):
        string = self._clean_line(string)
        for level in self._order.get_levels():
            if (string.find("level='" + level + "'") != -1):
                return level
        for var in self._order.get_vars():
            if ((string.find("level='" + var + "'") != -1) or ((string.find("intent_id='" + var + "'") != -1))):
                return var
        if (is_sink and ((string.find("intent_id")) != -1)):
            var = (string.split("intent_id='")[1]).split("'")[0]
            self._order.add_var(var)
            return var
        die(string + " contain a unknown level") 
        
    def show_security_levels(self, sl):
        if (sl["correct"] == True):
            string = "Applications don't have security problems. \n Assigned security levels are: \n"
        else:
            string = "Applications have security problems. \n The methods are: \n"
        res = str(sl ["p"]).split(", ")
        for x in xrange(0,len(res)):
            string = string + "  " + res[x] + "\n"
        return string

    def check_levels(self, flows):
        inequalities = list()
        # Each element is a sink with its possible sources
        for flow in flows["Taints"]: 
            if (flow.startswith("Sink") or flow.startswith("Intent") or flow.startswith("Src")):
                current_sink_level = self._get_level(flow)
                current_sink_method = flow
            else:
                die("Unknown Type of Sink: " + flow)
            for src in flows["Taints"][flow]: 
                if (src.startswith("Src")): 
                    current_src = (src.split("Src: ")[1].split("',")[0], self._get_level(src, False))
                    if (current_sink_method.startswith("Intent")):
                        current_sink = (current_sink_method, current_sink_level)
                    else:
                        if (current_sink_method.startswith("Sink")):    
                            current_sink = (current_sink_method.split("Sink: ")[1].split("',")[0], current_sink_level)
                        else:
                            current_sink = (current_sink_method.split("Src: ")[1].split("',")[0], current_sink_level)                    
                    
                    tupl = (current_src, current_sink)
                    inequalities.append(tupl)                    
                else:
                    die("Unknown Type of Src: " + src)                    
        result = tract_const_finite_semilattice(inequalities, self._order, self._exceptions)
        return self.show_security_levels(result)
    
    def _clean_line(self, line):
        return re.sub(r'\s+', '', line)
        
    def _parse_security_levels(self): 
        try:
            file_ptr = open(file_security_levels, 'r')
        except IOError, e:
            die(str(e))
        relations = set()
        for line in file_ptr:
            if line.startswith("#") or line.startswith("\n"):
                continue
            if (line.count("<=") != 1):
                file_ptr.close()    
                die(file_security_levels + ": each line must have a <=")   
            line = self._clean_line(line)
            current_levels = line.split("<=")
            levels_tuple = current_levels[0], current_levels[1]

            relations.add(levels_tuple)
        file_ptr.close()
        return self._order.add_relations(relations)

    def _parse_assign_levels(self): 
        try:
            file_ptr = open(file_assign_levels, 'r')
        except IOError, e:
            self.die(str(e))
        for line in file_ptr:
            if line.startswith("#") or line.startswith("\n"):
                continue    
            if (line.count("->") != 1):
                file_ptr.close()
                die(file_assign_levels + ": each line must have a ->")   
            line = self._clean_line(line)
            current_method = line.split("->")
            levels_tuple = current_method[0], current_method[1]
            
            self._order.add_methods(levels_tuple)

    def _parse_exceptions(self):
        try:
            file_ptr = open(file_exceptions, 'r')
        except IOError, e:
            die(str(e))
    
        for line in file_ptr:
            if line.startswith("#") or line.startswith("\n"):
                continue
            pprint(line)
            if (line.count("->") != 1):
                file_ptr.close()
                die(file_exceptions + ": each line must have a ->")   
            line = self._clean_line(line)
            current_method = line.split("->")
            if ((get_category_permission(current_method[0]) != current_method[0]) and (get_category_permission(current_method[1]) != current_method[1])):
                exc_tuple = current_method[0], current_method[1]
                self._exceptions.add(exc_tuple)
            else: 
                pprint("Methods in the exceptions not found. Exceptions not added")

    def add_exception(self, exc):
        exc_tuple = self._clean_line(exc[0]), self._clean_line(exc[1])
        if ((get_category_permission(exc_tuple[0]) != exc_tuple[0]) and (get_category_permission(exc_tuple[1]) != exc_tuple[1])):
            self._exceptions.add(exc_tuple)
            return True
        else:
            return False

    def selection_assign_levels(self, tuples): 
        for t in tuples:
            if t[1] != None:
                self._order.add_methods(t)

    def assign_level(self, method):
        return self._order.assign_level(self._clean_line(method))

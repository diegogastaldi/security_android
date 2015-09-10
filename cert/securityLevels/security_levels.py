#!/usr/bin/python2
from securityLevels.partial_order import *
from securityLevels.tract_constr_finite_slattice import *
import sys
import traceback
from pprint import pprint
import re
import os

file_assign_levels = os.path.abspath("assign-levels.txt").replace("toyapps/out", "cert/securityLevels")
file_security_levels = os.path.abspath("security-levels.txt").replace("toyapps/out", "cert/securityLevels")

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

class Check_levels(object):
    _order = Partial_order()

    def __init__(self, from_file = True):
        self._parse_security_levels()
        if from_file:
            self._parse_assign_levels()

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
            if (string.find("level='" + var + "'") != -1):
                return var
        if (is_sink and string.find("intent_id")):
            var = (string.split("intent_id='")[1]).split("'")[0]
            self._order.add_var(var)
            return var
        self._die(string + " contain a unknown level") 
        
    def show_security_levels(self, sl, im):
        if (sl["correct"] == True):
            return "Applications don't have security problems. \n Assigned security levels are: " + str(sl ["p"])
        else:
            string = "Applications have security problems. \n The methods are: \n"
            while len(im):
                tm = im.pop()
                string = string + str(tm) + "\n"
            return string

    def check_levels(self, flows):
        inequalities_levels = list()
        inequalities_methods = list()
        # Each element is a sink with its possible sources
        for flow in flows["Taints"]: 
            if (flow.startswith("Sink") or flow.startswith("Intent") or flow.startswith("Src")):
                current_sink_level = self._get_level(flow)
                current_sink_method = flow
            else:
                die("Unknown Type of Sink: " + flow)
            for src in flows["Taints"][flow]: 
                if (src.startswith("Src")):
                    current_src_level = self._get_level(src, False)
                    current_src_method = src
                    t_l = (current_src_level, current_sink_level)
                    inequalities_levels.append(t_l)
                    t_m = (current_src_method, current_sink_method)
                    inequalities_methods.append(t_m)                    
                else:
                    die("Unknown Type of Src: " + src)                    
        #Parameters to algorithm
        result = tract_const_finite_semilattice(inequalities_levels, self._order)
        return self.show_security_levels(result, inequalities_methods)
    
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
                die(file_security_levels + ": each line must have a <=")   
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
                self.die(file_security_levels + ": each line must have a ->")   
            line = self._clean_line(line)
            current_method = line.split("->")
            levels_tuple = current_method[0], current_method[1]
            
            self._order.add_methods(levels_tuple)

    def selection_assign_levels(self, tuples): 
        for t in tuples:
            if t[1] != None:
                self._order.add_methods(t)
        pprint(self._order)

    def assign_level(self, method):
        return self._order.assign_level(self._clean_line(method))
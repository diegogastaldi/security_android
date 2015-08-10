#!/usr/bin/python2
from pprint import pprint
class Partial_order(object):

    def __init__(self):
        self._relations = set()
        self._level_method = set()
        self._levels = set()
        self._vars = set()
        
    def add_level(self, level):
        self._levels.add(level)

    def get_levels(self):
        return self._levels

    def add_relation(self, relation):
        self._relations.add(relation)
        self.add_level(relation[0])
        self.add_level(relation[1])

    def get_relations(self):
        return self._relations

    def add_methods(self, method):
        self._level_method.add(method)

    def add_var(self, var):
    	self._vars.add(var)

    def get_vars(self):
    	return self._vars

    def assign_level(self, method):
        for current_method in self._level_method:
            if current_method[0] == method:
                return current_method[1]
        # This method don't have a level assigned
        self._vars.add(method)
        return method

    def __repr__(self):
        return "Levels: " + str(self._levels) + "\n" + "Relations: " + str(self._relations) + "\n" + "Levels Methods: " + str(self._level_method) + "\n" + "Vars: " + str(self._vars) + "\n"
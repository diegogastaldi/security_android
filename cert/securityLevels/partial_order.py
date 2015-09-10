#!/usr/bin/python2
from pprint import pprint
import sys

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

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
        if not (method[1] in self._levels):
            die(str(method[1]) + ": is an unknown level in add_methods") 
        self._level_method.add(method)
        self._vars.remove(method[0])

    def add_var(self, var):
        self._vars.add(var)

    def get_vars(self):
        return self._vars
 
    def bottom(self):
        bottom = list(self._relations)[0][0]
        for relation in self._relations:
            if (bottom == relation[1]):
                bottom = relation[0]
        return bottom

    def supremum(self, levels):
        for l in levels:
            if not (l in self._levels):
                die("Supremum error")
        greater_levels = {}
        # Greater for each level
        for level in levels:
            greater_levels[level] = set()
            greater_levels[level].add(level)
            for rel in self._relations:
                if level == rel[0]:
                    greater_levels[level].add(rel[1])
        greater = set()
        greater = greater_levels[levels.pop()]
        for level in levels:
            greater = greater.intersection(greater_levels[level])
        aux_greater = greater.copy()
        for g in aux_greater:
            for rel in self._relations:
                if ((g == rel[1]) and (rel[0] != g) and (rel[0] in greater)):
                    greater.remove(g)
                    break

        if len(greater) != 1:
            die("Supremum error.")
        return greater.pop()

    def assign_level(self, method):
        for current_method in self._level_method:
            if current_method[0] == method:
                return current_method[1]
        # This method don't have a level assigned
        self._vars.add(method)
        return method

    def __repr__(self):
        return "Partial Order: \n Levels: " + str(self._levels) + "\n" + "Relations: " + str(self._relations) + "\n" + "Levels Methods: " + str(self._level_method) + "\n" + "Vars: " + str(self._vars) + "\n"
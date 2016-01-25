#!/usr/bin/python2
from collections import *
from pprint import pprint
import re

# Inequalities
ilist = {} # dict('inequality', inserted)

# Vars
clist = {} # dict('vars', 'inequality' = [])

# Inequalities not stisfied in p
ns = set()

# Current interpretation
p = {} # dict('var', 'level')

# inequalities with a variable to right
c_var = set()

def clean_line(line):
    return re.sub(r'\s+', '', line)

def check(inequality, order, exceptions):
    src = inequality[0][1]
    sink = inequality[1][1]

    if src in order.get_vars():
        level_src = p[src]
    else:
        level_src = inequality[0][1]
    if sink in order.get_vars():
        level_sink = p[sink]
    else:
        level_sink = inequality[1][1]

    return (((level_src, level_sink) in order.get_relations()) or ((clean_line(inequality[0][0]), clean_line(inequality[1][0])) in exceptions))

def initialize(inequalities, order, exceptions):
    bottom = order.bottom()
    for var in order.get_vars():
        p[var] = bottom
        clist[var] = set()
    for inequality in inequalities:
        ilist[inequality] = False
        if (inequality[1][1] in order.get_vars()):
            c_var.add(inequality)
            clist[inequality[1][1]].add(inequality)
        if (inequality[0][1] in order.get_vars()):
            clist[inequality[0][1]].add(inequality)
    for inequality in c_var:
        if not check(inequality, order, exceptions):
            ns.add(inequality)
            ilist[inequality] = True

# removes the head element from ns and returns it after setting the field inserted to false 
def pop(): 
    inq = ns.pop()
    ilist[inq] = False
    return inq

# inserts a inequality at the front of ns, updating inserted field (if inserted is true, insert does nothing)
def insert(i):
    if ilist[i] == False:
        ilist[i] = True
        ns.add(i)

# remove arbitrary i from ns 
def drop(i):
    if ilist[i] == True:
        ilist[i] = False
        ns.remove(i)

def tract_const_finite_semilattice(inequalities, order, exceptions):
    initialize(inequalities, order, exceptions)
    while len(ns):
        (t, b) = pop()
        p[b[1]] = order.supremum(set([t[1], p[b[1]]]))
        for inequality in clist[b[1]]:
            if not check(inequality, order, exceptions):
                insert(inequality)
            else:
                drop(inequality)
    out = {}
    for inequality in ilist:
        if not check(inequality, order, exceptions):
            out ["correct"] = False
            out ["p"] = inequality
            return out
    out ["correct"] = True
    out ["p"] = p
    return out
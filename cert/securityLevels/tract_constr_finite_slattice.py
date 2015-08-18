#!/usr/bin/python2
from collections import *
from pprint import pprint

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

def check(inequality, order):
    left = inequality[0]
    right = inequality[1] 
    if left in order.get_vars():
        level_left = p[left]
    else:
        level_left = left
    if right in order.get_vars():
        level_right = p[right]
    else:
        level_right = right
    return (level_left, level_right) in order.get_relations()

def initialize(inequalities, order):
    bottom = order.bottom()
    for var in order.get_vars():
        p[var] = bottom
        clist[var] = set()
    for inequality in inequalities:
        ilist[inequality] = False
        if (inequality[1] in order.get_vars()):
            c_var.add(inequality)
            clist[inequality[1]].add(inequality)
        if (inequality[0] in order.get_vars()):
            clist[inequality[0]].add(inequality)
    for inequality in c_var:
        if not check(inequality, order):
            ns.add(inequality)
            ilist[inequality] = True

# removes the head element from ns and returns it after setting the field inserted to false 
def pop(): 
    inq = ns.pop()
    ilist[inq] = False
    return inq

# inserta a inequality at the front of ns, updating inserted field (if inserted is true, insert does nothing)
def insert(i):
    if ilist[i] == False:
        ilist[i] = True
        ns.add(i)

# remove arbitrary i from ns 
def drop(i):
    if ilist[i] == True:
        ilist[i] = False
        ns.remove(i)

def tract_const_finite_semilattice(inequalities, order):
    pprint(order)
    initialize(inequalities, order)
    while len(ns):
        (t, b) = pop()
        p[b] = order.supremum(set([t, p[b]]))
        for inequality in clist[b]:
            if not check(inequality, order):
                insert(inequality)
            else:
                drop(inequality)
    for inequality in ilist:
        if not check(inequality, order):
            return "Error"
    return p
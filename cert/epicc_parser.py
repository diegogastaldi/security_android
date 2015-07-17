#!/usr/bin/python2
###############################################################################
# Copyright (c) 2014 Carnegie Mellon University
# Distributed under the terms of the BSD-style license found in license.txt.
# 
# Contributors: Will Klieber
###############################################################################

import sys
import os 
#import xml.etree.ElementTree as ET
import subprocess
from collections import *
from pprint import pprint
from OrderedSet import OrderedSet
from collections import OrderedDict
import re
import pdb

stop = pdb.set_trace

def die(text): 
    sys.stderr.write(text + "\n")
    sys.exit(1)

class LineReader:
    """Reads a file line-by-line."""
    def __init__(self, file):
        self.file = file
        self.cur = None
        self.line_num = 0
        self.advance()

    def advance(self):
        self.cur = self.file.readline()
        self.line_num += 1

    def consume_line(self):
        ret = self.cur
        self.advance()
        return ret

    def close(self):
        self.file.close()

    def is_eof(self):
        return len(self.cur) == 0

class EpiccException(Exception):
    pass

def process_intent(infile, strip_intent_id=False): # (infile -> linea corriente, strip_intent_id=as_dict) -> llamada
    src_func = infile.consume_line()[4:].strip() # corta la linea, le saca los primero 4 y luego remueve los espacios en blanco -> linea despues de ICC
    curline = infile.consume_line() # siguiente linea
    if not re.match("Intent value: [0-9]* possible value\(s\):", curline): # re expre reg match con curline
        if curline.strip() == "No value found.":  # TODO: Find out what this means.
            return [src_func, [], []] 
        elif curline.strip() == "Found top element":
            return [src_func, [], [{'Top':True}]]
        elif curline.startswith("Type: "): # Type del intent
            return "IntentFilter" # si no tiene definida la accion y arranca indicando el tipo
        else:
            raise EpiccException("Unrecognized line: '%s'" % (curline.strip(),))
    ret = []
    intent_id = set()
    while True:
        curline = infile.consume_line()
        if len(curline.strip()) == 0: # linea de longitud cero
            break
        if curline.strip() == 'No field set':
            ret.append({})
            continue
        # Note: ord("[")==0x5b, ord("]")==0x5d
        regex_one =  "([A-Za-z]+): (\\x5b[^\\x5d]*\\x5d|[^\\x5d\\x5b, ]*)[,\n] *" # match con extra??
        m = re.match("^ *(" + regex_one + ")*[\n]?$", curline)
        if m == None:
            intent = "ERROR: Unrecognized line: " + curline.strip()
        else:
            m = re.findall(regex_one, curline) # extra
            intent = {}
            for (key, val) in m:
                if val.startswith("["):
                    assert(val.endswith("]"))
                    val = val[1:-1].split(", ") # remueve corchetes y las comas
                    if key == "Extras":
                        new_val = []
                        for ex in val: # extra es una lista
                            if ex.startswith("newField_"):
                                intent_id.add(ex) # id del intent
                                if not strip_intent_id:
                                    new_val.append(ex)
                            else:
                                new_val.append(ex) # secret 
                        val = new_val
                intent[key] = val # intent es un diccionario que tiene como clave a extra (en los ejemplos) y valor es lo que tiene dentro de los corchetes
        #ret.append(curline)
        ret.append(intent) # ret es una lista de intent
    return (src_func, sorted(intent_id), ret) # (funcion fuente, intent_id ordenada, intents)

def parse_epicc(filename, as_dict=False): # as_dict es llamado con true
    try:
        if (filename == '-'):
            file_ptr = sys.stdin # entrada consola
        else:
            file_ptr = open(filename, 'r') # abre el archivo .epicc en modo lectura
    except IOError, e:
        die(str(e))
    infile = LineReader(file_ptr) # Reads a file line-by-line
    ret = []
    pkg_name = ""
    while not infile.is_eof(): # mientras no se termine el archivo
        if infile.cur.startswith("  - "): # cur avanza la linea - cuando arranca con "-" ver archivos .epicc -> los ICC
            try:
                intent = process_intent(infile, strip_intent_id=as_dict) # (funcion fuente, intent_id ordenada, intents)
                if intent != "IntentFilter":
                    ret.append(intent)
            except EpiccException as e:
                die("Error parsing %s:\n%s" % (filename, str(e)))
        else:
            if pkg_name == "":
                m = re.match("^Manifest file for ([A-Za-z0-9_.$]+) version .*", infile.cur)
                if m:
                    pkg_name = m.group(1) 
            infile.consume_line()
    if as_dict:
        ret = epicc_to_dict(ret)
    return (pkg_name, ret) # ret diccionario con funcion, conjunto ordenado de intents y lista de intents (key: ids)

def epicc_to_dict(epicc):
    d = {}
    for (func_loc, intent_ids, intent_info) in epicc:
        if len(intent_ids) == 0:
            intent_ids = ["*"]
        if len(intent_ids) > 1:
            die("Error: Intent does not have exactly one ID!\n")
        d.setdefault(intent_ids[0], [])
        d[intent_ids[0]].extend(intent_info)
    return d

if __name__ == "__main__":
    import json
    def main():
        filename = sys.argv[1]
        ret = parse_epicc(filename)
        ret_json = json.dumps(ret, sort_keys=True, indent=4, separators=(',', ': '))
        #pprint(ret)
        print(ret_json)
    main()

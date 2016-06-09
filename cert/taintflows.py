#!/usr/bin/python2
###############################################################################
# Copyright (c) 2014 Carnegie Mellon University
# Distributed under the terms of the BSD-style license found in license.txt.
# 
# Contributors: Will Klieber, Lori Flynn, Amar Bhosale
###############################################################################

import sys
import os
import traceback
import xml.etree.ElementTree as ET
import subprocess
from collections import *
from pprint import pprint
from OrderedSet import OrderedSet
from collections import OrderedDict
import re
import pdb # debugger
from epicc_parser import parse_epicc, BCAST_ID
from securityLevels.security_levels import *
from gui.main import *
from gui.out import *

stop = pdb.set_trace

class ComponentType(object):
    Activity = "Activity"
    Service = "Service"
    BroadcastReceiver = "BroadcastReceiver"
    ContentProvider = "ContentProvider"

Flow = namedtuple('Flow', ['src', 'app', 'sink'])
Intent = namedtuple('Intent', ['tx', 'rx', 'intent_id'])
IntentResult = namedtuple('IntentResult', ['i'])
# Modified: New level field.
Src = namedtuple('Src', ['src', 'level'])
Sink = namedtuple('Sink', ['sink', 'level'])
android_pfx = "{http://schemas.android.com/apk/res/android}"
script_path = os.path.dirname(os.path.realpath(__file__))

def die(text):
    sys.stderr.write(text + "\n")
    sys.exit(1)

# Removes Repeated
def uniq_by_str(l):
    ret = []
    hit = set()
    for x in l:
        x_str = str(x)
        if x_str not in hit:
            hit.add(x_str)
            ret.append(x)
    return ret

def flatten(l):
    return [item for sublist in l for item in sublist]

class Glo(object):
    def __init__(self):
        self.mainfest = {}
        self.filter = {}
        self.flows = {}
        self.epicc = {}
        self.match_by_tx = {}
        self.match_by_rx = {}
        self.match_by_tx_id = {}
        self.unsound = False
        self.act_alias_to_targ = {}
glo = Glo()

class IntentFilter(object): 
    def __init__(self, action=None, category=None, mime_type =None):
        self.action = action or []
        self.category = category or []
        self.mime_type = mime_type or []
    
    def __repr__(self):
        return "IntentFilter(action=%r, category=%r, mime_type=%r)" % (self.action, self.category, self.mime_type)

# Modified: When intents, sinks and source are created, we add a level field from input gui or input file.
def find_flows(root, check_levels):
    pkg_name = root.attrib['package']
    ret = []

    for flow in root.findall("flow"):
        sink = flow.find("sink").attrib['method']
        if flow.find("sink").attrib.get('is-intent') == "1":
            intent_id = flow.find("sink").attrib.get('intent-id')
            if (intent_id is None):
                sys.stderr.write("Error: Intent in %s is missing intent-id!\n" % pkg_name)
            sink_component = flow.find("sink").get('component')
            sink_component = None # FIXME: for debugging!
            sink = Intent(tx=(pkg_name, sink_component), rx=None, intent_id=intent_id)
        elif flow.find("sink").attrib.get('is-intent-result') == "1":
            sink_component = flow.find("sink").get('component')
            sink_component = None # FIXME: for debugging!
            sink = IntentResult(Intent(tx=None, rx=(pkg_name, sink_component), intent_id=None))
        else:
            sink = Sink("Sink: " + str(sink), check_levels.assign_level(str(sink)))
        for src_node in flow.findall("source"):
            src = src_node.attrib['method']
            component = None
            if src.startswith("<android.content.Intent:") or ("getIntent" in src):
                component = src_node.attrib['component']
                component = None # FIXME: for debugging!
                src = Intent(tx=None, rx=(pkg_name, component), intent_id=None)
            elif ("@parameter2: android.content.Intent" in src):  # FIXME: only for "android.app.Activity: void onActivityResult" 
                component = src_node.attrib['component']
                component = None # FIXME: for debugging!
                src = IntentResult(Intent(tx=(pkg_name, component), rx=None, intent_id=None))
            else:
                src = Src("Src: " + str(src), check_levels.assign_level(str(src)))
            #FIXME: What if the the source and sinks are in different components?
            ret.append(Flow(src=src, app=pkg_name, sink=sink))
    return ret

def get_epicc_and_filters(tx, rx):
    assert(isinstance(tx, Intent))
    assert(isinstance(rx, Intent))
    ((tx_pkg, tx_comp), tx_id) = (tx.tx, tx.intent_id)
    (rx_pkg, rx_comp) = rx.rx
    try:
        epicc = glo.epicc[tx_pkg][tx_id]
    except KeyError as e:
        if id(tx) not in get_epicc_and_filters.missed:
            get_epicc_and_filters.missed.add(id(tx))
            sys.stderr.write("Missing epicc info for %s, intent_id='%s'\n" % (tx_pkg, tx_id))
        epicc = [{}]
    try:
        filters_by_comp = glo.filter[rx_pkg]
        try:
            filters = filters_by_comp[rx_comp]
        except KeyError as e:
            filters = flatten(filters_by_comp.values())
    except KeyError as e:
        die("Missing manifest (apk) for " + tx_pkg)
    return (epicc, filters)
get_epicc_and_filters.missed = set()

def match_intent_attr(tx, rx):
    assert(isinstance(tx, Intent))
    assert(isinstance(rx, Intent))
    (tx_epicc, filters) = get_epicc_and_filters(tx, rx)
    (rx_pkg, rx_comp) = rx.rx
    ret = []

    def match_intent_subcase(epicc, filt):
        # This method implements the action, category, and data tests described in
        # http://developer.android.com/guide/components/intents-filters.html#Resolution
        # Epicc does not produce URI information, so we ignore the URI tests.
        assert(isinstance(filt, IntentFilter))
        if epicc.get('Top', None) == True:
            return (not glo.unsound)
        def match_any_string(x):
            return (x == '<any_string>') and not glo.unsound
        # Check if the intent is an explicit intent.
        epicc_class = epicc.get('Class', None)
        if epicc_class != None:
            # Lots of false positives here for <any_string>.
            # TODO: Can explicit intents be explicitly designated using an
            # activity alias?  If so, we need to the use information in
            # glo.act_alias_to_targ.
            return ((epicc_class == rx_comp) or match_any_string(epicc_class))
        # Action test
        act = epicc.get('Action', None) or epicc.get('Actions', None)
        if type(act) == str:
            act_set = set([act])
        elif (act is None):
            act_set = set()
        else:
            act_set = set(act)
        act_ok = (
            (((act is None) or match_any_string(act)) and len(filt.action) > 0) or 
            (act_set & set(filt.action)))
        if not act_ok:
            return False
        ############################################################
        # For each category in intent, must be a match in filter.
        # Zero categories in intent, but many in filter: still can be received.
        cat = epicc.get('Categories', None)
        if type(cat) == str:
            cat_set = set([cat])
        elif (cat is None):
            cat_set = set()
        else:
            cat_set = set(cat)
        cat_ok = (
            (cat == None) or any(match_any_string(x) for x in cat_set) or
            ((cat_set & set(filt.category)) == cat_set))
        if not cat_ok:
            return False
        # If glo.unsound, then False negatives returned if <any_string> is
        # intent category EPICC returns and the filter actually matches that
        # category EPICC doesn't process 
        ############################################################
        # TODO: data MIME type
        # An intent filter can declare zero or more data elements. Rules:
        # 1. An intent that contains neither a URI nor a MIME type passes the test only if the filter does not specify any URIs or MIME types.
        # (Can't test for this): 2. An intent that contains a URI but no MIME type (neither explicit nor inferable from the URI) passes the test only if its URI matches per test
        # 3. An intent that contains a MIME type but not a URI passes the test only if the filter lists the same MIME type and does not specify a URI format.
        # 4. (Can't test for last rule, since depends on URI)
        # OUTPUT: com.UCMobile.intl.epicc:Actions: [action_local_share], Data types: [*/*]
        # OUTPUT2: Uxpp.UC.epicc:Package: Uxpp/UC, Class: com/nate/android/nateon/uc3/msg/view/MsgListActivity, Extras: [RoomID, FileType, by, ShareUri, ShareType, ShareData, SearchWord, ShareText], Flags: 67108864

        if False:
            data = epicc.get('Type', None)
            pdb.set_trace()
            if type(data) == str:
                data_set = set([data])
            elif (data is None):
                data_set = set()
            else:
                data_set = set(data)
            data_ok = (
                ((data == None) and len(filter.data)==0) or
                ((data_set & set(filt.data)) == data_set))
            if not data_ok:
                return False
        return True

    for intent in tx_epicc:
        for filt in filters:
            if match_intent_subcase(intent, filt):
                return True
                
    return False

def generate_all_matches():
    for (tx_pkg, intent_list) in glo.epicc.iteritems():
        for (intent_id, epicc) in intent_list.iteritems():
            if intent_id == '*':
                continue
            tx = Intent(tx=(tx_pkg,None), rx=None, intent_id=intent_id)
            for (rx_pkg, filters_by_comp) in glo.filter.iteritems():
                for (comp, filters) in filters_by_comp.iteritems():
                    comp = None # FIXME: for debugging!
                    rx = Intent(tx=None, rx=(rx_pkg,comp), intent_id=None)
                    if match_intent_attr(tx, rx):
                        yield Intent(tx=tx.tx, rx=rx.rx, intent_id=intent_id)

def populate_matches():
    for (pkg, flows) in glo.flows.iteritems():
        pkg_epicc = glo.epicc[pkg]
        for flow in flows:
            if isinstance(flow.sink, Intent):
                intent_id = flow.sink.intent_id
                if (intent_id not in pkg_epicc) and ('*' in pkg_epicc):
                    pkg_epicc[intent_id] = pkg_epicc['*']
    glo.match_by_tx = {}
    glo.match_by_tx_id = {}
    glo.match_by_rx = {}
    for i in OrderedSet(generate_all_matches()): # OrderedSet eliminates duplicates
        glo.match_by_rx.setdefault(i.rx, {}).setdefault(i.tx, []).append(i.intent_id)
        glo.match_by_tx.setdefault(i.tx, {}).setdefault(i.rx, []).append(i.intent_id)
        glo.match_by_tx_id.setdefault((i.tx, i.intent_id), set()).add(i.rx)


def match_flows(half_flows):
    populate_matches()
    src_intents = OrderedSet()
    sink_intents = OrderedSet()
    src_intent_results = OrderedSet()
    sink_intent_results = OrderedSet()
    for flow in half_flows:
        if isinstance(flow.src, Intent):
            src_intents.add(flow.src)
        if isinstance(flow.sink, Intent):
            sink_intents.add(flow.sink)
        if isinstance(flow.src, IntentResult):
            src_intent_results.add(flow.src)
        if isinstance(flow.sink, IntentResult):
            sink_intent_results.add(flow.sink)
    def complete_src_intents(half_flows):
        # For a flow of the form Flow(src, app, sink):
        #   If src is a non-intent source, yield the original flow unchanged.
        #   If src has the form Intent(tx=None,rx,intent_id), find all possible
        #   values for tx, and yield the corresponding flows.
        for flow1 in half_flows:
            if isinstance(flow1.src, Intent): # getIntent
                half_intent = flow1.src
                assert(half_intent.tx == None)
                assert(half_intent.intent_id == None)
                for (tx, intent_ids) in glo.match_by_rx.get(half_intent.rx, {}).iteritems():
                    for intent_id in intent_ids:
                        full_intent = Intent(tx, half_intent.rx, intent_id)
                        assert(full_intent.intent_id != None)
                        yield Flow(src=full_intent, app=None, sink=flow1.sink)
            elif isinstance(flow1.src, IntentResult): # onActivityResult
                half_intent = flow1.src.i
                assert(half_intent.rx == None)
                for (rx, intent_ids) in glo.match_by_tx.get(half_intent.tx, {}).iteritems():
                    for intent_id in intent_ids:
                        full_intent = Intent(half_intent.tx, rx, intent_id)
                        assert(full_intent.intent_id != None)
                        yield Flow(src=IntentResult(full_intent), app=None, sink=flow1.sink)
            else:
                yield flow1
    def complete_sink_intents(half_flows):
        # For a flow of the form Flow(src, comp, sink):
        #   If sink is a non-intent source, yield the original flow unchanged.
        #   If sink has the form Intent(tx,rx=None,intent_id), find all possible
        #   values for rx, and yield the corresponding flows.
        for flow1 in half_flows:
            if isinstance(flow1.sink, Intent): # startActivity
                half_intent = flow1.sink
                assert(half_intent.rx == None)
                tx_id = (half_intent.tx, half_intent.intent_id)
                for rx in glo.match_by_tx_id.get(tx_id, []):
                    full_intent = Intent(half_intent.tx, rx, half_intent.intent_id)
                    assert(full_intent.intent_id != None)
                    yield Flow(src=flow1.src, app=None, sink=full_intent)
            elif isinstance(flow1.sink, IntentResult): # setResult
                half_intent = flow1.sink.i
                assert(half_intent.tx == None)
                for (tx, intent_ids) in glo.match_by_rx.get(half_intent.rx, {}).iteritems():
                    for intent_id in intent_ids:
                        full_intent = Intent(tx, half_intent.rx, intent_id)
                        assert(full_intent.intent_id != None)
                        yield Flow(src=flow1.src, app=None, sink=IntentResult(full_intent))
            else:
                yield flow1
    def is_possible_flow(flow):
        if isinstance(flow.src, Intent) and isinstance(flow.sink, IntentResult):
            if flow.src != flow.sink.i:
                return False
        return True
    ret = half_flows
    ret = complete_src_intents(ret)
    ret = complete_sink_intents(ret)
    ret = filter(is_possible_flow, ret)
    return list(OrderedSet(ret))

def solve_flows(flows):
    intents = OrderedSet()
    intent_results = OrderedSet()
    sources = OrderedSet()
    feedout = {}
    taint = {}
    MySet = OrderedSet
    for flow in flows:
        if isinstance(flow.src, Intent):
            intents.add(flow.src)
        elif isinstance(flow.src, IntentResult):
            intent_results.add(flow.src)
        else:
            assert(isinstance(flow.src, Src))
            sources.add(flow.src)
            taint[flow.src] = MySet([flow.src])
        if isinstance(flow.sink, Intent):
            intents.add(flow.sink)
        elif isinstance(flow.sink, IntentResult):
            intent_results.add(flow.sink)
        else:
            assert(isinstance(flow.sink, Sink))
            taint[flow.sink] = MySet()
        feedout.setdefault(flow.src, OrderedSet())
        feedout[flow.src].add(flow)
    for intent in intents | intent_results:
        taint[intent] = MySet()
    changed = OrderedSet(sources)
    while len(changed) > 0:
        worklist = flows  # TODO: Base worklist off of the changed elements.
        changed = OrderedSet()
        for flow in worklist:
            for t in taint[flow.src] | OrderedSet([flow.src]):
                if t not in taint[flow.sink]:
                    taint[flow.sink].add(t)
                    changed.add(flow.sink)
        if glo.is_quiet:
            print("Changed: " + str(len(changed)))
        else:
            print("Changed: " + str(changed))
    return taint

def read_intent_filter(intent_node):
    assert(isinstance(intent_node, ET.Element))
    assert(intent_node.tag == 'intent-filter')
    intent_filter = IntentFilter()
    for sub in intent_node.findall("*"):
        filter_attr = OrderedDict()
        for (key, val) in sub.attrib.iteritems():
            # E.g., key might be "android:name" (for action and category) or
            # "android:scheme" (for data), but with "android:" expanded out to
            # android_pfx.
            key = key.replace(android_pfx,"")
            filter_attr[key] = val
        if sub.tag in ['action', 'category']:
            intent_filter.__dict__[sub.tag].append(filter_attr['name'])
        elif sub.tag == 'data':
            intent_filter.mime_type.append(filter_attr.get('mimeType', None))
        else:
            die("Unexpected tag in intent-filter: '%s'!" % (sub.tag,))
    return intent_filter

def read_intent_filters_from_manifest(root):
    ret = OrderedDict()
    # Intent filters can be used with Activities as well as Activity-aliases
    # Alias is used to have a different label for the same activity
    all_components = root.findall(".//activity")+root.findall(".//activity-alias")
    for component in all_components:
        filter_list = []
        # Component name for an Activity is stored as the "name" attribute
        if component.tag == "activity":
            comp_name = component.attrib[android_pfx + "name"]
        # Component name for an Activity-alias is stored as the "targetActivity" attribute
        elif component.tag == "activity-alias":
            comp_name = component.attrib[android_pfx + "targetActivity"]
            glo.act_alias_to_targ[component.attrib[android_pfx + "name"]] = comp_name
        if comp_name.startswith("."):
            comp_name = root.find('.').attrib['package'] + comp_name
        for intent_node in component.findall(".//intent-filter"):
            filter_list.append(read_intent_filter(intent_node))
        ret.setdefault(comp_name, []);
        ret[comp_name] += filter_list
    return ret

def try_read_manifest_file(filename):
    root = None
    try:
        if filename.endswith(".apk"):
            manifest_text = subprocess.check_output(
                ["cd " + script_path + "; ./extract-manifest.sh " + os.path.realpath(filename)], shell=True)
            root = ET.fromstring(manifest_text)
        elif filename.endswith("AndroidManifest.xml") or filename.endswith(".manifest.xml"):
            root = ET.parse(filename)
    except ET.ParseError:
        sys.stderr.write("Error parsing %s\n" % (filename,))
        sys.stderr.write(traceback.format_exc())
    return root

def main():
    if not(sys.version_info[0] == 2 and sys.version_info[1] >= 7):
        die("Incompatible version of Python! This script needs Python 2.7.") 
    glo.manifest = OrderedDict()  # diccionario ordenado vacio
    flow_lists= []
    flow_files = []
    all_filenames = []
    arg_iter = iter(sys.argv[1:]) 
    gv_base = None
    gv_out = None
    gv_legend = None
    cl_out = None
    cl_out_from_file = True
    glo.is_quiet = False 
    if len(sys.argv[1:]) == 0:
        sys.stderr.write(
            ("Usage: %s [OPTIONS] [FILES]\n" % (sys.argv[0],)) +
            "Files: For each app, should include manifest, epicc, and flowdroid output.\n" +
            #"       To override package name, use 'pkg:filename' (UNTESTED).\n" +
            "Options: \n" +
            "  --gv graphfile: Generates graphfile.{gv,txt,pdf}\n" +
            "  --cl jsonfile:  Writes the Flows and taint solution in JSON format and checks that flows comply with security levels\n"
            "  --quiet:        Don't write as much to stdout\n"
        )
        sys.exit(1)
    while True:
        try:
            arg = arg_iter.next()
        except StopIteration:
            break
        try:
            if arg == "--unsound": 
                glo.unsound = True
            elif arg == "--quiet":
                glo.is_quiet = True
            elif arg == "--gv":
                gv_base = arg_iter.next()
                if not(re.match("^[A-Za-z0-9_.-/]+$", gv_base)):
                    die("gv filename contains bad characters")
                assert(not (gv_base.endswith(".gv")))
                gv_out = open(gv_base + ".gv", "w")
                gv_legend = open(gv_base + ".txt", "w")
            elif arg == "--check_levels_file": # Added
                cl_out_filename = arg_iter.next()
                cl_out = open(cl_out_filename, "w") # Writes the Flows and taint solution in JSON format
            elif arg == "--check_levels_gui": # Added
                cl_out_from_file = False
            else:
                all_filenames.append(arg)
        except StopIteration:
            die("Option '%s' expects an argument." % (arg,))
    def check_epicc(filename, pkg_name, epicc):
        def die_epicc():
            sys.stderr.write(traceback.format_exc())
            die("Aborted due to error in parsing " + filename)
        try:
            assert(len(pkg_name) > 0)
            assert(isinstance(epicc, dict))
            warned_unknown = False
            for (intent_id, v) in epicc.iteritems():
                assert(isinstance(intent_id, str))
                assert(isinstance(v, list))
                if intent_id == "*":
                    sys.stderr.write("Warning: Missing IntentID in %s\n" % (filename,))
                    warned_unknown = True
                else:
                    if (intent_id == BCAST_ID):
                        continue
                    else:
                        assert(intent_id.startswith("newField_"))
                for x in v:
                    try:
                        assert(isinstance(x, dict))
                    except AssertionError as e:
                        sys.stderr.write("\nx: %r\n" % (x,))
                        die_epicc()
        except AssertionError as e:
            die_epicc()
    for filename in all_filenames:
        pkg_rename = None
        if ":" in filename:
            [pkg_rename, filename] = filename.split(":")
        root = try_read_manifest_file(filename)
        if root != None:
            pkg_name = pkg_rename or root.find('.').attrib['package']
            glo.manifest[pkg_name] = root
            glo.filter[pkg_name] = read_intent_filters_from_manifest(root)
            if len(all_filenames) == 1:
                pprint(dict(glo.filter[pkg_name]))
        elif filename.endswith(".xml"):
            flow_files.append(filename)
        elif filename.endswith(".epicc"):
            (pkg_name, epicc) = parse_epicc(filename, as_dict=True)
            if pkg_rename:
                pkg_name = pkg_rename
            check_epicc(filename, pkg_name, epicc)
            glo.epicc[pkg_name] = epicc
            if len(all_filenames) == 1:
                print "EPICC info:"
                pprint(epicc)
        else:
            print("Unknown file type: " + filename)
    # Creates levels chequer
    check_levels = Check_levels(cl_out_from_file)
    for filename in flow_files:
        pkg_rename = None
        if ":" in filename:
            [pkg_rename, filename] = filename.split(":")
        tree = ET.parse(filename)
        root = tree.getroot()
        pkg_name = pkg_rename or root.attrib['package']
        flows = find_flows(root, check_levels)

    # Solve Flows
    def analize():
        def num_intents_in_flow(flow):
            return sum((type(s) in [Intent, IntentResult]) for s in [flow.src, flow.sink]) 
        for filename in flow_files:
            pkg_rename = None
            if ":" in filename:
                [pkg_rename, filename] = filename.split(":")
            tree = ET.parse(filename) 
            root = tree.getroot()
            pkg_name = pkg_rename or root.attrib['package']
            flows = find_flows(root, check_levels)
            glo.flows[pkg_name] = flows
            flow_lists.append(flows)

        flows = flatten(flow_lists) 
        flows = match_flows(flows)
        solution = solve_flows(flows)
        sol_src = {}
        for (entity, taint_set) in solution.iteritems():
            sol_src[entity] = OrderedSet(x for x in taint_set if (type(x)==Sink or type(x)==Src))
        
        if not glo.is_quiet:
            for num_intents in [0,1,2]:
                print("---- Flows with %i intent(s) ---------------------------------" % num_intents)
                pprint(filter(lambda x: num_intents_in_flow(x)==num_intents, flows))
            print("--------------------------------------------------------------")
            print("--------------------------------------------------------------")
            sols = [[],[],[]]
            for (entity, taint_set) in sol_src.iteritems():
                if type(entity) == Intent: 
                    ix = 0
                elif type(entity) == IntentResult:
                    ix = 1
                elif type(entity)==Sink:
                    ix = 2
                else:
                    assert(type(entity)==Src)
                    continue
                sols[ix].append((entity, taint_set))
            for ix in [0,1,2]:
                print("--------------------")
                for (entity, taint_set) in sols[ix]:
                    sys.stdout.write("### '%s': ###\n" % (entity,))
                    pprint(list(taint_set))
            print("--------------------")
        return sol_src
    
    def stringize_intents(obj): #??
        t = type(obj)
        if t in [str, int, type(None), Sink, Src]:
            return str(obj)
        elif t in [set, OrderedSet, list]:
            return list(stringize_intents(x) for x in obj)
        elif t in [dict]:
            return t((stringize_intents(k), stringize_intents(v)) for (k,v) in obj.iteritems())
        elif t in [Intent, IntentResult]:
            return str(obj)
        elif t == Flow:
            narf = list(stringize_intents(x) for x in obj)
            return Flow(*narf)
        else:
            assert(0)
            return obj

    def main_window(levels, entities, analize_leves, add_exception):
        import gettext
        import wx
        gettext.install("app") 
    
        app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        frame_1 = MyFrame(None, wx.ID_ANY, "")
        frame_1.create(levels, entities, analize_leves, add_exception)
        app.SetTopWindow(frame_1)
        frame_1.Show()
        app.MainLoop()
    def out_window(security_probl):
        import wx
        wx.InitAllImageHandlers()
        dialog_1 = MyDialog(None, wx.ID_ANY, "")
        dialog_1.create(security_probl)
        dialog_1.Show()
    
    def analize_leves(tuples):
        if tuples != None: 
            check_levels.selection_assign_levels(tuples)
        sol_src = analize()
        import json
        cl_dict = stringize_intents({'Taints': sol_src})
        cl_str = json.dumps(cl_dict, sort_keys=True, indent=4, separators=(',', ': '))
        security_probl = check_levels.check_levels(cl_dict)
        
        if tuples != None:
            out_window(security_probl)
        else:
            cl_out.write(security_probl)
    if cl_out_from_file:
        analize_leves(None) 
    else:
        main_window(check_levels.get_levels_order(), check_levels.get_vars_order(), analize_leves, check_levels.add_exception)

main()

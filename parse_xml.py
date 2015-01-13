#!/usr/bin/env python

# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.
#
"""Parses a CybOX Observables document and creates a python-cybox Observables instance.
Once parsed, the dictionary representation of the object is printed to stdout.
"""

import sys
import cybox.bindings.cybox_core as cybox_core_binding
from  cybox.core import Observables
import json
import rawes
import collections
from bson import json_util

es = rawes.Elastic('http://localhost:9200')

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def parse(xml_file):
    observables_obj = cybox_core_binding.parse(xml_file) # create binding object from xml file
    observables = Observables.from_obj(observables_obj) # convert binding object into python-cybox object
    return observables

def parseString(xml):
    observables_obj = cybox_core_binding.parseString(xml) # create binding object from xml string
    observables = Observables.from_obj(observables_obj) # to python-cybox object
    return observables

def mapping1():
    # mapping type 1 so that it'll index xml without any mapping exception
    with open("./data1.json") as json_file:
        json_data = json.load(json_file)
        print(json_data)
        try:
            es_map = es.post('cybox/_mapping/data1',data=json_data)
            print es_map
        except Exception, e:
            print e        
            pass
    return

def mapping2():
    # mapping type 2 so that it'll index xml without any mapping exception
    with open("./data2.json") as json_file:
        json_data = json.load(json_file)
        print(json_data)
        try:
            es_map = es.post('cybox/_mapping/data2',data=json_data)
            print es_map
        except Exception, e:
            print e        
            pass
    return

def mapping3():
    # mapping type 2 so that it'll index xml without any mapping exception
    with open("./data3.json") as json_file:
        json_data = json.load(json_file)
        print(json_data)
        try:
            es_map = es.post('cybox/_mapping/data3',data=json_data)
            print es_map
        except Exception, e:
            print e        
            pass
    return

def create():
    print 'create index and disable dynamic mapping'
    #with open("/home/ubuntu/cybox-parser/data.json") as json_file:
    json_data = '{"index.mapper.dynamic": false}'
    try:
        es_disable = es.put('cybox',data=json_data)
        print es_disable
        mapping1()
        mapping2()
        mapping3()
    except Exception, e:
        print e        
        pass
    return

def main():
    if len(sys.argv) != 2:
        print "[!] Please provide an xml file" 
        exit(1)
    
    xml = sys.argv[-1]
    observables = parseString(xml)
    ob_dict = observables.to_dict()
    #print "length of observables   " + str(len(ob_dict['observables']))

    #check for empty index
    try:
        es_count = es.get('cybox/_search', data={
                       'query' : {
                                    'match_all' : {}
                                }
                        })
    except Exception, e:
        if e.result['error'] == "IndexMissingException[[cybox] missing]":
            create()
            pass
    
    ob_json = json.dumps(ob_dict,default=json_util.default)
    try:
        es_index = es.post('cybox/data1',data=ob_json)
    except Exception, e:
        if e.result['status'] == 400 or e.result['status'] == 404:
            try:
                es_index = es.post('cybox/data2',data=ob_json)
            except Exception, e:
                if e.result['status'] == 400 or e.result['status'] == 404:
                    try:
                        es_index = es.post('cybox/data3',data=ob_json)
                    except Exception, e:
                        print e
                        f = open( '/home/ubuntu/cybox-parser/exception.json', 'w' )
                        f.write(ob_json)
                        f.close()
                        pass
                pass
        pass
    
    


if __name__ == "__main__":
    main()

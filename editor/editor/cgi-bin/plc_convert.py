#!/usr/local/bin/python3.10
import cgi, cgitb
cgitb.enable()


import pickle
import parseSTL
import json
import copy
import time
import sys

class visual():
    def __init__(self, title, id, type):
        self.title = title,
        self.id = id
        self.type = type
        self.in_slots = {}
        self.out_slots = {}
        self.count_in = 0
        self.count_out = 0

        self.link_outputs = {}
        self.link_inputs = {}
        self.subgraph = None
        self.previous = None
    
    def add_in_slot(self, i):
        if i not in self.in_slots:
            self.in_slots[i]=self.count_in
            self.count_in+=1
    
    def add_out_slot(self, o):
        if o not in self.out_slots:
            self.out_slots[o] = self.count_out
            self.count_out+=1
    
    def add_link_in(self, i, id):
        if i not in self.link_inputs:
            self.link_inputs[i] = id
    
    def add_link_out(self, o, id):
        if o not in self.link_outputs:
            self.link_outputs[o] = []
        self.link_outputs[o].append(id)
        
    def create_dct_representation(self, pos):
        dct = {"id":copy.deepcopy(int(self.id)), "type":self.type,"pos":pos, "size":[500,70], "mode":0,"properties":{"enabled":True,"id":0}}
        dct['title'] = self.title[0]#self.type.split('/')[1]+' '+str(copy.deepcopy(self.id))
        dct['description'] = self.title[0]
        dct['outputs'] = []
        for o in self.out_slots:
            if o in self.link_outputs:
                dct['outputs'].append({"name":o,"links":self.link_outputs[o],"slot_index":self.out_slots[o]})
            else:
                dct['outputs'].append({"name":o,"links":[],"slot_index":self.out_slots[o]})
        dct['inputs'] = []
        for i in self.in_slots:
            if i in self.link_inputs:
                dct['inputs'].append({"name":i,"link":self.link_inputs[i]})
            else:
                dct['inputs'].append({"name":i})

        max_len = max(len(dct['inputs']), len(dct['outputs']))
        dct['size']=[500,max(175,int(max_len*23))]
        if self.subgraph:
            dct['subgraph'] = self.subgraph
        return dct

def create_json_file(nodes, pairs):
    l = []
    counter = 0
    pos = [50,50]
    for n in nodes:
        l.append(n.create_dct_representation(pos))
        if counter == 10:
            pos = [500, pos[1]+500]
            counter = 0
        else:
            pos = [pos[0]+550, pos[1]]
            counter+=1

    return {"last_node_id": 0, "last_link_id": 0, "nodes": l, "links": pairs, "config": {}, "extra": {}, "version": 0.4}

def create_process(data, counter, pairs_id, element='"247170"'):
    nets = []
    calls = {}
    previous = None
    for n in data[element].networks:
        v = visual(n.title, counter, "sparks/procedure")
        for i in n.ins:
            v.add_in_slot(i)
       
        for o in n.outs:
            v.add_out_slot(o)
        
        for call in n.calls:
            c = call[0]
            if c not in calls:
                counter+=1
                calls[c] = visual(c, counter, "sparks/process")
                calls[c].title = (c+"("+call[1]+")",0)
                if c in data:
                    counter+=1
                    subgraph, counter, pairs_id = create_process(data,counter,pairs_id, c)
                    calls[c].subgraph = subgraph

            e = calls[c]
            #print(element, e.title, e.id, v.id)
            v.add_out_slot("Call_"+str(v.id)+'_'+str(e.id))
            e.add_in_slot("Call_"+str(v.id)+'_'+str(e.id))
        
        #v.add_in_slot('in')
        #v.add_out_slot('out')
        nets.append(v)
        if previous is not None:
            v.previous = previous
        previous = nets.index(v)
        counter+=1
    
    pairs = []
 
    for n in nets:
        if n.previous is not None:
            n.add_in_slot('in')
            nets[n.previous].add_out_slot('out')
            nets[n.previous].add_link_out("out",pairs_id)
            n.add_link_in("in", pairs_id)
            #print([pairs_id,nets[n.previous].id, nets[n.previous].out_slots['out'], n.id, n.in_slots["in"], None])
            pairs.append([pairs_id,nets[n.previous].id,nets[n.previous].out_slots['out'], n.id, n.in_slots["in"], None])
            pairs_id+=1
    for n1 in nets:
        for o in n1.out_slots:
            for n2 in nets:
                if n2.id>n1.id:
                    if o in n2.in_slots:
                        pairs.append([pairs_id,n1.id,n1.out_slots[o], n2.id, n2.in_slots[o], None])
                        n1.add_link_out(o,pairs_id)
                        n2.add_link_in(o, pairs_id)
                        pairs_id+=1
                    if o in n2.out_slots:
                        break
            for j in calls:
                if o in calls[j].in_slots:
                    pairs.append([pairs_id,n1.id,n1.out_slots[o], calls[j].id, calls[j].in_slots[o], None])
                    n1.add_link_out(o,pairs_id)
                    calls[j].add_link_in(o, pairs_id)
                    pairs_id+=1
    output_str = create_json_file(nets+list(calls.values()),pairs)
    return output_str, counter, pairs_id

def main():
    with open("/Users/bsteenwi/Documents/volvo/editor/special.txt", 'r', encoding="iso-8859-15") as f:
        file = f.read()#cgi.FieldStorage()['param'].value
    data = parseSTL.run(file)
    counter = 1
    pairs_id = 1
    #create_process(data, counter, pairs_id)
    print('Content-Type: application/json\n\n')
    print(json.dumps(create_process(data, counter, pairs_id, '"SPECIAL"')[0]))

    #print(nets[9].create_dct_representation([100,20]))
    #output_str = json.dumps(create_json_file(nets+list(calls.values),pairs))
    # pairs = []
    # nets = []
    # calls = {}
    # print( data['"247170"'])
    # for n in data['"247170"'].networks:
    #     n.block = '"247170"'
    #     n.type = "Network"
    #     nets.append(n)
    #     for c in n.calls:
    #         try:
    #             n.outs.append('CALL_'+c)
    #             if c not in calls:
    #                 data[c].proccess_tile = c
    #                 data[c].title = c
    #                 data[c].ins = []
    #                 data[c].outs = [n.title]
    #                 data[c].calls = []
    #                 data[c].type = "Block"
    #                 calls[c] = data[c]
    #             else:
    #                 data[c].outs.append(n.title)
    #                 #nets.append(data[c])
    #         except:
    #             None
    # #print(len(nets))
    # #exit(0)
    # #nets = data['"247170"'].networks
    # for n in range(len(nets)):
    #     nets[n].proccess_tile = copy.deepcopy(nets[n].title)
    #     nets[n].title = str(n+1)
        
    # #22
    # chosen = [nets.index(n) for n in nets]
    # print(chosen)

    # for i in chosen:
    #     for o in nets[i].outs:
    #         for j in chosen:
    #             if j>i:
    #                 if o in nets[j].ins:
    #                     pairs.append((nets[i].title,nets[i].outs.index(o), nets[j].title, nets[j].ins.index(o)))
    #                 if o in nets[j].outs:
    #                     break

    # #for i in chosen:
    # #    current_network = nets[i]
    # #    for j in chosen:
    # #        if j!=i:
    # #            for inp in nets[j].ins:
    # #                if inp in current_network.outs:
    # #                    pairs.append((nets[j].title,nets[j].ins.index(inp), current_network.title, current_network.outs.index(inp)))
    # #                if inp in nets[j].outs:
    # #                    print(inp)
    # #                    break
    # #print(pairs)
    
    # or "json.dump(result, sys.stdout)"
    #with open('test.tcgraph', 'w') as file:
    #    json.dump(output_str, file)



    #with open('dump.pkl','rb') as f:
    #    data = pickle.load(f)
    #with open('symbols.pkl','rb') as f:
    #    symbols = pickle.load(f)
    #data['"247170"'].networks[9].outs

main()

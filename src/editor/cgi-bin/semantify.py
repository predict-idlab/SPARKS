#!/usr/local/bin/python3.10
import cgi, cgitb
cgitb.enable()
import json
import kglab
import rdflib
from rdflib import URIRef
import requests

schemas = {"GB_PRODUCTIONLOG": URIRef("http://example.volvocars.net/ProductionSource"),
            "PRODUCTION_TRACKING_VCG":URIRef("http://example.volvocars.net/TrackingSource"),
            "GB_TEMP_CIP":URIRef("http://example.volvocars.net/StoSource"),
            "GB_TEST_SEQSTEP":URIRef("http://example.volvocars.net/SeqstepSource"),
            "GB_ROBVIEW":URIRef("http://example.volvocars.net/EventlogSource"),
            "ATACQ_VCG":URIRef("http://example.volvocars.net/AtacqSource")}

mapping = {"BodyNumber": URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'), 
 "Description": URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'), 
 "Source": URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
 "Timestamp": URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
"OFOUTKODE":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'), 
"STNModes":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'), 
"Code":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'), 
"FlowCode":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'), 
"Severity":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'),
"BodyType":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'), 
"Modes":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'), 
"PerfA1InCl":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#boolean'), 
"DBSTASTO":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
"FluidConsumption":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'),
"Title":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
"PerfA1OutCl":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#boolean'), 
"Registration":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
"Type":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'), 
"MtrlChangeOn":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#boolean'), 
"CavityCleaned":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#boolean'),
"TypemaskedBody":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#quantity'),
 "ItemCode":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string'),
 "HistoricalDataSource":URIRef('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/metrics#string')}

def main():
    data = json.loads(cgi.FieldStorage()['param'].value)
    #data = json.loads(text)
    namespaces = {
        "folio":  "http://IBCNServices.github.io/Folio-Ontology/Folio.owl#",
        "ssn":  "http://www.w3.org/ns/ssn/",
        "sosa": "http://www.w3.org/ns/sosa/",
        "sparks": "https://sparks.idlab.ugent.be/",
        "base" : "https://www.example.com/sparks/"
        }

    kg = kglab.KnowledgeGraph(
        name = "A volvo procedure KG example",
        namespaces = namespaces,
        )
    
    common_components = {
    'sparks/system': kg.get_ns("ssn").system,
    'sparks/sensor': kg.get_ns("sosa").sensor,
    'sparks/procedure': kg.get_ns("sparks").procedure,
    'sparks/process': kg.get_ns("sparks").process
    }

    common_relations = {
        'sparks/system': kg.get_ns("ssn").hasSubSystem,
        'sparks/process': kg.get_ns("sparks").contains
    }

    node_dct = {}

    def create_node(n, p, p_type, links):
        #node_A = rdflib.URIRef("http://10.63.126.170:31886/things/{}".format(n['id']))
        #kg.add(node, kg.get_ns("rdf").type, common_components[n['type']])
        #kg.add(node, kg.get_ns("rdf").description, rdflib.Literal(n['title']))
        node = rdflib.URIRef("https://www.example.com/{}/{}".format(n['type'],n['id']))
        kg.add(node, kg.get_ns("rdf").type, common_components[n['type']])
        try:
            kg.add(node, kg.get_ns("rdf").description, rdflib.Literal(n['title']))
        except:
            None
        node_dct[n['id']] = common_components[n['type']]

        if "sources" in n:
            for s in n["sources"]:
                property_source = rdflib.URIRef("http://10.63.126.170:31886/things/{}/properties/{}".format(n['id'],n["sources"][s]["property"]))
                kg.add(property_source,  kg.get_ns("rdf").type, kg.get_ns("sosa").ObservableProperty)
                kg.add(property_source, URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#produces'), mapping[n["sources"][s]["property"]])
                kg.add(node,kg.get_ns("ssn").observes,property_source)
                
                
                if n["sources"][s]['source'] == 'snowflake':
                    source = rdflib.URIRef("http://10.63.126.170:31886/things/{}{}{}HistoricalDataSource".format(n["sources"][s]["hasSensor"],n["sources"][s]['hasSchema'],n["sources"][s]['hasProperty']))
                    kg.add(source, kg.get_ns("rdf").type, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#SnowflakeDataSource'))
                    kg.add(source, kg.get_ns("rdf").type, schemas[n["sources"][s]['hasSchema']])
                    
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasSensor'), node)
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasProperty'), property_source)

                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasSchema'), rdflib.Literal(n["sources"][s]['hasSchema']))
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasTable'), rdflib.Literal(n["sources"][s]['hasTable']))
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasDatabase'), rdflib.Literal(n["sources"][s]['hasDatabase']))
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasColumn'), rdflib.Literal(n["sources"][s]['hasColumn']))
                    
                    

                if n["sources"][s]['source'] == 'kafka':
                    source = rdflib.URIRef("http://10.63.126.170:31886/things/{}{}{}StreamingDataSource".format(n["sources"][s]["hasSensor"],schemas[n["sources"][s]['hasTopic'].split('.')[1].upper()],n["sources"][s]['hasProperty']))
                    kg.add(source, kg.get_ns("rdf").type, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#SnowflakeDataSource'))
                    kg.add(source, kg.get_ns("rdf").type, schemas[n["sources"][s]['hasTopic'].split('.')[1].upper()])
                    
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasSensor'), node)
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasProperty'), property_source)

                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasTopic'), rdflib.Literal(n["sources"][s]['hasTopic']))
                    kg.add(source, rdflib.URIRef('https://dynamicdashboard.ilabt.imec.be/broker/ontologies/ddashboard#hasKey'), rdflib.Literal(n["sources"][s]['hasKey']))
        
        if "fault_table" in n:
            for i in range(len(n["fault_table"])):
                if n["fault_table"][i]['fault'] != "Enter Fault":
                    f_node = rdflib.URIRef("https://www.example.com/{}/{}/fault/{}".format(n['type'], n['id'], i+1))
                    kg.add(f_node, kg.get_ns("rdf").type, kg.get_ns("folio").FailureEffect)
                    kg.add(f_node, kg.get_ns("rdfs").label, rdflib.Literal(n["fault_table"][i]['fault']))
                    kg.add(f_node, kg.get_ns("folio").happenedAt, node)
                    
                    c_node = rdflib.URIRef("https://www.example.com/{}/{}/cause/{}".format(n['type'], n['id'], i+1))
                    kg.add(c_node, kg.get_ns("rdf").type, kg.get_ns("folio").FailureCause)
                    kg.add(c_node, kg.get_ns("rdfs").label, rdflib.Literal(n["fault_table"][i]['cause']))
                    kg.add(f_node, kg.get_ns("folio").hasCause, c_node)
                    
                    m_node = rdflib.URIRef("https://www.example.com/{}/{}/mitigation/{}".format(n['type'], n['id'], i+1))
                    kg.add(m_node, kg.get_ns("rdf").type, kg.get_ns("folio").Mitigation)
                    kg.add(m_node, kg.get_ns("rdfs").label, rdflib.Literal(n["fault_table"][i]['mitigation']))
                    kg.add(f_node, kg.get_ns("folio").hasMitigation, m_node)
        
        if 'inputs' in n:
            if 'procedure' in n['type']:
                for _in in n['inputs']:
                    if _in['name'] != "in":
                        if 'links' in _in and _in['links'] is not None:
                            if isinstance(_in['link'], list):
                                for l in _in['link']:
                                    rule = links[l]
                                    property_node = rdflib.URIRef("https://www.example.com/{}/{}/processinput/{}".format(n['type'],  n['id'], rule[4]))
                                    kg.add(property_node,kg.get_ns("rdfs").type, kg.get_ns("sparks").ProcessInput)
                                    kg.add(property_node,kg.get_ns("sparks").isProcessInputOf, node)
                                    kg.add(property_node, kg.get_ns("rdfs").label, rdflib.Literal(_in['name']))

                        if 'link' in _in:
                            if isinstance(_in['link'], int):
                                rule = links[_in['link']]
                                property_node = rdflib.URIRef("https://www.example.com/{}/{}/processinput/{}".format(n['type'],  n['id'], rule[4]))
                                kg.add(property_node,kg.get_ns("rdfs").type, kg.get_ns("sparks").ProcessInput)
                                kg.add(property_node,kg.get_ns("sparks").isProcessInputOf, node)
                                kg.add(property_node, kg.get_ns("rdfs").label, rdflib.Literal(_in['name']))
                            
            elif 'system' in n['type'] or 'sensor' in n['type']:
                for _in in n['inputs']:
                    if 'links' in _in  and _in['links'] is not None:
                        for l in _in['links']:
                            rule = links[l]
                            input_node = rdflib.URIRef("https://www.example.com/{}/{}/actuatableproperty/{}".format(n['type'],  n['id'], rule[4]))
                            kg.add(node, kg.get_ns("ssn").actsOnProperty, input_node)
                            kg.add(input_node, kg.get_ns("rdf").type, kg.get_ns("sosa").ActuatableProperty)
                            kg.add(input_node, kg.get_ns("rdfs").label, rdflib.Literal(_in['name']))
                    if "link" in _in:
                        if isinstance(_in['link'], int):
                            rule = links[_in['link']]
                            input_node = rdflib.URIRef("https://www.example.com/{}/{}/actuatableproperty/{}".format(n['type'],  n['id'], rule[4]))
                            kg.add(node, kg.get_ns("ssn").actsOnProperty, input_node)
                            kg.add(input_node, kg.get_ns("rdf").type, kg.get_ns("sosa").ActuatableProperty)
                            kg.add(input_node, kg.get_ns("rdfs").label, rdflib.Literal(_in['name']))

        if 'outputs' in n:
            if 'procedure' in n['type']:
                for _out in n['outputs']:
                    if _out['name'] != "out" or "Call_" in _out['name']:
                        if 'links' in _out and _out['links'] is not None:
                            if isinstance(_out['links'], list):
                                for l in _out['links']:
                                    rule = links[l]
                                    property_node = rdflib.URIRef("https://www.example.com/{}/{}/processoutput/{}".format(n['type'],  n['id'], rule[2]))
                                    kg.add(property_node,kg.get_ns("rdfs").type, kg.get_ns("sparks").ProcessOutput)
                                    kg.add(property_node,kg.get_ns("sparks").isProcessOutputOf, node)
                                    kg.add(property_node, kg.get_ns("rdfs").label, rdflib.Literal(_out['name']))

                        if 'link' in _out:
                            if isinstance(_out['link'], int):
                                rule = links[_out['link']]
                                property_node = rdflib.URIRef("https://www.example.com/{}/{}/processoutput/{}".format(n['type'],  n['id'], rule[2]))
                                kg.add(property_node,kg.get_ns("rdfs").type, kg.get_ns("sparks").ProcessOutput)
                                kg.add(property_node,kg.get_ns("sparks").isProcessOutputOf, node)
                                kg.add(property_node, kg.get_ns("rdfs").label, rdflib.Literal(_out['name']))
                            
            elif 'system' in n['type'] or 'sensor' in n['type']:
                for _out in n['outputs']:
                    if 'links' in _out  and _out['links'] is not None:
                        for l in _out['links']:
                            rule = links[l]
                            output_node = rdflib.URIRef("https://www.example.com/{}/{}/observableproperty/{}".format(n['type'],  n['id'], rule[2]))
                            kg.add(node, kg.get_ns("ssn").observes, output_node)
                            kg.add(output_node, kg.get_ns("rdf").type, kg.get_ns("sosa").ObservableProperty)
                            kg.add(output_node, kg.get_ns("rdfs").label, rdflib.Literal(_out['name']))
                    if "link" in _out:
                        if isinstance(_out['link'], int):
                            rule = links[_out['link']]
                            output_node = rdflib.URIRef("https://www.example.com/{}/{}/observableproperty/{}".format(n['type'],  n['id'], rule[2]))
                            kg.add(node, kg.get_ns("ssn").observes, output_node)
                            kg.add(output_node, kg.get_ns("rdf").type, kg.get_ns("sosa").ObservableProperty)
                            kg.add(output_node, kg.get_ns("rdfs").label, rdflib.Literal(_out['name']))

        if p is not None:
            kg.add(p, common_relations[p_type], node)
            

        if 'subgraph' in n:
            if False:
                sub_links = {d[0]:d for d in n['subgraph']['links']}
                for s in n['subgraph']['nodes']:
                    create_node(s, node, n['type'], sub_links)
                create_links(n['subgraph']['links'])
        
        return
    
    def create_links(links):
            for l in links:
                if 'system' in node_dct[l[1]]:
                    if 'procedure' in node_dct[l[3]]:
                        output_node = rdflib.URIRef("https://www.example.com/sparks/system/{}/observableproperty/{}".format(l[1], l[2]))
                        input_node = rdflib.URIRef("https://www.example.com/sparks/procedure/{}/processinput/{}".format(l[3], l[4]))
                        kg.add(output_node, kg.get_ns("sparks").propertyLinkedTo, input_node)
                if 'procedure' in node_dct[l[1]]:
                    if 'system' in node_dct[l[3]]:
                        output_node = rdflib.URIRef("https://www.example.com/sparks/procedure/{}/processoutput/{}".format(l[1], l[2]))
                        input_node = rdflib.URIRef("https://www.example.com/sparks/system/{}/actuatableproperty/{}".format(l[3], l[4]))
                        kg.add(input_node, kg.get_ns("sparks").propertyLinkedTo, output_node)
                    if 'process' in node_dct[l[3]]:
                        output_node = rdflib.URIRef("https://www.example.com/sparks/procedure/{}".format(l[1]))
                        input_node = rdflib.URIRef("https://www.example.com/sparks/process/{}".format(l[3]))
                        kg.add(input_node, kg.get_ns("sparks").hasProcedure, output_node)
                        kg.add(output_node, kg.get_ns("sparks").calls, input_node)
                    if 'procedure' in node_dct[l[3]]:
                        output_node = rdflib.URIRef("https://www.example.com/sparks/procedure/{}".format(l[1]))
                        input_node = rdflib.URIRef("https://www.example.com/sparks/procedure/{}".format(l[3]))
                        kg.add(output_node, kg.get_ns("sparks").hasNextProcedure, input_node)
                        #kg.add(input_node, kg.get_ns("sparks").hasPreviousPrecudre, output_node)
                        


                #print(node_dct[l[1]], node_dct[l[3]])
        
        #if 'title' in n:
        #    kg.add(node, kg.get_ns('sparks').hasTitle, rdflib.Literal(n['title']))
        
        #if 'description' in n:
        #    kg.add(node, kg.get_ns('sparks').hasDescription, rdflib.Literal(n['description']))


        
    
    if "links" not in data:
        data["links"] = []
    for n in data['nodes']:
        create_node(n, None, None, {d[0]:d for d in data["links"]})
    create_links(data["links"])


    
    ttl = kg.save_rdf_text()
    kg.save_rdf("test_graph.ttl", format="ttl")
    print("Content-type: text/html")
    print(ttl)

    #headers = {'Content-Type': 'text/turtle;charset=utf-8'}
    #r = requests.post('http://localhost:3030/volvo/data?default', data=ttl, headers=headers)
    #print(r.text)
    return ttl
main()

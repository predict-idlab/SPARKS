from reasoner import *

graph = "example.rdf"

#graph = query(3076989)
def fault(x):
    print(f'FAULT: car {str(x[0]).split(".")[-1]} is faulty due a too high VP413P04BF1value of {x[1]}')

rule1 = Rule('car(?x) ^ hasProdLog(?x, ?y) ^ metricVP413P04BF1value(?y, ?v) ^ greaterThan(?v, 18) -> Fault(?x, ?v)',
             'SELECT ?x ?y WHERE {?x <http://example.com/Fault> ?y}',
             lambda x: fault(x))

reasoner = RuleReasoner(graph, [rule1])
reasoner.reason()
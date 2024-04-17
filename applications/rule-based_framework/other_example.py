from reasoner import *
from rdflib import Graph, Namespace, Literal, RDF, OWL
g = Graph()

# Define a custom namespace
ex = Namespace('http://example.org/')

# Add RDF triples
g.add((ex.John, ex.hasAge, Literal(70)))
g.add((ex.Mary, ex.hasAge, Literal(50)))
g.add((ex.John, ex.hasParent, ex.Mary))
g.add((ex.hasAge, RDF.type, OWL.DatatypeProperty))
g.add((ex.Fault, RDF.type, OWL.ObjectProperty))
g.add((ex.hasParent, RDF.type, OWL.ObjectProperty))
g.add((ex.Person, RDF.type, OWL.Class))

g.serialize(destination="tmp.rdf", format='xml')

def fault(x):
    print(f'FAULT: {x[0]} is parent of {x[1]}, but the age of {x[0]} is less than {x[1]}')

rule1 = Rule('hasAge(?x,?a) ^ hasAge(?y,?b) ^ hasParent(?x, ?y) ^ lessThan(?b, ?a) -> Fault(?x, ?y)',
             'SELECT ?x ?y WHERE {?x <http://example.org/Fault> ?y}',
             lambda x: fault(x))

reasoner = RuleReasoner("tmp.rdf", [rule1])
reasoner.reason()
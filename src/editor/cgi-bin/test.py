from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# Define the namespaces
ns_plc = Namespace("http://example.com/plc/")
ns_stl = Namespace("http://example.com/stl/")

# Define the input STL code
stl_code = """
NETWORK 1:
  LD X0
  OUT Y0
  LD X1
  AND X2
  OUT Y1
END_NETWORK

NETWORK 2:
  LD X3
  OR X4
  OUT Y2
END_NETWORK
"""

# Parse the input STL code into a list of networks and instructions
networks = []
instructions = []
for line in stl_code.split("\n"):
    line = line.strip()
    if line.startswith("NETWORK"):
        if instructions:
            networks.append(instructions)
            instructions = []
    elif line.startswith("END_NETWORK"):
        if instructions:
            networks.append(instructions)
            instructions = []
    elif line:
        instructions.append(line)

# Create an RDF graph and add the networks and instructions as nodes and edges
g = Graph()
for i, network in enumerate(networks):
    network_uri = URIRef(ns_plc[f"network{i}"])
    g.add((network_uri, RDF.type, ns_stl.Network))
    for j, instruction in enumerate(network):
        instruction_uri = URIRef(ns_plc[f"instruction{i}-{j}"])
        g.add((instruction_uri, RDF.type, ns_stl.Instruction))
        g.add((network_uri, ns_stl.hasInstruction, instruction_uri))
        g.add((instruction_uri, ns_stl.hasCode, Literal(instruction)))

# Print the RDF graph in Turtle format
print(g.serialize(format="turtle"))
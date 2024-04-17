from rdflib import Graph
from owlready2 import get_ontology, default_world, sync_reasoner_pellet, Imp, Thing

class Rule:
    def __init__(self, rule_str, trigger_query, act):
        self.rule_str = rule_str
        self.trigger_query = trigger_query
        self.act = act


class RuleReasoner:
    def __init__(self, owl_file, rules):
        self.ontology = get_ontology(owl_file).load()
        self.rules = rules
        with self.ontology:
            for rule in self.rules:
                print(list(self.ontology._namespaces.values()))

                Imp().set_as_rule(rule.rule_str,namespaces=list(self.ontology._namespaces.values()))

    def reason(self):
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        for rule in self.rules:
            res = list(default_world.sparql(rule.trigger_query))
            for r in res:
                rule.act(r)
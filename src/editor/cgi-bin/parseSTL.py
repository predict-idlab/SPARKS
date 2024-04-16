import enum
import re
import string
from sys import argv
import json
import PLC_old as PLC
import pickle

dependencyLayers = 5

#state machine to keep track of where we are in the stl file
class State(enum.Enum):
    searchNetwork = 0 #looking for the start of a network
    network = 1 #found the start of a network, looking for stl code
    stl = 2 #reading stl code
    definitions = 3 #at the end of the file, reading memory names
    outsideOB = 4
    call = 5

class Block():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.networks = []
    def add_networks(self, networks):
        self.networks = networks

class Network():

    def __init__(self, title):
        self.title=title
        self.ins=list()
        self.outs=list()
        self.calls=list()

    def set_text(self, text):
        self.text = text

    def add_ins(self, arg):
        if arg not in self.ins:
            self.ins.append(arg)
    
    def add_calls(self, arg):
        if arg not in self.calls:
            self.calls.append(arg)

    def add_outs(self, arg):
        if arg not in self.outs:
            self.outs.append(arg)


def parse(statementList:list, plc:PLC):
    for op,arg in statementList:
        try:
            plc.mapping[op](plc, arg)
        except:
            continue;
        #print("RLO:",plc.statusWord["RLO"])
    plc.resetState()
    return 0


opcodeExtract = re.compile("^([\w=()]+)")
argExtract = re.compile("\S+\s+(\S+)\s+(\S+);")
paramExtract = re.compile("\s*(.)\s+([^,]*),")
dependExtract = re.compile('[^ |+|\-|<|>|=]*[:|"]+[^ |+|\-|<|>|=]*')

def run(inFile):
        state = State.outsideOB
    
    #if(len(argv) < 2):
    #    #print("Provide an STL file")
    #    exit()
#
    #inFile = argv[1]
    ##print("Reading from ", inFile)

        plc = PLC.PLC()


    #with open(inFile, "r",  errors='replace') as inFp:

        inLines = inFile.split('\n')
        networks = []
        blocks = {}
        statements = []
        organizationBlock = ""
        stlLineEnds = [";", "(", ")"]
        symbols = {}
        decompilation = []
        next_line=False
        for line in inLines:
            line = line.strip() ##format lines to a regular form
            if(line.startswith("//") or len(line) == 0): ##ignore comments
                if State.network and next_line:
                    networks[-1].comment = line
                    next_line = False
                continue

            if(state == State.call and line[-1] in stlLineEnds):
                state = State.stl
                continue;

            if state == State.call and line[-1] not in stlLineEnds:
                if '#' in line:
                    line = line.replace('#',fn_name+'.')
                opcode = opcodeExtract.search(line).groups()[0]
                #print(line.split(':=')[-1])
                arg = paramExtract.search(line.split(':=')[-1])

                if(arg != None):
                    arg = arg.groups()[0] + ":" + arg.groups()[1]
                else:
                    arg = line.split(':=')[-1].replace(" ",'').replace(',','')

                if arg.startswith('L:'):
                    arg = arg+'_network_'+str(len(networks))+"_"
                statements.append(['A', arg])
                statements.append([':=', opcode])

                #print(statements)
                #print(line)

            if(line.find(":") != -1):
                if "FUNCTION" in line:
                    line=line.split(':')[0].strip()
                else:
                    line = line[line.find(":")+1:].strip()

            if(state == State.stl and line[-1] not in stlLineEnds): #end of network since no more statements
                state = State.searchNetwork
                #print("Title:",networks[-1]["title"])
                #networks[-1]["text"] = parse(statements, plc)
                networks[-1].set_text(parse(statements, plc))
                #print(networks[-1]["text"])
                statements = []
            if(state == State.searchNetwork and line.startswith("NETWORK")):
                state = State.network
                continue
            if(state == State.network and line.startswith("TITLE")):
                #networks.append({"title": line[line.find("=")+1:].strip()})
                networks.append(Network(line[line.find("=")+1:].strip()))
                next_line=True
                continue
            if(state == State.network and line[-1] in stlLineEnds):
                state = State.stl

            if (state == State.stl and "CALL" in line):
                state = State.call
                params = line.replace('(','').replace('CALL','').replace(' ','').split(',')
                funct = params[0]
                if len(params)>1:
                    datablk = params[1]
                    statements.append(['CALL', funct])
                    statements.append(['BLOCK', datablk])
                    networks[-1].add_calls((funct, datablk))
                else:
                    statements.append(['CALL', funct])
                    networks[-1].add_calls((funct,""))

            if(state == State.stl and line[-1] in stlLineEnds):
                try:
                    opcode = opcodeExtract.search(line).groups()[0]
                except:
                    opcode=None
                    if "+I" in line:
                        opcode = "+I"
                    if '>=I' in line:
                        opcode = '>=I'
                    if '-D' in line:
                        opcode = "-I"
                    if '+D' in line:
                        opcode = "+I"
                    if '<D' in line:
                        opcode = "<I"

                #if opcode is None:
                    #print("jjjj", line)


                arg = argExtract.search(line)
                if(arg != None):
                    arg = arg.groups()[0] + ":" + arg.groups()[1]

                    ##print(arg)
                else:

                    try:
                        x = int(line.split('L')[-1].replace(' ','').replace(';',''))
                        arg=str(x)
                    except:
                        if ' #' in line:
                            line = line.replace('#',fn_name+'.')

                        if '"' in line.split(" ")[-1]:
                            arg = line.split(" ")[-1].replace(';','')
                        else:
                            if line.startswith('L '):
                                arg = line.split(' ')[-1].replace(';','')
                            else:
                                arg = line.split(opcode)[-1].replace(';','').strip()
                    ##print("None")
                ##print(opcode)
                if arg.startswith('L:'):
                    arg = arg+'_network_'+str(len(networks))+"_"
                #print([opcode, arg])

                if opcode in PLC.ins:
                    #print(opcode, arg)
                    networks[-1].add_ins(arg)
                if opcode in PLC.outs:
                    #print(opcode, arg)
                    networks[-1].add_outs(arg)

                statements.append([opcode, arg])
            if(state != State.outsideOB and (line == "END_ORGANIZATION_BLOCK" or line == "END_FUNCTION" or "END_DATA_BLOCK" in line)):
                state = State.outsideOB
                blocks[organizationBlock].add_networks(networks)
                networks = []
                organizationBlock = None
                continue
            if(state == State.outsideOB and ("ORGANIZATION_BLOCK" in line or "FUNCTION" in line) and "END" not in line):
                state = State.searchNetwork
                organizationBlock = line.split()[1]
                blocks[organizationBlock]=Block(organizationBlock, "OB")
                fn_name = organizationBlock
                continue
            if(state == State.outsideOB and line != ""):
                symbolDefinition = line.split()
                ##print(symbolDefinition)
                symbol = symbolDefinition[0]
                try:
                    memLocation = symbolDefinition[1] + ":" + symbolDefinition[2]
                    symbols[memLocation] = symbol
                except:
                    None
                ##print("added symbol <", symbol, "> at", memLocation)

    #print(plc.decompliations)
    #print(symbols)
    #symbol replacements
        humanReadable = []
        dependencies = {}

        return blocks
    #with open('dump.pkl', 'wb') as f:
    #    pickle.dump(blocks, f)
    ########


    # def convertTagToSymbol(tagText:string):
    #     for memLoc in symbols.keys():
    #         if(memLoc in tagText):
    #             ##print(memLoc)
    #             tagText = tagText.replace(memLoc, symbols[memLoc])
    #     return tagText

    # for decomp in plc.decompliations:
    #     decomp = decomp.strip()
    #     decomp:str
    #     #print("Original:", decomp)

    #     dependent = re.search("\S+$", decomp)
    #     if(dependent == None):
    #         #print("No dependent found:", decomp)
    #         continue
    #     dependent = dependent.group()
    #     try:
    #         z = int(dependent)
    #     except:
    #         dependent = convertTagToSymbol(dependent)
    #         if(dependent not in dependencies):
    #             dependencies[dependent] = {
    #                 "direct": set(),
    #                 "indirect": [set()] * dependencyLayers
    #             }
    #         if ':=' in decomp:
    #             dependencies[dependent]["direct"].add(decomp.split(':=')[0].replace('AND ','').replace(' ',''))

    #         for match in dependExtract.findall(decomp): #ignore the last result as that is the dependent
    #             match = match.replace(' ','')
    #             if convertTagToSymbol(match)!=dependent and match!="=>":
    #                 #if dependent == "Flip_Flop_00":

    #                     #print(dependent, convertTagToSymbol(match))
    #                     #print(decomp)
    #                 #print(convertTagToSymbol(match))
    #                 dependencies[dependent]["direct"].add(convertTagToSymbol(match))

    #         symbolText = convertTagToSymbol(decomp)
    #         #print(symbolText)
    #         #print(decomp)
    #         #print("Human Readable:", symbolText)
    #         #print()
    #         humanReadable.append(symbolText + "\n")

    # with open(inFile + ".parsed", "w") as outFP:
    #     outFP.writelines(humanReadable)

    # for currentDepLayer in range(0,dependencyLayers):
    #     for tag in dependencies:
    #         #print("Tag:", tag)
    #         dependencies[tag]["indirect"][currentDepLayer] = set()
    #         if(currentDepLayer == 0):
    #             dependencyList = dependencies[tag]["direct"]
    #         else:
    #             dependencyList = dependencies[tag]["indirect"][currentDepLayer-1]

    #         for dependency in dependencyList:
    #             #dependencies[tag]["indirect"][currentDepLayer].add(dependency)
    #             if(dependency not in dependencies):
    #                 continue
    #             #print("Layer " + str(currentDepLayer) + " Dependency:", dependency)
    #             for nextLayerDepend in dependencies[dependency]["direct"]:
    #                 if nextLayerDepend not in dependencies[tag]["indirect"][currentDepLayer-1]:
    #                 #print("\t\t" + "Nextlayer:", nextLayerDepend)
    #                     dependencies[tag]["indirect"][currentDepLayer].add(nextLayerDepend)
    #         dependencies[tag]["indirect"][currentDepLayer]:set
    #         # dependencies[tag]["indirect"][currentDepLayer] = dependencies[tag]["indirect"] - dependencies[tag]["direct"]
    #         #print(dependencies[tag])

    # #needed to JSON encode the sets "Direct" and "Indirect"
    # class SetEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #     if isinstance(obj, set):
    #         return list(obj)
    #     return json.JSONEncoder.default(self, obj)
    # with open(inFile + "_Dependencies.json", "w") as outFP:
    #     json_obj = json.dumps(dependencies, indent=4, cls=SetEncoder)
    #     outFP.write(json_obj)

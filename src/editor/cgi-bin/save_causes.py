#!/usr/local/bin/python3.10
import cgi, cgitb
cgitb.enable()
import json

def main():
    json_result = json.loads(cgi.FieldStorage()['param'].value)
    with open("causes.json", 'w') as f:
        f.write(json.dumps(json_result))
    return {"res":"done"}
    
main()

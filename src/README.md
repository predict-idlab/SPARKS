# SPARKS GUI Editor

[![SPARKS GUI Editor](https://github.com/predict-idlab/SPARKS/blob/main/img/sparks_editor.gif)](https://youtu.be/BzLiNpzNHU8)

# Run editor
## Installation steps:

To run the editor, make sure a sparql endpoint is available such as the editor dynamically loads the observable properties from this service.

In our example (and also how the code is now being configured), a volvo endpoint should be queryable at localhost:3030.
You can setup easily a fuseki SPARQL endpoint using the following docker command:
```
docker run -p 3030:3030 -e ADMIN_PASSWORD=pw123 stain/jena-fuseki
```
After ran succesfully, you can browse to localhost:3030 and login using admin and the admin password defined in the docker command.
Create a new database (in memory) and load the corresponding rdf file. A sample rdf file is available in the examples folder (KG).
After the triples are loaded correctly, you can start the editor.


## Run editor:
To run the editor, navigate in a terminal/CMD prompt to the editor folder and run the following command:
```
python3.10 -m http.server --bind localhost --cgi 8000
```
If you have a different python version, you have to change the python entries (first row) for the parseSTL.py, save_cause.py, save_faults.py and semantify.py files the cgi-bin folder to the correct version and path.

Finally, open a browser and navigate to localhost:8000. 

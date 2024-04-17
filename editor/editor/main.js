var webgl_canvas = null;

LiteGraph.node_images_path = "../nodes_data/";

var editor = new LiteGraph.Editor("main",{miniwindow:false});
window.graphcanvas = editor.graphcanvas;
window.graph = editor.graph;
window.addEventListener("resize", function() { editor.graphcanvas.resize(); } );

//enable scripting
LiteGraph.allow_scripts = true;

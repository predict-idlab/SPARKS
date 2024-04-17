//node constructor class

//Procedure: a node that contains a graph
function Procedure() {
    var that = this;
    this.size = [140, 80];
    this.properties = { enabled: true, id: 0,  };
    this.enabled = true;

    //create inner graph
    this.subgraph = new LiteGraph.LGraph();
    this.subgraph._subgraph_node = this;
    this.subgraph._is_subgraph = true;

    this.subgraph.onTrigger = this.onProcedureTrigger.bind(this);

//nodes input node added inside
    this.subgraph.onInputAdded = this.onProcedureNewInput.bind(this);
    this.subgraph.onInputRenamed = this.onProcedureRenamedInput.bind(this);
    this.subgraph.onInputTypeChanged = this.onProcedureTypeChangeInput.bind(this);
    this.subgraph.onInputRemoved = this.onProcedureRemovedInput.bind(this);

    this.subgraph.onOutputAdded = this.onProcedureNewOutput.bind(this);
    this.subgraph.onOutputRenamed = this.onProcedureRenamedOutput.bind(this);
    this.subgraph.onOutputTypeChanged = this.onProcedureTypeChangeOutput.bind(this);
    this.subgraph.onOutputRemoved = this.onProcedureRemovedOutput.bind(this);
    this.subgraph.addInput("In");
    this.subgraph.addOutput("Out");

    //links
    this.links = {}; //container with all the links
}

Procedure.title = "Procedure";
Procedure.desc = "Graph inside a node";
Procedure.title_color = "#334";


Procedure.prototype.onDblClick = function(e, pos, graphcanvas) {
  console.log(e);
  if (e.altKey) {
    var that = this;
    setTimeout(function() {
        graphcanvas.openSubgraph(that.subgraph);
    }, 10);
  }
};

Procedure.prototype.onAction = function(action, param) {
    this.subgraph.onAction(action, param);
};

Procedure.prototype.onExecute = function() {
    this.enabled = this.getInputOrProperty("enabled");
    if (!this.enabled) {
        return;
    }

    //send inputs to subgraph global inputs
    if (this.inputs) {
        for (var i = 0; i < this.inputs.length; i++) {
            var input = this.inputs[i];
            var value = this.getInputData(i);
            this.subgraph.setInputData(input.name, value);
        }
    }

    //execute
    this.subgraph.runStep();

    //send subgraph global outputs to outputs
    if (this.outputs) {
        for (var i = 0; i < this.outputs.length; i++) {
            var output = this.outputs[i];
            var value = this.subgraph.getOutputData(output.name);
            this.setOutputData(i, value);
        }
    }
};

Procedure.prototype.sendEventToAllNodes = function(eventname, param, mode) {
    if (this.enabled) {
        this.subgraph.sendEventToAllNodes(eventname, param, mode);
    }
};

Procedure.prototype.onDrawBackground = function (ctx, graphcanvas, canvas, pos) {
    if (this.flags.collapsed)
        return;
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    // button
    var over = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0], LiteGraph.NODE_TITLE_HEIGHT);
    let overleft = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0] / 2, LiteGraph.NODE_TITLE_HEIGHT)
    ctx.fillStyle = over ? "#555" : "#222";
    ctx.beginPath();
    if (this._shape == LiteGraph.BOX_SHAPE) {
        if (overleft) {
            ctx.rect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        } else {
            ctx.rect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        }
    }
    else {
        if (overleft) {
            ctx.roundRect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        } else {
            ctx.roundRect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        }
    }
    if (over) {
        ctx.fill();
    } else {
        ctx.fillRect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT);
    }
    // button
    ctx.textAlign = "center";
    ctx.font = "24px Arial";
    ctx.fillStyle = over ? "#DDD" : "#999";
    ctx.fillText("+", this.size[0] * 0.25, y + 24);
    ctx.fillText("+", this.size[0] * 0.75, y + 24);
}

Procedure.prototype.onMouseDown = function (e, localpos, graphcanvas) {
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    console.log(0)
    if (localpos[1] > y) {
        if (localpos[0] < this.size[0] / 2) {
            console.log(1)
            graphcanvas.showSubgraphPropertiesDialog(this);
        } else {
            console.log(2)
            graphcanvas.showSubgraphPropertiesDialogRight(this);
        }
    }
}
Procedure.prototype.computeSize = function()
{
var num_inputs = this.inputs ? this.inputs.length : 0;
var num_outputs = this.outputs ? this.outputs.length : 0;
return [ 200, Math.max(num_inputs,num_outputs) * LiteGraph.NODE_SLOT_HEIGHT + LiteGraph.NODE_TITLE_HEIGHT ];
}

//**** INPUTS ***********************************
Procedure.prototype.onProcedureTrigger = function(event, param) {
    var slot = this.findOutputSlot(event);
    if (slot != -1) {
        this.triggerSlot(slot);
    }
};

Procedure.prototype.onProcedureNewInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        //add input to the node
        this.addInput(name, type);
    }
};

Procedure.prototype.onProcedureRenamedInput = function(oldname, name) {
    var slot = this.findInputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.name = name;
};

Procedure.prototype.onProcedureTypeChangeInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.type = type;
};

Procedure.prototype.onProcedureRemovedInput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeInput(slot);
};

//**** OUTPUTS ***********************************
Procedure.prototype.onProcedureNewOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        this.addOutput(name, type);
    }
};

Procedure.prototype.onProcedureRenamedOutput = function(oldname, name) {
    var slot = this.findOutputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.name = name;
};

Procedure.prototype.onProcedureTypeChangeOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.type = type;
};

Procedure.prototype.onProcedureRemovedOutput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeOutput(slot);
};
// *****************************************************

Procedure.prototype.getExtraMenuOptions = function(graphcanvas) {
    var that = this;
    return [
        {
            content: "Open",
            callback: function() {
                graphcanvas.openSubgraph(that.subgraph);
            }
        }
    ];
};

Procedure.prototype.onResize = function(size) {
    size[1] += 20;
};

Procedure.prototype.serialize = function() {
    var data = LiteGraph.LGraphNode.prototype.serialize.call(this);
    data.subgraph = this.subgraph.serialize();
    return data;
};
//no need to define node.configure, the default method detects node.subgraph and passes the object to node.subgraph.configure()

Procedure.prototype.clone = function() {
    var node = LiteGraph.createNode(this.type);
    var data = this.serialize();
    delete data["id"];
    delete data["inputs"];
    delete data["outputs"];
    node.configure(data);
    return node;
};

Procedure.prototype.buildFromNodes = function(nodes)
{
//clear all?
//TODO

//nodes that connect data between parent graph and subgraph
var subgraph_inputs = [];
var subgraph_outputs = [];

//mark inner nodes
var ids = {};
var min_x = 0;
var max_x = 0;
for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  ids[ node.id ] = node;
  min_x = Math.min( node.pos[0], min_x );
  max_x = Math.max( node.pos[0], min_x );
}

var last_input_y = 0;
var last_output_y = 0;

for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  //check inputs
  if( node.inputs )
    for(var j = 0; j < node.inputs.length; ++j)
    {
      var input = node.inputs[j];
      if( !input || !input.link )
        continue;
      var link = node.graph.links[ input.link ];
      if(!link)
        continue;
      if( ids[ link.origin_id ] )
        continue;
      //this.addInput(input.name,link.type);
      this.subgraph.addInput(input.name,link.type);
      /*
      var input_node = LiteGraph.createNode("graph/input");
      this.subgraph.add( input_node );
      input_node.pos = [min_x - 200, last_input_y ];
      last_input_y += 100;
      */
    }

  //check outputs
  if( node.outputs )
    for(var j = 0; j < node.outputs.length; ++j)
    {
      var output = node.outputs[j];
      if( !output || !output.links || !output.links.length )
        continue;
      var is_external = false;
      for(var k = 0; k < output.links.length; ++k)
      {
        var link = node.graph.links[ output.links[k] ];
        if(!link)
          continue;
        if( ids[ link.target_id ] )
          continue;
        is_external = true;
        break;
      }
      if(!is_external)
        continue;
      //this.addOutput(output.name,output.type);
      /*
      var output_node = LiteGraph.createNode("graph/output");
      this.subgraph.add( output_node );
      output_node.pos = [max_x + 50, last_output_y ];
      last_output_y += 100;
      */
    }
}

//detect inputs and outputs
  //split every connection in two data_connection nodes
  //keep track of internal connections
  //connect external connections

//clone nodes inside subgraph and try to reconnect them

//connect edge subgraph nodes to extarnal connections nodes
}

LiteGraph.Procedure = Procedure;
LiteGraph.registerNodeType("sparks/procedure", Procedure);


//Process: a node that contains a graph
function Process() {
    var that = this;
    this.size = [140, 80];
    this.properties = { enabled: true, id: 0,  };
    this.enabled = true;

    this.links = {}; //container with all the links

    //create inner graph
    this.subgraph = new LiteGraph.LGraph();
    this.subgraph._subgraph_node = this;
    this.subgraph._is_subgraph = true;

    this.subgraph.onTrigger = this.onProcessTrigger.bind(this);

//nodes input node added inside
    this.subgraph.onInputAdded = this.onProcessNewInput.bind(this);
    this.subgraph.onInputRenamed = this.onProcessRenamedInput.bind(this);
    this.subgraph.onInputTypeChanged = this.onProcessTypeChangeInput.bind(this);
    this.subgraph.onInputRemoved = this.onProcessRemovedInput.bind(this);

    this.subgraph.onOutputAdded = this.onProcessNewOutput.bind(this);
    this.subgraph.onOutputRenamed = this.onProcessRenamedOutput.bind(this);
    this.subgraph.onOutputTypeChanged = this.onProcessTypeChangeOutput.bind(this);
    this.subgraph.onOutputRemoved = this.onProcessRemovedOutput.bind(this);
    this.subgraph.addInput("In");
    this.subgraph.addOutput("Out");
}

Process.title = "Process";
Process.desc = "Graph inside a node";
Process.title_color = "#134";

//Process.prototype.onGetInputs = function() {
//    return [["enabled", "boolean"]];
//};

/*
Process.prototype.onDrawTitle = function(ctx) {
    if (this.flags.collapsed) {
        return;
    }

    ctx.fillStyle = "#555";
    var w = LiteGraph.NODE_TITLE_HEIGHT;
    var x = this.size[0] - w;
    ctx.fillRect(x, -w, w, w);
    ctx.fillStyle = "#333";
    ctx.beginPath();
    ctx.moveTo(x + w * 0.2, -w * 0.6);
    ctx.lineTo(x + w * 0.8, -w * 0.6);
    ctx.lineTo(x + w * 0.5, -w * 0.3);
    ctx.fill();
};
*/


Process.prototype.onDblClick = function(e, pos, graphcanvas) {
  console.log(e);
  if (e.altKey) {
    var that = this;
    setTimeout(function() {
        graphcanvas.openSubgraph(that.subgraph);
    }, 10);
  }
};

/*
Process.prototype.onMouseDown = function(e, pos, graphcanvas) {
    if (
        !this.flags.collapsed &&
        pos[0] > this.size[0] - LiteGraph.NODE_TITLE_HEIGHT &&
        pos[1] < 0
    ) {
        var that = this;
        setTimeout(function() {
            graphcanvas.openProcess(that.subgraph);
        }, 10);
    }
};
*/

Process.prototype.onAction = function(action, param) {
    this.subgraph.onAction(action, param);
};

Process.prototype.onExecute = function() {
    this.enabled = this.getInputOrProperty("enabled");
    if (!this.enabled) {
        return;
    }

    //send inputs to subgraph global inputs
    if (this.inputs) {
        for (var i = 0; i < this.inputs.length; i++) {
            var input = this.inputs[i];
            var value = this.getInputData(i);
            this.subgraph.setInputData(input.name, value);
        }
    }

    //execute
    this.subgraph.runStep();

    //send subgraph global outputs to outputs
    if (this.outputs) {
        for (var i = 0; i < this.outputs.length; i++) {
            var output = this.outputs[i];
            var value = this.subgraph.getOutputData(output.name);
            this.setOutputData(i, value);
        }
    }
};

Process.prototype.sendEventToAllNodes = function(eventname, param, mode) {
    if (this.enabled) {
        this.subgraph.sendEventToAllNodes(eventname, param, mode);
    }
};

Process.prototype.onDrawBackground = function (ctx, graphcanvas, canvas, pos) {
    if (this.flags.collapsed)
        return;
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    // button
    var over = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0], LiteGraph.NODE_TITLE_HEIGHT);
    let overleft = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0] / 2, LiteGraph.NODE_TITLE_HEIGHT)
    ctx.fillStyle = over ? "#555" : "#222";
    ctx.beginPath();
    if (this._shape == LiteGraph.BOX_SHAPE) {
        if (overleft) {
            ctx.rect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        } else {
            ctx.rect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        }
    }
    else {
        if (overleft) {
            ctx.roundRect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        } else {
            ctx.roundRect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        }
    }
    if (over) {
        ctx.fill();
    } else {
        ctx.fillRect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT);
    }
    // button
    ctx.textAlign = "center";
    ctx.font = "24px Arial";
    ctx.fillStyle = over ? "#DDD" : "#999";
    ctx.fillText("+", this.size[0] * 0.25, y + 24);
    ctx.fillText("+", this.size[0] * 0.75, y + 24);
}

// Process.prototype.onMouseDown = function(e, localpos, graphcanvas)
// {
// 	var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
// 	if(localpos[1] > y)
// 	{
// 		graphcanvas.showProcessPropertiesDialog(this);
// 	}
// }
Process.prototype.onMouseDown = function (e, localpos, graphcanvas) {
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    console.log(0)
    if (localpos[1] > y) {
        if (localpos[0] < this.size[0] / 2) {
            console.log(1)
            graphcanvas.showSubgraphPropertiesDialog(this);
        } else {
            console.log(2)
            graphcanvas.showSubgraphPropertiesDialogRight(this);
        }
    }
}
Process.prototype.computeSize = function()
{
var num_inputs = this.inputs ? this.inputs.length : 0;
var num_outputs = this.outputs ? this.outputs.length : 0;
return [ 200, Math.max(num_inputs,num_outputs) * LiteGraph.NODE_SLOT_HEIGHT + LiteGraph.NODE_TITLE_HEIGHT ];
}

//**** INPUTS ***********************************
Process.prototype.onProcessTrigger = function(event, param) {
    var slot = this.findOutputSlot(event);
    if (slot != -1) {
        this.triggerSlot(slot);
    }
};

Process.prototype.onProcessNewInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        //add input to the node
        this.addInput(name, type);
    }
};

Process.prototype.onProcessRenamedInput = function(oldname, name) {
    var slot = this.findInputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.name = name;
};

Process.prototype.onProcessTypeChangeInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.type = type;
};

Process.prototype.onProcessRemovedInput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeInput(slot);
};

//**** OUTPUTS ***********************************
Process.prototype.onProcessNewOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        this.addOutput(name, type);
    }
};

Process.prototype.onProcessRenamedOutput = function(oldname, name) {
    var slot = this.findOutputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.name = name;
};

Process.prototype.onProcessTypeChangeOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.type = type;
};

Process.prototype.onProcessRemovedOutput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeOutput(slot);
};
// *****************************************************

Process.prototype.getExtraMenuOptions = function(graphcanvas) {
    var that = this;
    return [
        {
            content: "Open",
            callback: function() {
                graphcanvas.openSubgraph(that.subgraph);
            }
        }
    ];
};

Process.prototype.onResize = function(size) {
    size[1] += 20;
};

Process.prototype.serialize = function() {
    var data = LiteGraph.LGraphNode.prototype.serialize.call(this);
    data.subgraph = this.subgraph.serialize();
    return data;
};
//no need to define node.configure, the default method detects node.subgraph and passes the object to node.subgraph.configure()

Process.prototype.clone = function() {
    var node = LiteGraph.createNode(this.type);
    var data = this.serialize();
    delete data["id"];
    delete data["inputs"];
    delete data["outputs"];
    node.configure(data);
    return node;
};

Process.prototype.buildFromNodes = function(nodes)
{
//clear all?
//TODO

//nodes that connect data between parent graph and subgraph
var subgraph_inputs = [];
var subgraph_outputs = [];

//mark inner nodes
var ids = {};
var min_x = 0;
var max_x = 0;
for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  ids[ node.id ] = node;
  min_x = Math.min( node.pos[0], min_x );
  max_x = Math.max( node.pos[0], min_x );
}

var last_input_y = 0;
var last_output_y = 0;

for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  //check inputs
  if( node.inputs )
    for(var j = 0; j < node.inputs.length; ++j)
    {
      var input = node.inputs[j];
      if( !input || !input.link )
        continue;
      var link = node.graph.links[ input.link ];
      if(!link)
        continue;
      if( ids[ link.origin_id ] )
        continue;
      //this.addInput(input.name,link.type);
      this.subgraph.addInput(input.name,link.type);
      /*
      var input_node = LiteGraph.createNode("graph/input");
      this.subgraph.add( input_node );
      input_node.pos = [min_x - 200, last_input_y ];
      last_input_y += 100;
      */
    }

  //check outputs
  if( node.outputs )
    for(var j = 0; j < node.outputs.length; ++j)
    {
      var output = node.outputs[j];
      if( !output || !output.links || !output.links.length )
        continue;
      var is_external = false;
      for(var k = 0; k < output.links.length; ++k)
      {
        var link = node.graph.links[ output.links[k] ];
        if(!link)
          continue;
        if( ids[ link.target_id ] )
          continue;
        is_external = true;
        break;
      }
      if(!is_external)
        continue;
      //this.addOutput(output.name,output.type);
      /*
      var output_node = LiteGraph.createNode("graph/output");
      this.subgraph.add( output_node );
      output_node.pos = [max_x + 50, last_output_y ];
      last_output_y += 100;
      */
    }
}

//detect inputs and outputs
  //split every connection in two data_connection nodes
  //keep track of internal connections
  //connect external connections

//clone nodes inside subgraph and try to reconnect them

//connect edge subgraph nodes to extarnal connections nodes
}

LiteGraph.Process = Process;
LiteGraph.registerNodeType("sparks/process", Process);


//Process: a node that contains a graph
function System() {
    var that = this;
    this.size = [140, 80];
    this.properties = { enabled: true, id: 0};
    this.enabled = true;

    //create inner graph
    this.subgraph = new LiteGraph.LGraph();
    this.subgraph._subgraph_node = this;
    this.subgraph._is_subgraph = true;

    this.subgraph.onTrigger = this.onSystemTrigger.bind(this);

//nodes input node added inside
    this.subgraph.onInputAdded = this.onSystemNewInput.bind(this);
    this.subgraph.onInputRenamed = this.onSystemRenamedInput.bind(this);
    this.subgraph.onInputTypeChanged = this.onSystemTypeChangeInput.bind(this);
    this.subgraph.onInputRemoved = this.onSystemRemovedInput.bind(this);

    this.subgraph.onOutputAdded = this.onSystemNewOutput.bind(this);
    this.subgraph.onOutputRenamed = this.onSystemRenamedOutput.bind(this);
    this.subgraph.onOutputTypeChanged = this.onSystemTypeChangeOutput.bind(this);
    this.subgraph.onOutputRemoved = this.onSystemRemovedOutput.bind(this);
    //this.subgraph.addInput("In");
    //this.subgraph.addOutput("Out");
}

System.title = "System";
System.desc = "Graph inside a node";
System.title_color = "#2bb287";

//Process.prototype.onGetInputs = function() {
//    return [["enabled", "boolean"]];
//};

/*
Process.prototype.onDrawTitle = function(ctx) {
    if (this.flags.collapsed) {
        return;
    }

    ctx.fillStyle = "#555";
    var w = LiteGraph.NODE_TITLE_HEIGHT;
    var x = this.size[0] - w;
    ctx.fillRect(x, -w, w, w);
    ctx.fillStyle = "#333";
    ctx.beginPath();
    ctx.moveTo(x + w * 0.2, -w * 0.6);
    ctx.lineTo(x + w * 0.8, -w * 0.6);
    ctx.lineTo(x + w * 0.5, -w * 0.3);
    ctx.fill();
};
*/


System.prototype.onDblClick = function(e, pos, graphcanvas) {
  console.log(e);
  if (e.altKey) {
    var that = this;
    setTimeout(function() {
        graphcanvas.openSubgraph(that.subgraph);
    }, 10);
  }
};

/*
Process.prototype.onMouseDown = function(e, pos, graphcanvas) {
    if (
        !this.flags.collapsed &&
        pos[0] > this.size[0] - LiteGraph.NODE_TITLE_HEIGHT &&
        pos[1] < 0
    ) {
        var that = this;
        setTimeout(function() {
            graphcanvas.openProcess(that.subgraph);
        }, 10);
    }
};
*/

System.prototype.onAction = function(action, param) {
    this.subgraph.onAction(action, param);
};

System.prototype.onExecute = function() {
    this.enabled = this.getInputOrProperty("enabled");
    if (!this.enabled) {
        return;
    }

    //send inputs to subgraph global inputs
    if (this.inputs) {
        for (var i = 0; i < this.inputs.length; i++) {
            var input = this.inputs[i];
            var value = this.getInputData(i);
            this.subgraph.setInputData(input.name, value);
        }
    }

    //execute
    this.subgraph.runStep();

    //send subgraph global outputs to outputs
    if (this.outputs) {
        for (var i = 0; i < this.outputs.length; i++) {
            var output = this.outputs[i];
            var value = this.subgraph.getOutputData(output.name);
            this.setOutputData(i, value);
        }
    }
};

System.prototype.sendEventToAllNodes = function(eventname, param, mode) {
    if (this.enabled) {
        this.subgraph.sendEventToAllNodes(eventname, param, mode);
    }
};

System.prototype.onDrawBackground = function (ctx, graphcanvas, canvas, pos) {
    if (this.flags.collapsed)
        return;
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    // button
    var over = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0], LiteGraph.NODE_TITLE_HEIGHT);
    let overleft = LiteGraph.isInsideRectangle(pos[0], pos[1], this.pos[0], this.pos[1] + y, this.size[0] / 2, LiteGraph.NODE_TITLE_HEIGHT)
    ctx.fillStyle = over ? "#555" : "#222";
    ctx.beginPath();
    if (this._shape == LiteGraph.BOX_SHAPE) {
        if (overleft) {
            ctx.rect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        } else {
            ctx.rect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT);
        }
    }
    else {
        if (overleft) {
            ctx.roundRect(0, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        } else {
            ctx.roundRect(this.size[0] / 2, y, this.size[0] / 2 + 1, LiteGraph.NODE_TITLE_HEIGHT, [0,0, 8,8]);
        }
    }
    if (over) {
        ctx.fill();
    } else {
        ctx.fillRect(0, y, this.size[0] + 1, LiteGraph.NODE_TITLE_HEIGHT);
    }
    // button
    ctx.textAlign = "center";
    ctx.font = "24px Arial";
    ctx.fillStyle = over ? "#DDD" : "#999";
    ctx.fillText("+", this.size[0] * 0.25, y + 24);
    ctx.fillText("+", this.size[0] * 0.75, y + 24);
}

// Process.prototype.onMouseDown = function(e, localpos, graphcanvas)
// {
// 	var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
// 	if(localpos[1] > y)
// 	{
// 		graphcanvas.showProcessPropertiesDialog(this);
// 	}
// }
System.prototype.onMouseDown = function (e, localpos, graphcanvas) {
    var y = this.size[1] - LiteGraph.NODE_TITLE_HEIGHT + 0.5;
    console.log(0)
    if (localpos[1] > y) {
        if (localpos[0] < this.size[0] / 2) {
            console.log(1)
            graphcanvas.showSubgraphPropertiesDialog(this);
        } else {
            console.log(2)
            graphcanvas.showSubgraphPropertiesDialogRight(this);
        }
    }
}
System.prototype.computeSize = function()
{
var num_inputs = this.inputs ? this.inputs.length : 0;
var num_outputs = this.outputs ? this.outputs.length : 0;
return [ 200, Math.max(num_inputs,num_outputs) * LiteGraph.NODE_SLOT_HEIGHT + LiteGraph.NODE_TITLE_HEIGHT ];
}

//**** INPUTS ***********************************
System.prototype.onSystemTrigger = function(event, param) {
    var slot = this.findOutputSlot(event);
    if (slot != -1) {
        this.triggerSlot(slot);
    }
};

System.prototype.onSystemNewInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        //add input to the node
        this.addInput(name, type);
    }
};

System.prototype.onSystemRenamedInput = function(oldname, name) {
    var slot = this.findInputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.name = name;
};

System.prototype.onSystemTypeChangeInput = function(name, type) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getInputInfo(slot);
    info.type = type;
};

System.prototype.onSystemRemovedInput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeInput(slot);
};

//**** OUTPUTS ***********************************
System.prototype.onSystemNewOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        this.addOutput(name, type);
    }
};

System.prototype.onSystemRenamedOutput = function(oldname, name) {
    var slot = this.findOutputSlot(oldname);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.name = name;
};

System.prototype.onSystemTypeChangeOutput = function(name, type) {
    var slot = this.findOutputSlot(name);
    if (slot == -1) {
        return;
    }
    var info = this.getOutputInfo(slot);
    info.type = type;
};

System.prototype.onSystemRemovedOutput = function(name) {
    var slot = this.findInputSlot(name);
    if (slot == -1) {
        return;
    }
    this.removeOutput(slot);
};
// *****************************************************

System.prototype.getExtraMenuOptions = function(graphcanvas) {
    var that = this;
    return [
        {
            content: "Open",
            callback: function() {
                graphcanvas.openSubgraph(that.subgraph);
            }
        }
    ];
};

System.prototype.onResize = function(size) {
    size[1] += 20;
};

System.prototype.serialize = function() {
    var data = LiteGraph.LGraphNode.prototype.serialize.call(this);
    data.subgraph = this.subgraph.serialize();
    return data;
};
//no need to define node.configure, the default method detects node.subgraph and passes the object to node.subgraph.configure()

System.prototype.clone = function() {
    var node = LiteGraph.createNode(this.type);
    var data = this.serialize();
    delete data["id"];
    delete data["inputs"];
    delete data["outputs"];
    node.configure(data);
    return node;
};

System.prototype.buildFromNodes = function(nodes)
{
//clear all?
//TODO

//nodes that connect data between parent graph and subgraph
var subgraph_inputs = [];
var subgraph_outputs = [];

//mark inner nodes
var ids = {};
var min_x = 0;
var max_x = 0;
for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  ids[ node.id ] = node;
  min_x = Math.min( node.pos[0], min_x );
  max_x = Math.max( node.pos[0], min_x );
}

var last_input_y = 0;
var last_output_y = 0;

for(var i = 0; i < nodes.length; ++i)
{
  var node = nodes[i];
  //check inputs
  if( node.inputs )
    for(var j = 0; j < node.inputs.length; ++j)
    {
      var input = node.inputs[j];
      if( !input || !input.link )
        continue;
      var link = node.graph.links[ input.link ];
      if(!link)
        continue;
      if( ids[ link.origin_id ] )
        continue;
      //this.addInput(input.name,link.type);
      this.subgraph.addInput(input.name,link.type);
      /*
      var input_node = LiteGraph.createNode("graph/input");
      this.subgraph.add( input_node );
      input_node.pos = [min_x - 200, last_input_y ];
      last_input_y += 100;
      */
    }

  //check outputs
  if( node.outputs )
    for(var j = 0; j < node.outputs.length; ++j)
    {
      var output = node.outputs[j];
      if( !output || !output.links || !output.links.length )
        continue;
      var is_external = false;
      for(var k = 0; k < output.links.length; ++k)
      {
        var link = node.graph.links[ output.links[k] ];
        if(!link)
          continue;
        if( ids[ link.target_id ] )
          continue;
        is_external = true;
        break;
      }
      if(!is_external)
        continue;
      //this.addOutput(output.name,output.type);
      /*
      var output_node = LiteGraph.createNode("graph/output");
      this.subgraph.add( output_node );
      output_node.pos = [max_x + 50, last_output_y ];
      last_output_y += 100;
      */
    }
}

//detect inputs and outputs
  //split every connection in two data_connection nodes
  //keep track of internal connections
  //connect external connections

//clone nodes inside subgraph and try to reconnect them

//connect edge subgraph nodes to extarnal connections nodes
}

LiteGraph.System = System;
LiteGraph.registerNodeType("sparks/system", System);





//Show value inside the debug console
function Sensor() {
    this.mode = LiteGraph.ON_EVENT;
    this.properties = { enabled: true, id: 0,  "Service schema": "",  "Service signal": "", "Service Table":""};
    this.addProperty("msg", "");
    var that = this;
    //this.widget = this.addWidget("text", "Text", "", "msg");
    this.widgets_up = true;
    this.size = [200, 30];
}

Sensor.title = "Sensor";
Sensor.desc = "Show an Sensor window";
Sensor.color = "#00f2e6";


LiteGraph.registerNodeType("sparks/sensor", Sensor);

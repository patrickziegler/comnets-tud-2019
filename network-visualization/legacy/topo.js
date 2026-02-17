/* global vis */

var HOST = "http://localhost:8080";

var EDGE_COLOR_DEFAULT = "#000000";
var EDGE_WIDTH_DEFAULT = 1;
var EDGE_COLOR_ACTIVE = "#0000ff";
var EDGE_WIDTH_ACTIVE = 10;
var EDGE_COLOR_DISABLED = "#ff0000";
var EDGE_WIDTH_DISABLED = 2;

var MAX_IDLE = 3;

var nodes = null;
var edges = null;

/* load topology from json file */
$.ajax({
    async: false,
    url: "topo.json",
    dataType: "json",
    success: function(data) {
        nodes = new vis.DataSet(data.nodes);
        edges = new vis.DataSet(data.edges);
    }
});

/* add field 'idle' for tracking idle cylces in 'update_network_graph' */
edges.update(edges.map(
        function (e) {
            e.color = {color: EDGE_COLOR_DEFAULT};
    e.idle = 0;
    e.disabled = false;
    return e;
}));

var options = {
    nodes: {
        shape: 'dot',
        size: 10,
        color: '#ed5aab',
        font: '20px sans green',
        fixed: {
            x: true,
            y: true
        }
    },
    edges: {
        smooth: false,
        width: EDGE_WIDTH_DEFAULT,
        color: {
            color: EDGE_COLOR_DEFAULT
        }
    },
    physics: false
};

var container = document.getElementById('topo');

var data = {
    nodes: nodes,
    edges: edges
};

var network = new vis.Network(container, data, options);

var width = nodes.max("x")["x"];
var height = nodes.max("y")["y"] + nodes.min("y")["y"];

network.moveTo({
    position: {x: 0, y: 0},
    offset: {
        x: -width/2,
        y: -height/2
    },
    scale: 1
});

network.on("click", function(params) {
    
    (edges.get(params.edges)).forEach(function (e) {
        var data;
        
        if (e.disabled) {
            data = "" + e.cost;
        } else {
            data = "9999";
        }
            
        $.ajax({
            url: HOST + "/nodes/s" + e.from + "/links/s" + e.to,
            type: "PUT",
            data: data
        });
            
        $.ajax({
            url: HOST + "/nodes/s" + e.to + "/links/s" + e.from,
            type: "PUT",
            data: data
        });
    });
    
});

network.on("doubleClick", function(params) {
    
    edges.forEach(function (e) {
        
        $.ajax({
            url: HOST + "/nodes/s" + e.from + "/links/s" + e.to,
            type: "PUT",
            data: "" + e.cost
        });
            
        $.ajax({
            url: HOST + "/nodes/s" + e.to + "/links/s" + e.from,
            type: "PUT",
            data: "" + e.cost
        });
        
    });
    
});

function update() {
    tmp = edges.map(
            function (e) {
                e.idle++;
        return e;
    });
    
    $.ajax({
        async: false,
        url: HOST + "/flows",
        dataType: "json",
        
        success: function(data) {
            for (var i = 0; i < data.length; i++) {
            
                if (data[i].to.length === 0) {
                    continue;
                }
            
                var from = Number(data[i].from.substr(1,4));
                var to = Number(data[i].to[0].substr(1,4));
            
                tmp = tmp.map( function (e) {
                
                    if ((e.from === from && e.to === to) || 
                            (e.from === to && e.to === from)) {
                        e.color = {color: EDGE_COLOR_ACTIVE};
                        e.width = EDGE_WIDTH_ACTIVE;
                        e.idle = 0;
                    }
                
                    return e;
                });
            
            }
        }
    });
    
    tmp = tmp.map( function (e) {
        
        if (e.idle > MAX_IDLE) {
            e.color = {color: EDGE_COLOR_DEFAULT};
            e.width = EDGE_WIDTH_DEFAULT;
            e.idle = 1;
        }
        
        return e;
    });
    
    $.ajax({
        async: false,
        url: HOST + "/nodes",
        dataType: "json",
        
        success: function(data) {
            tmp = tmp.map( function(e) {
                
                e.disabled = false;
                
                if (data["s" + e.from].links["s" + e.to] === 9999) {
                    e.color = {color: EDGE_COLOR_DISABLED};
                    if (e.idle === 0) {
                        e.width = EDGE_WIDTH_ACTIVE;
                    } else {
                        e.width = EDGE_WIDTH_DISABLED;
                    }
                    e.disabled = true;
                }
                
                return e;
            });
            
        }
    });
    
    edges.update(tmp);
}

setInterval(update, 100);

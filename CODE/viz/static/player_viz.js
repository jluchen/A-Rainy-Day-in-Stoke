console.log('player viz oui oui')
var margin = {top:100, right:100, bottom:100, left:100};
width = window.innerWidth-200;
height = 500;

//node scale
var minRad = 5;
var maxRad = 20;
var node_scale = d3.scaleLinear().range([minRad,maxRad]);

var svg = d3.select('#player_viz').append('svg')
	.attr("width", width)
	.attr("height", height)
	.attr("margins", margin)
	.attr("class", "player_graph");

svg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "#d5d7d4");

var tip = d3.tip().attr("class", "tip").html(function(d){
	var tipInfo = "<strong>Player: </strong>" + d["name"]
				  + "<br><strong>Gender: </strong>" + d["gender"]
				  + "<br><strong>Position: </strong>" + d["pos"]
				  + "<br><strong>Seasons Played: </strong>" + d["season"]
				  + "<br><strong>Leagues Played In: </strong>" + d["league"]
				  + "<br><strong>Teams Played For: </strong>" + d["squad"];
	return tipInfo});
svg.call(tip)

d3.dsv(',', '/get-stats', function(d){
	return {
		player: d['Player']
		,gender: d['Gender']
		,pos: d['Pos']
		,squad: d['Squad']
		,season: d['Season']
		,league: d['League']
	}
}).then(function(stats) {
	//console.log(stats)
//});

	d3.dsv(',', '/get-player-graph', function(d){
		//console.log(d);
		return {
			source: d['Source']
			,target: d['Player']
			,degree: +d['degree']
		}
	}).then(function(data){
		//console.log(data);
		var links = data;

		var nodes = {};

		// compute the distinct nodes from the links.
		links.forEach(function(link) {
		  //link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
		  var source_stats = stats.filter(function(s){
			return s['player'] == link.source});
		  var target_stats = stats.filter(function(s){
			return s['player'] == link.target});
		  try {
			  link.source = nodes[link.source] || (nodes[link.source] = {name: link.source, weight: link.degree
			  															,gender: source_stats[0]['gender']
			  															,pos: source_stats[0]['pos']
			  															,season: source_stats[0]['season']
			  															,league: source_stats[0]['league']
			  															,squad: source_stats[0]['squad']
			  															});
		  } catch(error){
		  	link.source = nodes[link.source] || (nodes[link.source] = {name: link.source, weight: link.degree
			  															,gender: 'N/A'
				  														,pos: 'N/A'
				  														,season: 'N/A'
				  														,league: 'N/A'
				  														,squad: 'N/A'
			  															});
		  }
		  try {
			  link.target = nodes[link.target] || (nodes[link.target] = {name: link.target, weight: link.degree
			  															,gender: target_stats[0]['gender']
			  															,pos: target_stats[0]['pos']
			  															,season: target_stats[0]['season']
			  															,league: target_stats[0]['league']
			  															,squad: target_stats[0]['squad']
			  															});
		  } catch(error) {
			  link.target = nodes[link.target] || (nodes[link.target] = {name: link.target, weight: link.degree
				  														,gender: 'N/A'
				  														,pos: 'N/A'
				  														,season: 'N/A'
				  														,league: 'N/A'
				  														,squad: 'N/A'
				  														});
		  }
		});
		//console.log(links);
		//console.log(nodes);

		var force = d3.forceSimulation()
	      .nodes(d3.values(nodes))
	      .force("link", d3.forceLink(links).distance(100))
	      .force('center', d3.forceCenter(width / 2, height / 2))
	      .force("x", d3.forceX())
	      .force("y", d3.forceY())
	      .force("charge", d3.forceManyBody().strength(-250))
	      .alphaTarget(1)
	      .on("tick", tick);
		
	     var g = svg.append("g").attr("class", "everything") 
	     //var path = svg.append("g")
	     var path = g.append("g")
	      .selectAll("path")
	      .data(links)
	      .enter()
	      .append("path")
	      .attr("class", function(d) { return "link " + d.type; })
	      .style("stroke", '#6EB5FF')
	      .style("stroke-width", 3)
	      .style("fill", "none");

		  // define the nodes
		  //console.log(force.nodes())
		  //var node = svg.selectAll(".node")
		  var node = g.selectAll(".node")
		      .data(force.nodes())
		      .enter().append("g")
		      .attr("class", "node")
		      .call(d3.drag()
		          .on("start", dragstarted)
		          .on("drag", dragged)
		          .on("end", dragended))
		      .on("mouseover", tip.show)
		      .on("mouseleave", tip.hide)
		      .on("dblclick", function(d){
		      	console.log('yo');
		      	//$.get("/player_comp", {player_name: d["name"]});
		      	//$("html").load("/player_comp?" + $.param({player_name: d["name"]}));
		      	//document.getElementById('#player_search').submit();
		      	//$(".player_name").submit();
		      	$('#player_value').val(d["name"]);
		      	$("#player_search").submit();
		      })
		      .on("contextmenu", function(d){
		      	d3.event.preventDefault();
		      //.on("dblclick", function(d){
		      	d.fixed=false;
		      	d.fx = null;
		      	d.fy = null;
		      	d3.select(this).select("circle").style("stroke-width", 1.5)});

		  // add the nodes
		  //console.log(node)
		  node.append("circle")
		      //.attr("r", 5)
		      .attr("r", function(d){return node_scale(d.weight)})
		      .attr("class", "player_node")
		      .style("fill", function(d){
		      	//color all nodes that are either the player or directly similar to player
		      	if (d.weight == 1){
		      		return "#2d790f"
		      	}
		      	//color all other nodes as some other
		      	else {
		      		return "#03c04a"
		      		//return "#b8e4a6"
		      	}
		      });
		  //add the labels
		  //label all nodes that are either the player or directly similar to player
		  important_nodes = node.filter(function(d){return d.weight==1})
		  important_nodes.append("text")
		  	.attr("dx", 10)
		  	.attr("dy", -18)
		  	.style("font-weight", 'bold')
		  	.style("fill", "#000000")
		  	.text(function(d) {return d.name;});
		  // add the curvy lines
		  function tick() {
		      path.attr("d", function(d) {
		          var dx = d.target.x - d.source.x,
		              dy = d.target.y - d.source.y,
		              dr = Math.sqrt(dx * dx + dy * dy);
		          return "M" +
		              d.source.x + "," +
		              d.source.y + "A" +
		              dr + "," + dr + " 0 0,1 " +
		              d.target.x + "," +
		              d.target.y;
		      });

		      node.attr("transform", function(d) {
		          return "translate(" + d.x + "," + d.y + ")"; 
		      });
		  };

		  function dragstarted(d) {
		      if (!d3.event.active) force.alphaTarget(0.3).restart();
		      d.fx = d.x;
		      d.fy = d.y;
		  };

		  function dragged(d) {
		      d.fx = d3.event.x;
		      d.fy = d3.event.y;
		      //pin nodes
		      d.fixed=true;
		  };

		  function dragended(d) {
		      if (!d3.event.active) force.alphaTarget(0);
		      if (d.fixed == true) {
		          d.fx = d.x;
		          d.fy = d.y;
		      }
		      else {
		          d.fx = null;
		          d.fy = null;
		      }
		      d3.select(this).select("circle").style("stroke-width", 50)
		  };

		  //graph drag+zoom stuff
		  function zoom_actions() {
		  	g.attr("transform", d3.event.transform);
		  }
		  var zoom_handler = d3.zoom()
		  	.on("zoom", zoom_actions);
		  zoom_handler(svg);
		  svg.on("dblclick.zoom", null)


		//console.log(links)
	}).catch(function(error) {
	  console.log(error);
	});
});
console.log('league viz oui oui')
var margin = {top:100, right:100, bottom:100, left:100};
var width = 1000;
var height = 500;
var barpad = 2;

var svg = d3.select('#league_viz').append('svg')
	.attr("width", width)
	.attr("height", height)
	.attr("margins", margin);

//scalers
var x = d3.scaleBand()
    .range([margin.left, width - margin.right])
    .padding(.1);
var y = d3.scaleLinear()
	.range([height - margin.bottom, margin.top]);

d3.dsv(',', '/get-league-data', function(d){
	//console.log(d);
	//return {} etc when we figure out what data
	//below is just an example
	return {
		Squad: d['Squad']
		,Season: d['Season']
		,League: d['League']
		,num_Pl: d['# Pl']
	}
}).then(function(data){
	console.log(data);//see data in console

	//example bar chart
	x.domain(data.map(a=>a["Season"]));
	y.domain([0, d3.max(data, function(d){return d["num_Pl"]})]);

	svg.selectAll('rect')
      	.data(data)
      	.enter()
      	.append('rect')
      	.attr("x", function(d) {return x(d['Season'])})
   		.attr("y", function(d){return y(d['num_Pl']);})
   		.attr("width", width / data.length - barpad)
   		.attr("height", function(d){return y(0) - y(d['num_Pl']);})
   		.attr("fill", "steelblue");


}).catch(function(error) {
  console.log(error);
});
var margin = {top:50, right:50, bottom:50, left:50};
var width = 1500-margin.left-margin.right;
var height = 500 - margin.top - margin.bottom;
var barpad = 2;

var svg = d3.select('#league_chart').append('svg')
	.attr("width", width+margin.left+margin.right)
	.attr("height", height+margin.top+margin.bottom)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + (margin.top) + ")")

console.log(document.getElementById("stats").value);

//scalers
var xscale_years = []
for(var i=1988; i<2021; i++){
	xscale_years.push(i)
}
var xscale = d3.scaleBand()
    .range([margin.left, width - margin.right])
		.domain(xscale_years)
    .padding(.1);
var yscale = d3.scaleLinear()
	.range([height, 0]);
var min = 0;
var max = 0;

const yaxis = d3.axisLeft()
    .scale(yscale);

const xaxis = d3.axisBottom()
    .scale(xscale);

d3.dsv(',', '/get-league-chart-data', function(d){
	// console.log(d);
	//return {} etc when we figure out what data
	//below is just an example
	return {
		d
	}
}).then(function(data){
	console.log(data);
	d3.dsv(',', '/get-line-chart-data', function(d){
		return_dict = {League: d['League']}

		for(var i=1988; i<2021; i++){
			return_dict[i] = d[i]
			if(d[i]>max){
				max = d[i]
			}
		}

		return return_dict

	}).then(function(line_data){

		yscale.domain([0, max])

		svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xaxis);

		svg.append("g")
    .attr("class", "y axis")
		.attr("transform", "translate("+margin.left+",0)")
    .call(yaxis);

		var focus = svg.append("g")
            .attr("class", "focus")
            .style("display", "none");
						.attr("width", "10px");
						.attr("height", "10px")

		focus.append("text")
          .attr("class", "league_name")
          .attr("x", 18)
          .attr("y", -2);

		line_data_mod = []
		line_data.forEach((item, i) => {
			league_arr = []
			for(var key in line_data[i]){
				if( key != 'League'){
					league_arr.push({"Season": key, "Value": parseFloat(line_data[i][key])})
				}
			}
			line_data_mod.push(league_arr)
		});

		for(var j=0; j<line_data_mod.length;j++){

			line_data_mod[j].forEach((key, i) => {
				// console.log(key);
				var line = d3.line()
				.x(function(d){return xscale(d['Season'])})
				.y(function(d){return yscale(d['Value'])})

				svg.append("path")
					.data([line_data_mod[j]])
					.attr("class", "line")
					.attr("d", line)
					.style("stroke", "#"+((1<<24)*Math.random()|0).toString(16))
					.style("stroke-width", "2px")
					.style("fill", "none")
					.on('mouseover', function (d, i) {
	          d3.select(this).transition()
	               .duration('50')
	               .attr('opacity', '.85');
						 focus.style("display", null);
						})
					.on('mouseout', function(d,i){
						d3.select(this).transition()
	               .duration('50')
	               .attr('opacity', '1');
						focus.style("display", "none");
					})
					.on
			});
		}
		svg.append("text")
		.attr("transform", "translate(" + (width/2) + ",0)")
		.attr("fill", "black")
		.style("font-weight", "bold")
		.style("font-size", "15px")
		.text("Graphhh")
	})

}).catch(function(error) {
  console.log(error);
});

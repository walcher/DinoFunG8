
/**
 *
 */
    var date_format = d3.time.format("%Y-%m-%d %H:%M:%S");
    var scale_x = d3.scale.linear();
    scale_x.domain([0, 100]);
    scale_x.range([0, 800]);

    var scale_y = d3.scale.linear();
    scale_y.domain([0, 100]);
    scale_y.range([800, 0]);

    var colors = colorbrewer.PuBuGn[9];
    var time_scale = d3.time.scale();
    var time_scale_aux = d3.time.scale();
    var open_time = date_format.parse("2014-6-06 08:00:00");
    var close_time = date_format.parse("2014-6-06 20:30:00");
    time_scale_aux.domain([open_time, close_time]);
    time_scale_aux.range([0,colors.length-1]);
    var time_domain=d3.range(colors.length).map(function(i){return time_scale_aux.invert(i);});
    time_scale.domain(time_domain);
    time_scale.range(colors);

	var t_width=800;
    var t_height=50;
	
	var time_line_scale = d3.time.scale();
    time_line_scale.domain([open_time,close_time]);
    time_line_scale.range([0,t_width]);
	
    var svg = d3.select("#main_svg");
    var scatter = svg.append("g");

	var time_svg = d3.select("#timeline_svg").append("g");
	time_svg.append("rect")
	.attr("class", "grid-background")
	.attr("width", t_width)
	.attr("height", t_height);


	time_svg.append("g")
		.attr("class", "x grid")
		.attr("transform", "translate(0," + t_height + ")")
		.call(d3.svg.axis()
			.scale(time_line_scale)
			.orient("bottom")
			.ticks(d3.time.minutes,15)
			.tickSize(-t_height)
			.tickFormat(""))
	  .selectAll(".tick")
		.classed("minor", function(d) { return d.getMinutes(); });

	time_svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + t_height + ")")
		.call(d3.svg.axis()
		  .scale(time_line_scale)
		  .orient("bottom")
		  .ticks(d3.time.hours)
		  .tickPadding(0))
		.selectAll("text")
		.attr("x", 6)
		.style("text-anchor", null);
	
	var tbrush = d3.svg.brush()
    .x(time_line_scale)
    .on("brushend", t_brushended);

	function t_brushended() {
		var t=tbrush.extent();
		d3.select("#time_interval").html(
				"<p>"+t[0].toLocaleTimeString()+" - "+t[1].toLocaleTimeString()+"</p>"
		)
		
		d3.select("#show_data_button").attr("disabled", null);
	}

	var gBrush = time_svg.append("g")
    .attr("class", "brush")
    .call(tbrush);

	gBrush.selectAll("rect")
    .attr("height", 100);
    function draw_guests_at_time(array) {
    // parse times
	/*
        array.forEach(function (e, i, a) {
            e.time = date_format.parse(e.Timestamp);
        });
*/

        //function draw_time_points() {
			console.log(array.length)
            scatter.selectAll(".dot").data(array.slice(0,array.length)).enter().append("rect").attr("class", "dot")
					.attr("width", function (d) {
                        return (5);
                    })
					.attr("height", function (d) {
                        return (5);
                    })
					.attr("x", function (d) {
                        return scale_x(d.X);
                    })
                    .attr("y", function (d) {
                        return scale_y(d.Y);
                    })
                    .attr("fill", function (d) {
                        return time_scale(d.Time);
                    })
                    .classed("checkin",function(d){return d.type == "check-in";})
                    .append("title").text(function(d){return d.X + ":" + d.Y});
        //}

		
    }




    function read_data() {
		scatter.selectAll(".dot").remove();
		console.log("reading points");
		d3.select("#show_data_button").attr("disabled", true);
		doit();	
    }


	 function doit() {
			var t=tbrush.extent();
			var url = "heatmapdata?endhour=" + t[1].getHours() + ":" + t[1].getMinutes();
			
		
			d3.json(url, function (e, d) {
				console.log(d.array[0]);
				d.array[0].time = date_format.parse(d.array[0].Timestamp);
				d3.select("#clock").text(d.array[0].time.toLocaleTimeString());
				console.log("done " + url);
				draw_guests_at_time(d.array);
				
			});

        }
		
    d3.select("#show_data_button").on("click", read_data);
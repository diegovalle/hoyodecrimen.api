var margin = {top: 10, left: 10, bottom: 10, right: 10}
, width = parseInt(d3.select('#map-homicide').style('width'))
, width = width - margin.left - margin.right
, mapRatio = 1.5
, height = width * mapRatio;
var data, crimeData;
//Extra width for the tooltips
var width = 400,
    height = 500;
comma = d3.format("0,000");


createQuantized=function(domain, name) {
    return(d3.scale.quantize()
        .domain(domain)
        .range(d3.range(9).map(function(i) { return name + i + "-9"; })));

}

var max = d3.max(d3.entries(data), function(d) {
    return d3.max(d3.entries(d.value), function(e) {
        return d3.max(e.value);
    });
});


// findRange=function(name) {
//     var range = d3.extent(d3.entries(crimeData[name]), function(d) {
//         return d3.sum(d.value);
//     });
//     return(range);
// }





var projection = d3.geo.projection(function(x, y) { return [x, y];})
    .precision(0).scale(1).translate([0, 0]);

var path = d3.geo.path()
    .projection(matrix(.4, 0, 0, .4, 0, 25));

function matrix(a, b, c, d, tx, ty) {
    return d3.geo.transform({
        point: function(x, y) { this.stream.point(a * x + b * y + tx, c * x + d * y + ty); }
    });
}

var svgHomicide = d3.select("#map-homicide").append("svg")
    .attr("width", width)
    .attr("height", height);

var svgRNCV = d3.select("#map-rncv").append("svg")
    .attr("width", width)
    .attr("height", height);

var svgRVCV = d3.select("#map-rvcv").append("svg")
    .attr("width", width)
    .attr("height", height);

var svgRVSV = d3.select("#map-rvsv").append("svg")
    .attr("width", width)
    .attr("height", height);

var svgVIOL = d3.select("#map-viol").append("svg")
    .attr("width", width)
    .attr("height", height);

_.sortedFind = function sortedFind(list, item, key) {
    return (item, list[_.sortedIndex(list, item, key)]);
};

tip = function(crimeCode) {
    return(d3.tip()
    .attr('class', 'd3-tip')
    .offset([0, 10])
    .html(function(d) {
        if (topoName === "sectores") {
            obj = _.findWhere(cuadrantesMap.rows, {'sector': d.properties['sector'].toUpperCase(), 'crime':crimeCode.toUpperCase()});
            rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
            return "<span>" + d.properties.sector + (topoName === "sectores" ? "" : " - " + d.properties.cuadrante) +
                " ⇨ " + rate + "</span>";
        }
        else {
            obj = _.findWhere(cuadrantesMap.rows, {'cuadrante': d.properties['cuadrante'].toUpperCase(), 'crime':crimeCode.toUpperCase()});
            rate = obj[topoName === 'cuadrantes' ? 'count' : 'difference'];
            return "<span>" + d.properties.sector + (topoName === "sectores" ? "" : " - " + d.properties.cuadrante) +
                " ⇨ " + rate + "</span>";
        }

    }));
};
tipHom = tip('homicidio doloso');
svgHomicide.call(tipHom);
// tipRNCV = tip('robo a negocio c.v.');
// svgRNCV.call(tipRNCV);
// tipRVCV = tip('robo de vehiculo automotor c.v.')
// svgRVCV.call(tipRVCV);
// tipRVSV = tip('robo de vehiculo automotor s.v.');
// svgRVSV.call(tipRVSV);
// tipVIOL = tip('violacion');
// svgVIOL.call(tipVIOL);

createMap=function(df, svg, crime, crimeCode, colorFun, titleId, chart, topoNam, tipFun, seriesName) {
    type = topoName === "sectores" ? "sectores" : "cuadrantes";
    svg.append("g")
        .attr("class", "subdivisions")
        .selectAll("path")
        .data(topojson.feature(df, df.objects[type]).features)
        .enter().append("path")
        .attr("class", function(d) {

            if (topoName === "sectores") {
                console.time("findmap");
                obj = _.sortedFind(cuadrantesMap.rows,
                                  {'sector': d.properties['sector'].toUpperCase(),
                                   'crime':crimeCode.toUpperCase()},
                                  'sector');
                console.timeEnd("findmap");
                return colorFun(obj['count'] / obj['population'] * 100000 )
            }
            else {
                console.time("findmap");
                obj = _.sortedFind(cuadrantesMap.rows,
                                  {'cuadrante': d.properties['cuadrante'].toUpperCase(),
                                   'crime':crimeCode.toUpperCase()},
                                  'cuadrante');
                console.timeEnd("findmap");
                return colorFun(obj[topoName === 'cuadrantes' ? 'count' : 'difference'] )
            }

        })
        .attr("d", path)
        //.attr("title", function(d) { return +d.properties.sector; })
        .on("mouseover", tipFun.show)
        .on("mouseout", tipFun.hide)
        .on("mousedown", function(d) {
            if(topoName === "sectores")
                var url = "/api/v1/sectores/" + encodeURIComponent(d.properties['sector'].toUpperCase()) + '/crimes';
            else
                var url = "/api/v1/cuadrantes/"+ encodeURIComponent(d.properties['cuadrante'].toUpperCase()) + '/crimes';
            d3.json(url  + '/' + crimeCode + '/series', function(data) {
                series = _.map(data.rows, function(x) {return summer(x)})
                series.unshift(seriesName);
                chart.load({
                    columns: [series],
                });
                d3.select(titleId).text(crime + " / " + d.properties.sector + (topoName === "sectores" ? "" : " / " + d.properties.cuadrante));

            })
            // data = crimeData[crimeCode][d.properties[type]].slice(0);
            //data.unshift(seriesName);
            //chart.load({
            //    columns: [data],
            //});
            });
}


d3.select(self.frameElement).style("height", height + "px");





function createLineChart(selection, totalCrime, labelText, color, dates) {
    name = totalCrime[0];
    var chart1 = c3.generate({
        padding: {
        //    top: 0,
            right: 27,
        //    bottom: 0,
        //    left: 20,
        },
        bindto: selection,
        point: { show: false },
        regions: [
            {start:cuadrantesMap.rows[0].start_period1 + '-15',
             end:cuadrantesMap.rows[0].end_period1 + '-15'},
            {start:cuadrantesMap.rows[0].start_period2 + '-15',
             end:cuadrantesMap.rows[0].end_period2 + '-15',
             class:'foo'}
        ],
        data: {
            x: 'x',
            columns: [
                dates,
                totalCrime
            ],
            //types:{'Homicides':'area',
            //       'Violent robberies to a business':'area'},
            color: function(d) {return color}
        },
        axis: {
            x: {

                type: 'timeseries',
                tick: {count:4,
                       format: '%Y-%B'
                      }
            },
            y: {
                tick : {format: function (d) { return d % 1 == 0 ? d : ""  } },
                min: 0,
                label: {
                    text: labelText,
                    position:'outer-middle'
                },
                padding: {
                    top:0,
                    bottom:0}
            }
        },
        tooltip: {
            format: {
                title: function (d) {
var format = d3.time.format("%Y-%B");
return format(d);
},
                value: function (value, ratio, id) {
                    var format = d3.format('');
                    return format(value);
                }
                //            value: d3.format(',') // apply this format to both y and y2
            }
        }
    });
    return chart1;
}

createLegend=function(selection, colorFun){
    d3.select(selection).selectAll("*").remove();
    var legend = d3.select(selection)
        .append('ul')
        .attr('class', 'list-inline');

    var keys = legend.selectAll('li.key')
        .data(colorFun.range());

    keys.enter().append('li')
        .attr('class', function(d) {return('key ' + String(d))})
        .text(function(d) {
            var r = colorFun.invertExtent(d);
            return d3.round(r[0], 0);
        });
}

// var topoName = 'cuadrantes';
// var mapFile = "js/cuadrantes.json";
// var crimeFile = "js/hom-dol-cuad.js";
d3.json(mapFile, function(error, df) {
    if(topoName == "sectores")
        var url = "/api/v1/sectores/all/crimes/all/period";
    else if (topoName == "cuadrantes")
        var url = "/api/v1/cuadrantes/all/crimes/all/period";
    else
        var url = "/api/v1/cuadrantes/all/crimes/all/period/change";
    d3.json('/api/v1/df/crimes/all/series', function(data) {
        d3.json(url, function(cuadrantes){
            cuadrantesMap =cuadrantes;
        if(topoName == "sectores")
            summer = annualizedRate
        else
            summer = crimeCounts;

            var dates = _.uniq(_.pluck(data.rows, 'date'));
            dates = _.map(dates, function(x) {return x + '-15'});
            dates.unshift("x")

        byCrime = _.groupBy(data.rows, 'crime')
        HomicidesA = _.map(byCrime['HOMICIDIO DOLOSO'], function(x) {return summer(x)})
        HomicidesA.unshift('Homicides')
        // rncvA = _.map(byCrime['ROBO A NEGOCIO C.V.'], function(x) {return summer(x)})
        // rncvA.unshift('Violent robberies to a business')
        // rvcvA = _.map(byCrime['ROBO DE VEHICULO AUTOMOTOR C.V.'], function(x) {return summer(x)})
        // rvcvA.unshift('Violent car robberies')
        // rvsvA = _.map(byCrime['ROBO DE VEHICULO AUTOMOTOR S.V.'], function(x) {return summer(x)})
        // rvsvA.unshift('Non-violent car robberies')
        // violA = _.map(byCrime['VIOLACION'], function(x) {return summer(x)})
        // violA.unshift('Rape')

        chartHomicides = createLineChart('#chart-homicide',
                                         HomicidesA,
                                         crimePrefix + 'homicides',
                                         'rgb(203,24,29)', dates)

        // chartrncv = createLineChart('#chart-rncv',
        //                             rncvA,
        //                             crimePrefix + 'violent robberies to a business','rgb(8,48,107)',dates )

        // chartrvcv = createLineChart('#chart-rvcv',
        //                                 rvcvA,
        //                             crimePrefix + 'violent car robberies','rgb(63,0,125)', dates)

        // chartrvsv = createLineChart('#chart-rvsv',
        //                             rvsvA,
        //                             crimePrefix + 'non-violent car robberies','rgb(0,68,27)', dates)

        // chartviol = createLineChart('#chart-viol',
        //                             violA,
        //                             crimePrefix + 'rapes','rgb(0,0,0)', dates)


        findRange=function(name) {
            name = name.toUpperCase();
            var ext = d3.extent(cuadrantesMap.rows, function(d) {
                if(d.crime === name) {
                    if(topoName === "sectores")
                        if(d.population)
                            return d.count / d.population * 100000;
                        else
                            return 0;
                    else if (topoName === "cuadrantes")
                        if(d.population)
                            return d.count
                        else
                            return 0;
                    else
                        if(d.population)
                            return d.difference;
                        else
                            return 0;
                }
            });
            if(ext[0] < 0)
                if(Math.abs(ext[0])> ext[1]) {
                    return([ext[0], 0, Math.abs(ext[0])])
                } else
                    return([-ext[1], 0, ext[1]]);
            else
                return(ext);
        }

        //crimeData=data

        if(topoName==="cuadrantes-change"){
            var monthNames = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
            var start_period1 = new Date(cuadrantesMap.rows[0].start_period1 + '-15');
            var start_period2 = new Date(cuadrantesMap.rows[0].start_period2 + '-15');
            var end_period1 = new Date(cuadrantesMap.rows[0].end_period1 + '-15');
            var end_period2 = new Date(cuadrantesMap.rows[0].end_period2 + '-15');
            var dates = monthNames[start_period1.getMonth()] + ' ' + start_period1.getFullYear() + ' - ' + monthNames[end_period1.getMonth()]  + ' ' + end_period1.getFullYear()+ ' to ' + monthNames[start_period2.getMonth()] + ' ' + start_period2.getFullYear() + ' - ' + monthNames[end_period2.getMonth()]  + ' ' + end_period2.getFullYear()
            d3.select('#hom-date').text('change in homicides ' + dates);
            // d3.select('#rncv-date').text('change in violent robberies to a business ' + dates);
            // d3.select('#rvcv-date').text('change in violent car robberies ' + dates);
            // d3.select('#rvsv-date').text('change in non-violent car robberies ' + dates);
            // d3.select('#viol-date').text('change in rapes ' + dates);
        } else {
            var monthNames = [ "January", "February", "March", "April", "May", "June",
                               "July", "August", "September", "October", "November", "December" ];
            var startDate = new Date(cuadrantesMap.rows[0].start_date + '-15');
            var endDate = new Date(cuadrantesMap.rows[0].end_date + '-15');
            var dates = monthNames[startDate.getMonth()] + ' ' + startDate.getFullYear() + ' to ' + monthNames[endDate.getMonth()] + ' ' +  endDate.getFullYear();
            d3.select('#hom-date').text((topoName == "sectores" ? 'homicide rate from ' : 'total homicides from ') + dates);
            // d3.select('#rncv-date').text((topoName == "sectores" ?'violent robbery to a business rate from ' : 'total (violent robberies to a business rate from') + dates);
            // d3.select('#rvcv-date').text((topoName == "sectores" ?'violent car robbery rate from ' : 'total violent car robberies from ') + dates);
            // d3.select('#rvsv-date').text((topoName == "sectores" ?'non-violent car robbery rate from ': 'total non-violent car robberies from ') + dates);
            // d3.select('#viol-date').text((topoName == "sectores" ?'rape rate from ' : 'total rapes from ') + dates);
        }
        quantizeRed = createQuantized(findRange('homicidio doloso'), mapColors.hom)
        // quantizeBlue = createQuantized(findRange('robo a negocio c.v.'), mapColors.rncv)
        // quantizePurple = createQuantized(findRange('robo de vehiculo automotor c.v.'), mapColors.rvcv)
        // quantizeGreen = createQuantized(findRange('robo de vehiculo automotor s.v.'), mapColors.rvsv)
        // quantizeGray = createQuantized(findRange('violacion'), mapColors.viol)
        createMap(df, svgHomicide, 'Homicides','homicidio doloso', quantizeRed, '#homicide-title', chartHomicides, topoName, tipHom, HomicidesA[0]);
        // createMap(df, svgRNCV, 'Violent robberies to a business', 'robo a negocio c.v.', quantizeBlue, '#rncv-title', chartrncv, topoName, tipRNCV, rncvA[0]);
        // createMap(df, svgRVCV, 'Violent car robberies', 'robo de vehiculo automotor c.v.', quantizePurple, '#rvcv-title', chartrvcv, topoName, tipRVCV, rvcvA[0]);
        // createMap(df, svgRVSV, 'Non-violent car robberies', 'robo de vehiculo automotor s.v.', quantizeGreen, '#rvsv-title', chartrvsv, topoName, tipRVSV, rvsvA[0]);
        // createMap(df, svgVIOL, 'Rape', 'violacion', quantizeGray, '#viol-title', chartviol, topoName, tipVIOL, violA[0]);
        createLegend('#legend-homicides', quantizeRed)
        // createLegend('#legend-rncv', quantizeBlue)
        // createLegend('#legend-rvcv', quantizePurple)
        // createLegend('#legend-rvsv', quantizeGreen)
        // createLegend('#legend-viol', quantizeGray)


    });

    });


});

annualizedRate = function(x) {
    return Math.round(x.count / x.population * 100000 * 12 * 10)/10
}

crimeCounts = function(x) {
    return x.count
}

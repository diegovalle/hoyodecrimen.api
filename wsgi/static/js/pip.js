var cuadsGeojson, singleGeojson, polygonCuads= [], pipCuad =[],
    polygonSectors = [], sectorsGeojson, map, pipData;
var cuadsLayer, sectorsLayer, singleLayer;
var latLng;
var chartHomicides, chartrncv,
    chartrvcv,chartrvsv,chartviol,
    barHomicides,
    crimeData;
var crime = {hom:[],rncv:[],
             rvcv:[], rvsv:[],
             viol:[], rccv:[],
             rtcv:[], rtsv:[]};
var crimeCompare = {hom:0,rncv:0,
                    rvcv:0, rvsv:0,
                    viol:0,
                    rccv:0, rtcv:0,rtsv:0};
var allDF = {hom:0,rncv:0,
             rvcv:0, rvsv:0,
             viol:0,
             rccv:0, rtcv:0,rtsv:0};
var sql_statement;
var last3Months_sql = "SELECT sum(count) as count,sum(population)/3 as population, crime FROM cuadrantes where cuadrante='C-1.1.1' and (date='2014-07-01' OR date='2014-06-01' or date='2014-05-01') GROUP BY crime"
L.Icon.Default.imagePath = '/js/images';
var comma = d3.format("0,000")


        $.getJSON('/js/df-outline.json', function (single) {
            var southWest = L.latLng(19.152952023808638, -99.55192565917969),
            northEast = L.latLng(19.597959855171077, -98.67919921875),
                bounds = L.latLngBounds(southWest, northEast);
            map = L.map('map', {
                maxBounds: bounds,
                maxZoom: 19,
                minZoom: 10
            });

            function get_location() {
                if (Modernizr.geolocation) {
                    navigator.geolocation.
                        getCurrentPosition(geoSuccess, geoError,
                                           {enableHighAccuracy:true,
                                            maximumAge: 18000,
                                            timeout: 5000});
                } else {
                    map.setView([lat, lng], 14)
                    createMarker(lat, lng)
                }
            }
            // if (geoPosition.init()) {
            //     geoPosition.getCurrentPosition(geoSuccess, geoError,
            //                                    {enableHighAccuracy:true});
            // }
            // else{
            //     map.setView([lat, lng], 15)
            //     createMarker(lat, lng)
            // }
            function geoSuccess(p) {
                latLng = {
                    lat:p.coords.latitude,
                    lng:p.coords.longitude
                };
                map.setView([latLng.lat, latLng.lng], 14);
                createMarker(latLng.lat, latLng.lng)
            }
            function geoError() {
                if(!latLng){
                    latLng = {
                        lat: 19.432605540309215,
                        lng: -99.133208
                    };
                    map.setView([latLng.lat, latLng.lng], 14)
                    createMarker(latLng.lat, latLng.lng)
                }
            }
            get_location();
            setTimeout(function () {
                if(!latLng){
                    window.console.log("No confirmation from user, using fallback");
                    geoError();
                }else{
                    window.console.log("Location was set");
                }
            }, 5000+ 1000);

	    L.tileLayer('https://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/normal.day/{z}/{x}/{y}/256/png8?app_id=2xIqG1pjt7OdQnzqAHmm&app_code=t0G_EMNWEWEpFEIoJYEncg', {
	        attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
	        subdomains: '1234',
	        mapID: 'newest',
	        app_id: '2xIqG1pjt7OdQnzqAHmm',
	        app_code: 't0G_EMNWEWEpFEIoJYEncg',
	        base: 'base',
	        minZoom: 0,
	        maxZoom: 20
            }).addTo(map);

            var myStyle = {
                "color": "red",
                "fillColor": "#fff",
                "weight": 2,
                "opacity": 1
            };
            singleGeojson = topojson.feature(single, single.objects.single).features;
            L.geoJson(singleGeojson, {
                style: myStyle
            }).addTo(map);
            //sectorsGeojson = topojson.feature(secs, secs.objects.sectores).features;
            //cuadsGeojson = topojson.feature(cuads, cuads.objects.cuadrantes).features;
            //map.on('locationfound', onLocationFound);
            //map.locate({setView: true});
        });




function get_data(data, dates){

    var filterCrime = function(data, crime) {
        data = _.filter(data, { 'crime': crime });
        data = MG.convert.date(data, 'date', '%Y-%m');
        return (data);
    };
    var filterBar = function(df_period, cuadrante_period, crime) {
        df_period = _.filter(df_period, { 'crime': crime });
        df_period = df_period[0]["count"] / df_period[0]["population"] * 100000;
        cuadrante_period = _.filter(cuadrante_period, { 'crime': crime });
        cuadrante_period = cuadrante_period[0]["count"] / cuadrante_period[0]["population"] * 100000
        return ([{'label': all_df_txt, 'value': df_period, 'baseline': 0},
                {'label':'Cuadrante', 'value': cuadrante_period, 'baseline': 0}]);
    };
    var bar_options = {
        title: "Bar Prototype",
        x_label : rate_txt,
        bottom: 50,
        baseline_accessor: 'baseline',
        //data: bar_data,
        chart_type: 'bar',
        x_accessor: 'value',
        y_accessor: 'label',
        width: 650,
        height: 150,
        full_width: true,
        target: '#bar1',
    };
    var line_options = {
        title: "Homicides",
        width: 650,
        height: 150,
        y_label: count_txt,
        bottom: 40,
        full_width: true,
        interpolate: "linear",
        target: '#homicidios',
        x_accessor: 'date',
        y_accessor: 'count',
        xax_count: 4
    };
    crimes = _.uniq(_.pluck(data.cuadrante, 'crime'));
    _.map(crimes, function(x) {
        if (document.getElementById('line' + x.replace(/ /g, '-').replace(/\./g, '-')) === null) {
            $('<div id="'+ 'line' + x.replace(/ /g, '-').replace(/\./g, '-') +'"></div>').appendTo('#linecharts');
            $('<div id="'+ 'bar' + x.replace(/ /g, '-').replace(/\./g, '-') +'"></div>').appendTo('#barcharts');
        }
    });
    _.map(crimes, function(x) {
        line_values = filterCrime(data.cuadrante, x);
        bar_values = filterBar(data.df_period, data.cuadrante_period, x);
        line_options.data = line_values;
        line_options.title = x;
        line_options.target = "#line" + x.replace(/ /g, '-').replace(/\./g, '-');
        bar_options.data = bar_values;
        bar_options.title = x;
        bar_options.target = "#bar" + x.replace(/ /g, '-').replace(/\./g, '-');
        MG.data_graphic(line_options);
        MG.data_graphic(bar_options);
        return
    });
    // var i = 0;
//     crime.hom.length = 0;
//     crime.rncv.length = 0;
//     crime.rvcv.length = 0;
//     crime.rvsv.length = 0;
//     crime.viol.length = 0;
//     crime.hom.push(hom_txt);
//     crime.rncv.push(rncv_txt);
//     crime.rvcv.push(rvcv_txt);
//     crime.rvsv.push(rvsv_txt);
//     crime.viol.push(viol_txt);
//     crime.rtcv.push(rtcv_txt);
//     crime.rtsv.push(rtsv_txt);
//     crime.rccv.push(rccv_txt);
//     $.each(data.cuadrante, function(i, value){
//         switch(value.crime) {
//         case "HOMICIDIO DOLOSO":
//             crime.hom.push(value.count);
//             break;
//         case "ROBO A NEGOCIO C.V.":
//             crime.rncv.push(value.count);
//             break;
//         case "ROBO DE VEHICULO AUTOMOTOR C.V.":
//             crime.rvcv.push(value.count);
//             break;
//         case "ROBO DE VEHICULO AUTOMOTOR S.V.":
//             crime.rvsv.push(value.count);
//             break;
//         case "VIOLACION":
//             crime.viol.push(value.count);
//             break;
//         case "ROBO A TRANSEUNTE C.V.":
//             crime.rtcv.push(value.count);
//             break;
//         case "ROBO A TRANSEUNTE S.V.":
//             crime.rtsv.push(value.count);
//             break;
//         case "ROBO A CASA HABITACION C.V.":
//             crime.rccv.push(value.count);
//             break;
//         }
//     });
//         //len = crime.hom.length;
//     //crimeCompare.hom = 0
//         //for(var i=crime.hom.length;i>(crime.hom.length-11);i--)
//         //    crimeCompare.hom += crime.hom[i-1]
     var cuad_last = _.indexBy(data.cuadrante_period, 'crime')
//     var totals = _.indexBy(data.df_period, 'crime')
//     crimeCompare.hom  = Math.round(cuad_last['HOMICIDIO DOLOSO'].count / cuad_last['HOMICIDIO DOLOSO'].population * Math.pow(10,5) * 10) / 10
//     allDF.hom =  Math.round(totals['HOMICIDIO DOLOSO'].count / totals['HOMICIDIO DOLOSO'].population * Math.pow(10,5) * 10) / 10

//     crimeCompare.rncv  = Math.round(cuad_last['ROBO A NEGOCIO C.V.'].count / cuad_last['ROBO A NEGOCIO C.V.'].population * Math.pow(10,5) * 10) / 10
//     allDF.rncv =  Math.round(totals['ROBO A NEGOCIO C.V.'].count / totals['ROBO A NEGOCIO C.V.'].population * Math.pow(10,5) * 10) / 10

//     crimeCompare.rvcv  = Math.round(cuad_last['ROBO DE VEHICULO AUTOMOTOR C.V.'].count / cuad_last['ROBO DE VEHICULO AUTOMOTOR C.V.'].population * Math.pow(10,5) * 10) / 10
//     allDF.rvcv =  Math.round(totals['ROBO DE VEHICULO AUTOMOTOR C.V.'].count / totals['ROBO DE VEHICULO AUTOMOTOR C.V.'].population * Math.pow(10,5) * 10) / 10

//     crimeCompare.rvsv  = Math.round(cuad_last['ROBO DE VEHICULO AUTOMOTOR S.V.'].count / cuad_last['ROBO DE VEHICULO AUTOMOTOR S.V.'].population * Math.pow(10,5) * 10) / 10
//     allDF.rvsv =  Math.round(totals['ROBO DE VEHICULO AUTOMOTOR S.V.'].count / totals['ROBO DE VEHICULO AUTOMOTOR S.V.'].population * Math.pow(10,5) * 10) / 10

//     crimeCompare.viol  = Math.round(cuad_last['VIOLACION'].count / cuad_last['VIOLACION'].population * Math.pow(10,5) * 10) / 10
//     allDF.viol =  Math.round(totals['VIOLACION'].count / totals['VIOLACION'].population * Math.pow(10,5) * 10) / 10

// // set the population and cuadrante
     $("#poblacion").text(comma(cuad_last['HOMICIDIO DOLOSO'].population))
     $("#cuadrante").text(data.pip[0].cuadrante)
     $("#sector").text(data.pip[0].sector)

//     chartHomicides.load({
//         columns: [crime.hom],
//     });
//     chartrncv.load({
//         columns: [crime.rncv],
//     });
//     chartrvcv.load({
//         columns: [crime.rvcv],
//     });
//     chartrvsv.load({
//         columns: [crime.rvsv],
//     });
//     chartviol.load({
//         columns: [crime.viol],
//     });
//     barHomicides.load({
//         columns: [[all_df_txt, allDF.hom],[hom_txt, crimeCompare.hom]],
//     });
//     barRNCV.load({
//         columns: [[all_df_txt, allDF.rncv],[rncv_txt, crimeCompare.rncv]],
//     })
//     barRVCV.load({
//         columns: [[all_df_txt, allDF.rvcv],[rvcv_txt, crimeCompare.rvcv]],
//     });
//     barRVSV.load({
//         columns: [[all_df_txt, allDF.rvsv],[rvsv_txt, crimeCompare.rvsv]],
//     });
//     barVIOL.load({
//         columns: [[all_df_txt, allDF.viol],[viol_txt, crimeCompare.viol]],
//     });


}

function createMarker(lat, lng) {

    //Check if the location is inside the DF
    singleLayer = L.geoJson(singleGeojson);
    isDF = leafletPip.pointInLayer(L.latLng(lat,lng), singleLayer, true);
    if(!isDF[0]){
        lat= 19.432605540309215;
        lng= -99.133208;
    }

    marker = new L.marker([lat, lng], {draggable: true});
    marker.on('dragend', function(event){
        var marker = event.target;
        var position = marker.getLatLng();

        $.getJSON('/api/v1/cuadrantes/crimes/all/pip/' +marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
            var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
            dates = _.map(dates, function(x) {return x + '-15'});
            dates.unshift("x")
            if(pipCuad)
                map.removeLayer(pipCuad);
            pipCuad = L.geoJson(JSON.parse(data.pip[0].geometry))
            if(pipCuad)
                pipCuad.addTo(map);
            pipData = data;
            get_data(pipData, dates);
        });


        //}
    });
    cuadsLayer = L.geoJson(cuadsGeojson);
    sectorsLayer = L.geoJson(sectorsGeojson);
    //polygonCuads = leafletPip.pointInLayer(marker.getLatLng(), cuadsLayer, true);
    //sql_statement = "SELECT count, date, crime, population FROM cuadrantes where cuadrante='"+ polygonCuads[0].feature.id + "' ORDER BY crime,date";
    marker.addTo(map);
       //$.each(sectorsLayer._layers, function(i, value){
    //    if(value.feature.id == polygonCuads[0].feature.properties.sector)
    //        polygonSectors[0] = value
    //});
    //polygonCuads[0].addTo(map);
    //polygonSectors[0].setStyle({fillColor: '#fff',color: '#000', opacity:1})
    //polygonSectors[0].addTo(map);
    $.getJSON('/api/v1/cuadrantes/crimes/all/pip/' +marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
        var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
        dates = _.map(dates, function(x) {return x + '-15'});
        dates.unshift("x")
        // chartHomicides = createLineChart('#chart-homicide',
    //                                  HomicidesA,
    //                                  'number of homicides',
    //                                  'rgb(203,24,29)', dates);
    // barHomicides = createBarChart("#barchart-homicide", 10, 'rgb(203,24,29)', hom_txt);
    // chartrncv = createLineChart('#chart-rncv',
    //                             rncvA,
    //                             'number of violent robberies to a business','rgb(8,48,107)', dates );
    // barRNCV = createBarChart("#barchart-rncv", 10, 'rgb(8,48,107)', rncv_txt);

    // chartrvcv = createLineChart('#chart-rvcv',
    //                             rvcvA,
    //                             'number of violent car robberies','rgb(63,0,125)', dates)
    // barRVCV = createBarChart("#barchart-rvcv", 10, 'rgb(63,0,125)', rvcv_txt);
    // chartrvsv = createLineChart('#chart-rvsv',
    //                             rvsvA,
    //                             'number of non-violent car robberies','rgb(0,68,27)', dates)
    // barRVSV = createBarChart("#barchart-rvsv", 10, 'rgb(0,68,27)', rvsv_txt);

    // chartviol = createLineChart('#chart-viol',
    //                             violA,
    //                             'number of rapes','rgb(0,0,0)', dates)
    // barVIOL = createBarChart("#barchart-viol", 10, 'rgb(0,0,0)', viol_txt);

        pipCuad = L.geoJson(JSON.parse(data.pip[0].geometry))
        if(pipCuad)
            pipCuad.addTo(map);
        pipData = data;
        get_data(pipData, dates);
    });
    // data = crimeData['hom'][polygonSectors[0].feature.id].slice(0);
    // data.unshift('Sector homicide rate');
    // chartHomicides.load({
    //     columns: [data],
    // });
    /*L.circle(e.latlng, radius).addTo(map);
      map.initlat = e.latlng.lat;
      map.initlng = e.latlng.lng;*/
    // Modify the line chart

    //d3.select("#homicide-title").text(polygonSectors[0].feature.id);
}

function createBarChart(selection, DFRate, color, cuad_txt){
    var chart = c3.generate({
        bindto: selection,
        data: {
            columns: [
                [all_df_txt, DFRate],
                [cuad_txt, 0]
            ],
            type: 'bar',
            colors: {
                "All DF": "#444",
                "Todo DF": "#444",
                "Cuadrante Homicides":color,
                "Cuadrante Violent robberies to a business":color,
                'Cuadrante Vehicle robberies with violence':color,
                'Cuadrante Vehicle robberies without violence':color,
                'Cuadrante Rape':color,
                'Cuadrante - Homicidios': color,
                'Cuadrante - Robo a Negocio C.V.': color,
                'Cuadrante - Robo de Vehículo C.V': color,
                'Cuadrante - Robo de Vehículo S.V.': color,
                'Cuadrante - Violaciones': color
                }
        },
        bar: {
            width: {
                ratio: 0.5 // this makes bar width 50% of length between ticks
            }
            // or
            //width: 100 // this makes bar width 100px
        },
        axis:{
            y:{
                min:-7,
                tick : {format: function (d) {  return ((d % 100 == 0 & d != 0)| d == 10 ) ? d : ""   } },
                label: {
                    text: rate_txt,
                    position:'outer-middle'
                }
            }
        },
        tooltip: {
            format: {
                value: function (value, ratio, id) {
                    return value //+', '+ crimeCompare.hom;
                }
                //            value: d3.format(',') // apply this format to both y and y2
            }
        }
    });
    return(chart);
}

function createLineChart(selection, totalCrime, labelText, color, dates) {
    name=totalCrime[0];
    var chart1 = c3.generate({

        padding: {
        //    top: 0,
            right: 30,
        //    bottom: 0,
        //    left: 20,
        },
        transition: { duration: 0 },
        bindto: selection,
        point: { show: false },
        regions: [
            {start:"2013-05-15", end:"2013-07-15"},
            {start:"2014-05-15", end:"2014-07-15", class:'foo'}
        ],
        data: {
            x: 'x',
            columns: [
                dates,
                [name,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ],
            colors: {
                "Cuadrante Homicides":color,
                "Cuadrante Violent robberies to a business":color,
                'Cuadrante Vehicle robberies with violence':color,
                'Cuadrante Vehicle robberies without violence':color,
                'Cuadrante Rape':color,
                'Cuadrante - Homicidios': color,
                'Cuadrante - Robo a Negocio C.V.': color,
                'Cuadrante - Robo de Vehículo C.V': color,
                'Cuadrante - Robo de Vehículo S.V.': color,
                'Cuadrante - Violaciones': color
            }
            //types:{'Homicides':'area',
            //       'Violent robberies to a business':'area'},
            //color: function(d)  {
                // d will be 'id' when called for legends
               // return d.id && d.id === 'DF homicide rate' ? d3.rgb(color).darker(color / 150) : color;
            //}
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
                    text: count_txt,
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
            }
        }
    });
    return chart1;
}


HomicidesA = [hom_txt, 62, 81, 89, 76, 97, 90, 59, 78, 60, 68, 60, 58, 69, 54, 90, 76, 62, 78, 70 ], rncvA = [rncv_txt, 389, 355, 355, 297, 328, 361, 379, 363, 348, 374, 420, 348, 306, 270, 248, 278, 260, 287, 365 ], rvcvA = [rvcv_txt, 488, 492, 432, 434, 503, 487, 470, 501, 457, 587, 612, 510, 560, 493, 506, 474, 507, 457, 544 ], rvsvA = [rvsv_txt, 944, 851, 850, 912, 949, 990, 930, 990, 903, 917, 971, 931, 980, 825, 864, 803, 884, 708, 807 ], violA = [viol_txt, 64, 64, 46, 34, 40, 36, 45, 46, 27, 44, 34, 33, 23, 35, 46, 41, 51, 38, 43 ];




// data = crimeData[crimeCode][d.properties[type]].slice(0);
// data.unshift(seriesName);
// chart.load({
//     columns: [data],
// });
// d3.select(titleId).text(crime + " / " + d.properties.sector + (topoName === "sectores" ? "" : " / " + d.properties.id));

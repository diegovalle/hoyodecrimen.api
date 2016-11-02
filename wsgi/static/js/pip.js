var cuadsGeojson, singleGeojson, polygonCuads = [], pipCuad = [],
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
var circles = [];
charts_url = '/api/v1/cuadrantes/crimes/HOMICIDIO DOLOSO,LESIONES POR ARMA DE FUEGO,ROBO DE VEHICULO AUTOMOTOR S.V.,ROBO DE VEHICULO AUTOMOTOR C.V.,ROBO A TRANSEUNTE C.V./pip_extra/';

$.getJSON('/js/df-outline.json', function (single) {
    var southWest = L.latLng(19.081966, -99.569838),
        northEast = L.latLng(19.779954, -98.690870),
        bounds = L.latLngBounds(southWest, northEast);
    map = L.map('map', {
        maxBounds: bounds,
        maxZoom: 19,
        minZoom: 10,
        fullscreenControl: {
          pseudoFullscreen: true // if true, fullscreen to page width and height
        }
    });
    

    function get_location() {
        if (Modernizr.geolocation) {
            navigator.geolocation.
                getCurrentPosition(geoSuccess, geoError,
                                   {enableHighAccuracy:true,
                                    maximumAge: 18000,
                                    timeout: 15000});
        } else {
            map.setView([lat, lng], 15)
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
        map.setView([latLng.lat, latLng.lng], 15);
        createMarker(latLng.lat, latLng.lng)
    }
    function geoError() {
        if(!latLng){
            latLng = {
                lat: 19.432605540309215,
                lng: -99.133208
            };
            map.setView([latLng.lat, latLng.lng], 15)
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
    }, 15000);

    L.tileLayer('https://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/normal.day/{z}/{x}/{y}/256/png8?app_id=2xIqG1pjt7OdQnzqAHmm&app_code=t0G_EMNWEWEpFEIoJYEncg', {
        attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
        subdomains: '1234',
        mapID: 'newest',
        app_id: '2xIqG1pjt7OdQnzqAHmm',
        app_code: 't0G_EMNWEWEpFEIoJYEncg',
        base: 'base',
        minZoom: 0,
        maxZoom: 23
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
                 {'label':your_cuadrante, 'value': cuadrante_period, 'baseline': 0}]);
    };

    crimes = _.uniq(_.pluck(data.cuadrante, 'crime'));
    crimes = _.sortBy(crimes,
                      function(x) {
                          if (x === "HOMICIDIO DOLOSO")
                              return -5;
                          if (x === "ROBO DE VEHICULO AUTOMOTOR C.V.")
                              return -3;
                          if (x === "ROBO DE VEHICULO AUTOMOTOR S.V.")
                              return -1;
                          if (x === "ROBO A TRANSEUNTE C.V.")
                              return 3;
                          return 9999;
                      });
    _.map(crimes, function(x) {
        if (document.getElementById('line' + x.replace(/ /g, '-').replace(/\./g, '-')) === null) {
            $('<div id="'+ 'line' + x.replace(/ /g, '-').replace(/\./g, '-') +'"></div>').appendTo('#linecharts');
            $('<div id="'+ 'bar' + x.replace(/ /g, '-').replace(/\./g, '-') +'"></div>').appendTo('#barcharts');
        }
    });

    _.map(crimes, function(x) {
        var bar_options = {
            title: "Bar Prototype",
            x_label : rate_txt,
            bottom: 50,
            left: 80,
            baseline_accessor: 'baseline',
            //data: bar_data,
            chart_type: 'bar',
            x_accessor: 'value',
            y_accessor: 'label',
            width: 650,
            height: 150,
            full_width: true,
            target: '#bar1',
            xax_count: 3
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
            xax_count: 3,
            yax_count: 2
        };
        line_values = filterCrime(data.cuadrante, x);
        bar_values = filterBar(data.df_period, data.cuadrante_period, x);
        line_options.data = line_values;
        line_options.title = x;
        line_options.target = "#line" + x.replace(/ /g, '-').replace(/\./g, '-');
        line_options.mouseover = function(d, i) {
            var target = line_options.target;
            var date = new Date(d.date);
            var day = d.date.getDate();
            var monthIndex = d.date.getMonth();
            var year = d.date.getFullYear();
            d3.select(target + ' text.mg-active-datapoint')
                .text( d3.time.format('%b %Y')(date) +
                       ', ' + count_txt + ': ' + comma(d.count));
        };;
        bar_options.data = bar_values;
        bar_options.title = x;
        bar_options.target = "#bar" + x.replace(/ /g, '-').replace(/\./g, '-');
        MG.data_graphic(line_options);
        MG.data_graphic(bar_options);
        return
    });

    //var cuad_last = _.indexBy(data.cuadrante_period, 'crime')


    $("#poblacion").text(comma(data.cuadrante[0].population))
    $("#cuadrante").text(data.pip[0].cuadrante)
    $("#sector").text(data.pip[0].sector)



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

        $.getJSON(charts_url +marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
            var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
            dates = _.map(dates, function(x) {return x + '-15'});
            dates.unshift("x")
            if(pipCuad)
                map.removeLayer(pipCuad);
            pipCuad = L.geoJson(JSON.parse(data.pip[0].geometry), {
                "fillColor": "yellow",
                "color": "black",
                "weight": 4,
                "opacity": .7,
                "fillOpacity": 0.1
            })
            if(pipCuad)
                pipCuad.addTo(map);
            pipData = data;
            get_data(pipData, dates);
            while(circles.length > 0) {
                map.removeLayer(circles.pop())
            }
            for (var i = 0; i < data.latlong.length; i++) {
                circle_color = "darkgray"
                if (data.latlong[i].crime == "ROBO A TRANSEUNTE C.V.")
                    circle_color = "#377eb8"
                if (data.latlong[i].crime == "ROBO DE VEHICULO AUTOMOTOR C.V.")
                    circle_color = "#00441b"
                if (data.latlong[i].crime == "ROBO DE VEHICULO AUTOMOTOR S.V.")
                    circle_color = "#41ab5d"
                if (data.latlong[i].crime == "HOMICIDIO DOLOSO")
                    circle_color = "#e41a1c"
                circle = new L.circle(L.latLng(data.latlong[i].lat, data.latlong[i].long),
                                      20, { fillOpacity: .7, color: circle_color, weight: 1 })
                    .bindPopup(data.latlong[i].crime + '<br>' + data.latlong[i].date + '<br>' + data.latlong[i].hour +
                               (data.latlong[i].hour < "12" ? ' AM' : ' PM'))
                    .addTo(map);
                circles.push(circle)
            }
        });


        //}
    });
    cuadsLayer = L.geoJson(cuadsGeojson);
    sectorsLayer = L.geoJson(sectorsGeojson);

    marker.addTo(map);

    $.getJSON(charts_url + marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
        var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
        dates = _.map(dates, function(x) {return x + '-15'});
        dates.unshift("x")


        pipCuad = L.geoJson(JSON.parse(data.pip[0].geometry), {
            "fillColor": "yellow",
            "color": "black",
            "weight": 4,
            "opacity": .7,
            "fillOpacity": 0.1
        })
        if(pipCuad)
            pipCuad.addTo(map);
        pipData = data;
        get_data(pipData, dates);
        while(circles.length > 0) {
            map.removeLayer(circles.pop())
        }
        for (var i = 0; i < data.latlong.length; i++) {
            circle_color = "darkgray"
            if (data.latlong[i].crime == "ROBO A TRANSEUNTE C.V.")
                circle_color = "#377eb8"
            if (data.latlong[i].crime == "ROBO DE VEHICULO AUTOMOTOR C.V.")
                circle_color = "#00441b"
            if (data.latlong[i].crime == "ROBO DE VEHICULO AUTOMOTOR S.V.")
                circle_color = "#41ab5d"
            if (data.latlong[i].crime == "HOMICIDIO DOLOSO")
                circle_color = "#e41a1c"
            circle = new L.circle(L.latLng(data.latlong[i].lat, data.latlong[i].long),
                                  20, { fillOpacity: .7, color: circle_color, weight: 1 })
                .bindPopup(data.latlong[i].crime + '<br>' + data.latlong[i].date + '<br>' + data.latlong[i].hour +
                           (data.latlong[i].hour < "12" ? ' AM' : ' PM'))
                .addTo(map);
            circles.push(circle)
        }
    });

    // There's a weird bug where the map has a red border
    $('.leaflet-clickable').first().attr({'stroke': '#7f0000'});
}

HomicidesA = [hom_txt, 62, 81, 89, 76, 97, 90, 59, 78, 60, 68, 60, 58, 69, 54, 90, 76, 62, 78, 70 ], rncvA = [rncv_txt, 389, 355, 355, 297, 328, 361, 379, 363, 348, 374, 420, 348, 306, 270, 248, 278, 260, 287, 365 ], rvcvA = [rvcv_txt, 488, 492, 432, 434, 503, 487, 470, 501, 457, 587, 612, 510, 560, 493, 506, 474, 507, 457, 544 ], rvsvA = [rvsv_txt, 944, 851, 850, 912, 949, 990, 930, 990, 903, 917, 971, 931, 980, 825, 864, 803, 884, 708, 807 ], violA = [viol_txt, 64, 64, 46, 34, 40, 36, 45, 46, 27, 44, 34, 33, 23, 35, 46, 41, 51, 38, 43 ];

$(window).load(function() {
    $("#linechartstext").height($("#barchartstext").height());
});

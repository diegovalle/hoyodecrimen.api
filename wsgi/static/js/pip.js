var cuadsGeojson, singleGeojson, polygonCuads = [], pipCuad = [],
    polygonSectors = [], sectorsGeojson, map, pipData;
var cuadsLayer, sectorsLayer, singleLayer;
var latLng;
var chartHomicides, chartrncv,
    chartrvcv, chartrvsv, chartviol,
    barHomicides,
    crimeData;
var crime = {hom: [], rncv: [],
             rvcv: [], rvsv: [],
             viol: [], rccv: [],
             rtcv: [], rtsv: []};
var crimeCompare = {hom: 0, rncv: 0,
                    rvcv: 0, rvsv: 0,
                    viol: 0,
                    rccv: 0, rtcv: 0, rtsv: 0};
var allDF = {hom: 0, rncv: 0,
             rvcv: 0, rvsv: 0,
             viol: 0,
             rccv: 0, rtcv: 0, rtsv: 0};
var sql_statement;
L.Icon.Default.imagePath = '/js/images';
var comma = d3.format('0,000');
var circles = [];
charts_url = '/api/v1/cuadrantes/crimes/HOMICIDIO DOLOSO,LESIONES POR ARMA DE FUEGO,ROBO DE VEHICULO AUTOMOTOR S.V.,ROBO DE VEHICULO AUTOMOTOR C.V.,ROBO A TRANSEUNTE C.V./pip_extra/';

var geoLocation = {
    getLocation: function() {
        var deferred = $.Deferred();
        // if geo location is supported
        if (navigator.geolocation) {
            // get current position and pass the results to
            // getPostalCode or time out after 5 seconds if it fails
            navigator.geolocation.getCurrentPosition(deferred.resolve,
                                                     deferred.reject, {
                timeout: 5000
            });
        } else {
            //geo location isn't supported
            deferred.reject(new Error('Your browser does not support Geo Location.'));
        }
        return deferred.promise();
    }
};

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
L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', { attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>' }).addTo(map);

addOutline = function(polygon, map) {
    var myStyle = {
        'color': 'red',
        'fillColor': '#fff',
        'weight': 2,
        'opacity': 1
    };
    singleGeojson = topojson
        .feature(polygon, polygon.objects.single)
        .features;
    L.geoJson(singleGeojson, {
        style: myStyle
    }).addTo(map);
};

function delay(ms) {
    var d = $.Deferred();
    setTimeout(function() { d.resolve(); }, ms);
    return d.promise();
}

function timeout(promise, ms) {
    var timeout = delay(ms); // your timeout
    var d = $.Deferred();
    timeout.then(function() { d.reject(new Error('Timed Out')); });
    promise.then(function(data) { d.resolve(data); });
    return d.promise();
}

// Download both the outline of CDMX and the geolocation at the same time
// but time out if the geolocation is taking too long because firefox
// just hangs if you dismiss the 'allow geolocation' dialog
$.when(timeout(geoLocation.getLocation(), 5500),
       $.getJSON('/js/df-outline.json'))
    .done(function(p, single) {
        //console.log(data.coords.longitude, data.coords.latitude);
        latLng = {
            lat: p.coords.latitude,
            lng: p.coords.longitude
        };
        addOutline(single[0], map);
        createMarker(latLng.lat, latLng.lng);
    })
    .fail(function(e) {
        latLng = {
            lat: 19.432605540309215,
            lng: -99.133208
        };
        // download the json df outline again since there was an error
        $.getJSON('/js/df-outline.json', function(polygon) {
            addOutline(polygon, map);
        });
        //map.setView([latLng.lat, latLng.lng], 15);
        createMarker(latLng.lat, latLng.lng);
    });


function get_data(data, dates) {

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
    isDF = leafletPip.pointInLayer(L.latLng(lat, lng), singleLayer, true);
    if (!isDF[0]) {
        lat = 19.432605540309215;
        lng = -99.133208;
    }
    if (typeof marker === 'undefined') {
        map.setView([lat, lng], 15);
        marker = new L.marker([lat, lng], {draggable: true});
        marker.on('dragend', function(event) {
            var marker = event.target;
            var position = marker.getLatLng();

            $.getJSON(charts_url +marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
                var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
                dates = _.map(dates, function(x) {return x + '-15';});
                dates.unshift('x');
                if (typeof pipCuad !== 'undefined')
                    map.removeLayer(pipCuad);
                while (circles.length > 0) {
                    map.removeLayer(circles.pop());
                }
                pipCuad = L.geoJson(JSON.parse(data.pip[0].geometry), {
                    "fillColor": "yellow",
                    "color": "black",
                    "weight": 4,
                    "opacity": .7,
                    "fillOpacity": 0.1
                });
                if (typeof pipCuad !== 'undefined')
                    pipCuad.addTo(map);
                pipData = data;
                get_data(pipData, dates);
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
                                          15, { fillOpacity: .7, color: circle_color, weight: 1 })
                        .bindPopup(data.latlong[i].crime + '<br>' + data.latlong[i].date + '<br>' + data.latlong[i].hour +
                                   (data.latlong[i].hour < "12" ? ' AM' : ' PM'))
                        .addTo(map);
                    circles.push(circle);
                }
            });


            //}
        });
        cuadsLayer = L.geoJson(cuadsGeojson);
        sectorsLayer = L.geoJson(sectorsGeojson);

        marker.addTo(map);
    }

    $.getJSON(charts_url + marker.getLatLng().lng +'/' + marker.getLatLng().lat, function(data) {
        var dates = _.uniq(_.pluck(data.cuadrante, 'date'));
        dates = _.map(dates, function(x) {return x + '-15';});
        dates.unshift("x");


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
            circles.push(circle);
        }
    });

    // There's a weird bug where the map has a red border
    $('.leaflet-clickable').first().attr({'stroke': '#7f0000'});
};

$(window).load(function() {
    $('#linechartstext').height($('#barchartstext').height());
});

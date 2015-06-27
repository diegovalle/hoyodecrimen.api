//The map
var mxc, crimes, select_html = '';
L.Icon.Default.imagePath = '/js/images';
//return a color scale for the choropleths
var createScale = function(colors, domain, numcol){
    return chroma.scale(colors).domain(domain, numcol);
};
var createScale = function(colors, domain, numcol){
    return d3.scale.quantize()
        .domain(domain)
        .range(d3.range(numcol).map(function(i) { return colors[i] }));
}
//for formatting the population data
comma = d3.format("0,000");

var scaleHomicide,
scaleRNCV,
scaleRVCV,
scaleRVSV,
scaleVIOL;

var mapData;

//remember this is a mustache template
var varName = "hom_rate";
var title = title_text;
var config;

//use the appropiate scale from the template
var getColor;

var nokiaStreets = L.tileLayer('https://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/normal.night/{z}/{x}/{y}/256/png8?app_id={app_id}&app_code={app_code}', {
    attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
    subdomains: '1234',
    mapID: 'newest',
    app_id: '2xIqG1pjt7OdQnzqAHmm',
    app_code: 't0G_EMNWEWEpFEIoJYEncg',
    base: 'base',
    minZoom: 0,
    maxZoom: 20
});
var nokiaSat = L.tileLayer('https://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/satellite.day/{z}/{x}/{y}/256/png8?app_id={app_id}&app_code={app_code}', {
    attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
    subdomains: '1234',
    mapID: 'newest',
    app_id: '2xIqG1pjt7OdQnzqAHmm',
    app_code: 't0G_EMNWEWEpFEIoJYEncg',
    base: 'aerial',
    minZoom: 0,
    maxZoom: 20
});

// var nokiaStreets = L.tileLayer('http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/normal.night/{z}/{x}/{y}/256/png8', {
//     attribution: '©2012 Nokia <a href="http://here.net/services/terms" target="_blank">Terms of use</a>'
// }),
// nokiaSat = L.tileLayer('http://{s}.maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/satellite.day/{z}/{x}/{y}/256/png8', {
//     attribution: '©2012 Nokia <a href="http://here.net/services/terms" target="_blank">Terms of use</a>'
// })
var map = L.map('map', {center: new L.LatLng(19.38, -99.1),
                        zoom: 11,
                        layers: [nokiaStreets]});

var baseMaps = {
    "Satellite": nokiaSat,
    "Streets": nokiaStreets
};





//add a geosearch control
// new L.Control.GeoSearch({
//  provider: new L.GeoSearch.Provider.Google()
// }).addTo(map);

// control that shows state info on hover
var info = L.control();
var legend = L.control({position: 'bottomright'});

info.onAdd=function(map){
    this._div=L.DomUtil.create('div','info', L.DomUtil.get('control'));
    this.update();

    //return this._div;
    return L.DomUtil.create('adsf')
};

legend.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info legend', L.DomUtil.get('control'));
    this.update();
    //document.getElementById("seltarget").onmouseover = controlEnter;
    //document.getElementById("seltarget").onmouseout = controlLeave;
    return this._div;
};

function controlEnter(e) {
    map.dragging.disable();
}
function controlLeave() {
    map.dragging.enable();
}
_.sortedFind = function sortedFind(list, item, key) {
    return (item, list[_.sortedIndex(list, item, key)]);
};

setChange = function(){

    $("#seltarget").change(function() {
      d3.json(mapType === 'sectores' ? '/api/v1/sectores/all/crimes/'+ this.value +'/period' : '/api/v1/cuadrantes/all/crimes/'+ this.value +'/period', function(data){
        mapData = data;
        $(config.selector).attr('style', '');
        changeConfig($("#seltarget").attr('value'))
        mxc.eachLayer(function(layer) {
            if(mapType === 'sectores') {
                obj = _.sortedFind(mapData.rows,
                                  {'sector': layer.feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                                   'crime':config.currentName.toUpperCase()},
                                  'sector');
            } else {
                obj = _.sortedFind(mapData.rows,
                                  {'cuadrante': layer.feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                                   'crime':config.currentName.toUpperCase()},
                                  'cuadrante');
            }
            layer.setStyle({
                fillColor:  mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
                //properties[config.currentName]),
                fillOpacity: 0.8,
                weight: 0.5
            });
        });
        for(i = 0; i < 9; i++) {
            $("#legendnum" + i).html(
                '<i style="background:' + config.color[i] + '"></i>' +
                    config.round1(config.colorFun.
                                  invertExtent(config.color[i])[0], 1) +" - " +
                    config.round2(config.colorFun.
                                  invertExtent(config.color[i])[1], 1)
            );
        }
        $(config.selector).css('background-color', config.color[2]);
        updateLineChart();
        clickedFeature = null;
        info.update();
    });
  });
}


changeConfig = function(seltarget) {
    switch(seltarget) {
        case "Homicide":
            config.colorFun =  scaleHomicide;
            config.color = colorbrewer.Reds["9"];
            config.currentName ='HOMICIDIO DOLOSO';
            config.lastSelect = "Homicide";
            config.selector = mapType === 'sectores'  ? ".crime_rate" : ".crime_count";
            break;

        default:
            if (typeof(seltarget) === 'undefined' | seltarget === "")  seltarget = "HOMICIDIO DOLOSO";
            config.colorFun =   createScale(colorbrewer.Reds["9"],
                                        findRange(seltarget), 9);
            config.color = colorbrewer.Reds["9"];
            config.currentName = seltarget;
            config.lastSelect = seltarget;
            config.selector = mapType === 'sectores'  ? ".crime_rate" : ".crime_count";;
            //homTotal = calcTotal(seltarget);
            //homTotalRate = Math.round(homTotal / 8785874 * 100000 * 10)/10;
            break;

        }
}

info.update = function (feature) {

    if(feature) {
        props = {};
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(), 'crime': config.currentName.toUpperCase()});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(), 'crime': config.currentName.toUpperCase()});
        }
        props.hom_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.hom_count = obj['count'];
        props.population = obj['population']
        props.sector = obj['sector']
        if (mapType != "sectores") {
            props.cuadrante = obj['cuadrante']
        }
    } else {
        props = null;
    }
    var start_date = new Date(mapData.rows[0].start_date + '-15');
    var end_date = new Date(mapData.rows[0].end_date + '-15');
    var date_text = '(' + monthNames[start_date.getMonth()] + ' ' + start_date.getFullYear() +
        ' - ' + monthNames[end_date.getMonth()] + ' ' + end_date.getFullYear() + ')'
    var div;
    config.color = colorbrewer.Reds["9"];
    div = '<div id="variables" class="menu-ui"><select id="seltarget" autofocus>'+select_html+'</select></div><h1>'+
        title + '</h1><h3>' +
        (props ? props.sector + (mapType === "sectores" ? "" : " / " + props.cuadrante) : 'DF') +'</h3>' + '<h4>' +date_text + '</h4><div><h4>'+total_population_text+': ' +  (props ? '' + comma(props.population) : '8,785,874') +
        '</h4></div>' +
        '<table class="tg">' +
        '<tr>' +
        '<th class="tg-031e"></th>' +
        '<th class="tg-031e">'+rate_text+'</th>' +
        '<th class="tg-031e">'+count_text+'</th>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name  tg-031e">'+ config.currentName.toUpperCase() +'</td>' +
        '<td class="crime_rate tg-031e' + ('sectores' === "sectores" ? " homicides " : "")  + '">' + (props ? null + props.hom_rate : homTotalRate) +'</td>' +
        '<td class="crime_count tg-031e' + ('sectores' === "sectores" ? "" : " homicides ")  + '">' + (props ? comma(props.hom_count) : comma(homTotal)) +'</td>' +
        '</tr>' +
        '</table><br/><div class="row"><div class="col-md-5">'+map_legend_text+'<div class="legend">';

    changeConfig($("#seltarget").attr('value'))
    for(i = 0; i < 9; i=i+3) {
        div  +=
            '<span id="legendnum' +
            i +'">' + '<i style="background:' + config.color[i] + '"></i>' +
            config.round1(config.colorFun.
                          invertExtent(config.color[i])[0], 1) +" - " +
            config.round2(config.colorFun.
                          invertExtent(config.color[i])[1], 1) +'</span><br>';
    }
    // don't leak
    $("#seltarget").remove();
    this._div.innerHTML = div + '</div></div></div>';
    $(config.selector).css('background-color',config.color[2]);

    $("#seltarget").val(config.lastSelect);
    setChange();

    if(document.getElementById("seltarget")) {
        document.getElementById("seltarget").onmouseover = controlEnter;
        document.getElementById("seltarget").onmouseout = controlLeave;
    }

};




var getStyle = function(feature) {
  if(mapType === 'sectores') {
      obj = _.sortedFind(mapData.rows,
                        {'sector': feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                         'crime':config.currentName.toUpperCase()},
                        'sector');
  } else {
      obj = _.sortedFind(mapData.rows,
                        {'cuadrante': feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                         'crime':config.currentName.toUpperCase()},
                        'cuadrante');
  }


    return {
        fillColor: mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
        weight: .5,
        opacity: 1,
        color: '#555',
        fillOpacity: 0.8
    };

};
var clickedFeature;
function highlightFeature(e) {
    if(clickedFeature){
        resetHighlight(clickedFeature)
        //clickedFeature.target.setStyle({
	      //  fillColor: mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
        //        fillOpacity: 0.8,
        //        weight: 0.5,
        //        color: '#555'
        //    });
    }
    clickedFeature = e;
    var layer = e.target;
    layer.setStyle({
        //fillColor: 'transparent',
        weight: 5,
        fillOpacity: 0.6,
        color: '#333'

    });

    if (!L.Browser.ie && !L.Browser.opera) {
       layer.bringToFront();
    }

    info.update(layer.feature.properties);
    d3.json(mapType === "sectores" ? '/api/v1/sectores/'+obj.sector+'/crimes/'+config.currentName+'/series' : '/api/v1/cuadrantes/'+obj.cuadrante+'/crimes/'+config.currentName+'/series', function(data){
      var line_options = {
        //title: "Homicides",
        description: '',
        height: 150,
        y_label: '',
        area: false,
        buffer: 30,
        top: 30,
        left: 50,
        full_width: true,
        //width: 200,
        interpolate: "linear",
        target: '#line-chart',
        x_accessor: 'date',
        y_accessor: 'rate',
        xax_count: 3
      };
        _.forEach(data.rows, function(x) {x['rate'] = x.count / x.population * 100000 * 12});
      if(mapType === "cuadrantes") line_options.y_accessor = 'count';
      data = MG.convert.date(data.rows, 'date', '%Y-%m');
      line_options.data = data;
      MG.data_graphic(line_options);
    });
}

updateLineChart = function(){
  d3.json('/api/v1/df/crimes/'+config.currentName+'/series', function(data){
    var line_options = {
      //title: "Homicides",
      description: '',
      height: 150,
      y_label: '',
      area: false,
      buffer: 30,
      top: 30,
      left: 50,
      full_width: true,
      //width: 200,
      interpolate: "linear",
      target: '#line-chart',
      x_accessor: 'date',
      y_accessor: 'rate',
      xax_count: 3
    };
      _.forEach(data.rows, function(x) {x['rate'] = x.count / x.population * 100000 * 12});
    data = MG.convert.date(data.rows, 'date', '%Y-%m');
    if(mapType === "cuadrantes") line_options.y_accessor = 'count';
    line_options.data = data;
    MG.data_graphic(line_options);
  });
}

function resetHighlight(e) {
    //mxc.resetStyle(e.target);
    if(mapType === 'sectores') {
        obj = _.findWhere(mapData.rows,
                          {'sector': e.target.feature.
                           properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                           'crime':config.currentName.toUpperCase()})
    } else {
        obj = _.findWhere(mapData.rows,
                          {'cuadrante': e.target.feature.
                           properties[mapType === "sectores" ? "sector" : "cuadrante"].toUpperCase(),
                           'crime':config.currentName.toUpperCase()})
    }
    e.target.setStyle({
	      fillColor: mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
        fillOpacity: 0.8,
        weight: 0.5,
        color: '#555'
    });
    info.update();
}

function onEachFeature(feature, layer) {
    layer.on({
        //mouseover: highlightFeature,
        click: highlightFeature,
        //mouseout: resetHighlight
    });

}

findRange = function(name) {
    name = name.toUpperCase();
    var ext = d3.extent(mapData.rows, function(d) {
        if(d.crime === name)
            if(mapType === "sectores")
                if(d.population)
                    return d.count / d.population * 100000;
                else
                    return 0;
            else if (mapType === "cuadrantes")
                if(d.population)
                    return d.count
                else
                    return 0;
    })


    return(ext);
};

calcTotal = function(crimeName, series) {
    ar=_.where(series.rows, {'crime': crimeName.toUpperCase()})
    return  _.reduce(ar, function(memo, value){
        if(value.date >= mapData.rows[0].start_date)
            return memo + value.count;
        else
            return 0;
    }, 0); }


$.getJSON(mapFile, function (data) {

    var mxcGeojson = topojson.feature(data, data.objects[mapType]).features;

    var featureCollection = {
        "type": "FeatureCollection",
        "features": []
    };

    for (var i = 0; i <  mxcGeojson.length; i++) {
        featureCollection.features.push({
            "type":"Feature",
            "geometry":  mxcGeojson[i].geometry,
            "properties":  mxcGeojson[i].properties
        });
    }

    //findRange=function(mxcGeojson, name) {
    //    return(d3.extent(d3.entries(mxcGeojson), function(d){return(+d.value.properties[name])} ));
    //}
    var api_url;
    mapType === 'sectores' ? api_url = '/api/v1/sectores/all/crimes/HOMICIDIO%20DOLOSO/period' : api_url = '/api/v1/cuadrantes/all/crimes/HOMICIDIO%20DOLOSO/period';
    d3.json(api_url, function (list) {
        mapData = list
        d3.json('/api/v1/df/crimes/HOMICIDIO%20DOLOSO/series', function(series){

            homTotal = calcTotal('homicidio doloso', series);
            homTotalRate = Math.round(homTotal / 8785874 * 100000 * 10)/10;

            //homTotal = 823,rncvTotal = 3867,rvcvTotal = 6208,rvsvTotal = 10583,violTotal = 461,homTotalRate = 9.4,rncvTotalRate = 44,rvcvTotalRate = 70.7,rvsvTotalRate = 120.5,violTotalRate = 5.2



        //The scales for the various maps
        scaleHomicide = createScale(colorbrewer.Reds["9"],
                                    findRange('homicidio doloso'), 9),
        scaleRNCV = createScale(colorbrewer.Blues["9"],
                                findRange('robo a negocio c.v.'), 9),
        scaleRVCV = createScale(colorbrewer.Purples["9"],
                                findRange('robo de vehiculo automotor c.v.'), 9),
        scaleRVSV = createScale(colorbrewer.Greens["9"],
                                findRange('robo de vehiculo automotor s.v.'), 9);
        scaleVIOL = createScale(colorbrewer.Greys["9"],
                            findRange('violacion'), 9);
        getColor = function(value) {
            return scaleFun(value);
        };
        scaleFun = scaleHomicide;
        //colorFun = scaleFun;
        config = {
            colorFun:  scaleFun,
            color: colorbrewer.Reds["9"],
            currentName: "homicidio doloso",
            lastSelect: "Homicide",
            selector: ".homicides",
            round1: null,
            round2: null
        }
        if(mapType != "sectores") {
            config.round1 = Math.ceil;
            config.round2 = Math.floor;
        }
        else {
            config.round1 = d3.round;
            config.round2 = d3.round;
        }

        // mxcLayer.addData(featureCollection);

        mxc = L.geoJson(featureCollection, {
            style: getStyle,
            onEachFeature: onEachFeature
        }).addTo(map);
        updateLineChart();
        //legend.addTo(map);
        info.addTo(map);
        info.update();

        $.ajax({
            dataType: 'jsonp',
            url: '/api/v1/crimes',
            success: function(data) {
                crimes = _.pluck(data.rows, "crime");
                $.each(crimes, function(key, value) {
                    $('#seltarget')
                 .append($('<option>', { value : value })
                 .text(value));
                });
                select_html = $('#seltarget').html();
            }});

        document.getElementById("seltarget").onmouseover = controlEnter;
        document.getElementById("seltarget").onmouseout = controlLeave;
        L.control.layers(null,baseMaps, {position: 'topleft'}).addTo(map);
            L.control.locate({
                              drawCircle: false,
                          locateOptions: {enableHighAccuracy: true }}).addTo(map);
        var hash = new L.Hash(map);
        //deselect any selected polygons when the user clicks on the map
        map.on('click', function(e) {
            if(clickedFeature){
                clickedFeature.target.setStyle({
	            fillColor: mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
                    fillOpacity: 0.8,
                    weight: 0.5,
                    color: '#555'
                });
            }
            updateLineChart();
            clickedFeature = null;
            info.update();
        });
    });
});
});

//The map
var mxc;

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
var title = "Rates by Sector";
var config;

//use the appropiate scale from the template
var getColor;

var nokiaStreets = L.tileLayer('http://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/normal.night/{z}/{x}/{y}/256/png8?app_id={app_id}&app_code={app_code}', {
    attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
    subdomains: '1234',
    mapID: 'newest',
    app_id: '6nA3IVXYrizzTDgFJMIN',
    app_code: '6o4Vvdk1QIkytF-bmyH_Yg',
    base: 'base',
    minZoom: 0,
    maxZoom: 20
});
var nokiaSat = L.tileLayer('http://{s}.{base}.maps.cit.api.here.com/maptile/2.1/maptile/{mapID}/satellite.day/{z}/{x}/{y}/256/png8?app_id={app_id}&app_code={app_code}', {
    attribution: 'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
    subdomains: '1234',
    mapID: 'newest',
    app_id: '6nA3IVXYrizzTDgFJMIN',
    app_code: '6o4Vvdk1QIkytF-bmyH_Yg',
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


info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    //document.getElementById("seltarget").onmouseover = controlEnter;
    //document.getElementById("seltarget").onmouseout = controlLeave;  
    return this._div;
    };

legend.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info legend');
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
setChange = function(){
    
    $("#seltarget").change(function() {
        $(config.selector).attr('style', '');
        changeConfig($("#seltarget").attr('value'))
        mxc.eachLayer(function(layer) {
            if(mapType === 'sectores') {
                obj = _.findWhere(mapData.rows, 
                                  {'sector': layer.feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                                   'crime':config.currentName})
            } else {
                obj = _.findWhere(mapData.rows, 
                                  {'cuadrante': layer.feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                                   'crime':config.currentName})
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
    });
}   


changeConfig = function(seltarget) {
    switch(seltarget) {
        case "Homicide":
            config.colorFun =  scaleHomicide;
            config.color = colorbrewer.Reds["9"];
            config.currentName ='homicidio doloso';
            config.lastSelect = "Homicide";
            config.selector = ".homicides";
            break;
        case "Violent robberies to a business":
            config.colorFun =  scaleRNCV;
            config.color = colorbrewer.Blues["9"];
            config.currentName = 'robo a negocio c.v.';
            config.lastSelect = "Violent robberies to a business";
            config.selector = ".rncv";
            break;
        case "Violent car robberies":
            config.colorFun =  scaleRVCV;
            config.color = colorbrewer.Purples["9"];
            config.currentName = 'robo de vehiculo automotor c.v.';
            config.lastSelect = 'Violent car robberies';
            config.selector = ".rvcv";
            break;
        case "Non-violent car robberies":
            config.colorFun =  scaleRVSV;
            config.color = colorbrewer.Greens["9"];
            config.currentName = 'robo de vehiculo automotor s.v.';
            config.lastSelect = "Non-violent car robberies";
            config.selector = ".rvsv";
            break;
        case "Rape":
            config.colorFun =  scaleVIOL;
            config.color = colorbrewer.Greys["9"];
            config.currentName = 'violacion';
            config.lastSelect = "Rape";
            config.selector = ".viol";
            break;
        }
}

info.update = function (feature) {
    
    if(feature) {
        props = {};
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'homicidio doloso'});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'homicidio doloso'});
        }
        props.hom_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.hom_count = obj['count'];
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo a negocio c.v.'});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo a negocio c.v.'});
        }
        props.rncv_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.rncv_count = obj['count'];
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo de vehiculo automotor c.v.'});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo de vehiculo automotor c.v.'});
        }
        props.rvcv_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.rvcv_count = obj['count'];
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo de vehiculo automotor s.v.'});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'robo de vehiculo automotor s.v.'});
        }
        props.rvsv_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.rvsv_count = obj['count'];
        if(mapType === 'sectores') {
            obj = _.find(mapData.rows, {'sector': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'violacion'});
        } else {
            obj = _.find(mapData.rows, {'cuadrante': feature[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 'crime': 'violacion'});
        }
        props.viol_rate = Math.round(obj['count'] / obj['population'] * 100000 * 10) / 10;
        props.viol_count = obj['count'];
        props.population = obj['population']
        props.sector = obj['sector']
        if (mapType != "sectores") {
            props.cuadrante = obj['cuadrante']
        }
    } else {
        props = null;
    }
    
    var div;
    config.color = colorbrewer.Reds["9"];
    div = '<div id="variables" class="menu-ui"><select id="seltarget" autofocus><option value="Homicide">Homicide</option><option value="Violent robberies to a business">Violent robberies to a business</option><option value="Violent car robberies">Violent car robberies</option><option value="Non-violent car robberies">Non-violent car robberies</option><option value="Rape">Rape</option></select></div><h1>'+
        title + '</h1><h3>' +
        (props ? props.sector + (mapType === "sectores" ? "" : " / " + props.cuadrante) : 'DF (Aug 13 - Jul 14)') +'</h3>' + '<div><h4>Total Population: ' +  (props ? '' + comma(props.population) : '8,785,874') +
        '</h4></div>' +
        '<table class="tg">' +
        '<tr>' +
        '<th class="tg-031e"></th>' +
        '<th class="tg-031e">Rate</th>' +
        '<th class="tg-031e">Count</th>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name homicides tg-031e">Homicides</td>' +
        '<td class="crime_rate tg-031e' + ('sectores' === "sectores" ? " homicides " : "")  + '">' + (props ? null + props.hom_rate : homTotalRate) +'</td>' +
        '<td class="crime_count tg-031e' + ('sectores' === "sectores" ? "" : " homicides ")  + '">' + (props ? comma(props.hom_count) : comma(homTotal)) +'</td>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name rncv tg-4eph">Violent robberies to a business</td>' +
        '<td class="tg-4eph' + ('sectores' === "sectores" ? " rncv " : "")  + '">' + (props ? '' + props.rncv_rate : rncvTotalRate) +'</td>' +
        '<td class="tg-4eph' + ('sectores' === "sectores" ? "" : " rncv ")  + '">' + (props ? comma(props.rncv_count) : comma(rncvTotal)) +'</td>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name rvcv tg-031e">Violent car robberies</td>' +
        '<td class="tg-031e' + ('sectores' === "sectores" ? " rvcv " : "")  + '">' + (props ? '' + props.rvcv_rate  : rvcvTotalRate) +'</td>' +
        '<td class="tg-031e' + ('sectores' === "sectores" ? "" : " rvcv ")  + '">' + (props ? comma(props.rvcv_count) : comma(rvcvTotal)) +'</td>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name rvsv tg-4eph">Non-violent car robberies</td>' +
        '<td class="tg-4eph' + ('sectores' === "sectores" ? " rvsv " : "")  + '">' + (props ? props.rvsv_rate  : rvsvTotalRate) +'</td>' +
        '<td class="tg-4eph' + ('sectores' === "sectores" ? "" : " rvsv ")  + '">' + (props ? comma(props.rvsv_count) : comma(rvsvTotal)) +'</td>' +
        '</tr>' +
        '<tr>' +
        '<td class="crime_name viol tg-4eph">Rape</td>' +
        '<td class="tg-031e' + ('sectores' === "sectores" ? " viol " : "")  + '">' + (props ? props.viol_rate  : violTotalRate) +'</td>' +
        '<td class="tg-031e' + ('sectores' === "sectores" ? "" : " viol ")  + '">' + (props ? comma(props.viol_count) : comma(violTotal)) +'</td>' +
        '</tr>' +
        '</table><br/><div class="legend">';
    
    changeConfig($("#seltarget").attr('value')) 
    for(i = 0; i < 9; i++) {
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
    this._div.innerHTML = div + '</div>';
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
        obj = _.findWhere(mapData.rows, 
                          {'sector': feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                           'crime':config.currentName})
    } else {
        obj = _.findWhere(mapData.rows, 
                          {'cuadrante': feature.properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                           'crime':config.currentName})
    }
    
    return {
        fillColor: mapType === "sectores" ? config.colorFun(obj['count'] / obj['population'] * 100000 ) : config.colorFun(obj['count']),
        weight: .5,
        opacity: 1,
        color: '#555',
        fillOpacity: 0.8
    };
    
};

function highlightFeature(e) {
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
}

function resetHighlight(e) {
    //mxc.resetStyle(e.target);
    if(mapType === 'sectores') {
        obj = _.findWhere(mapData.rows, 
                          {'sector': e.target.feature.
                           properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                           'crime':config.currentName})
    } else {
        obj = _.findWhere(mapData.rows, 
                          {'cuadrante': e.target.feature.
                           properties[mapType === "sectores" ? "sector" : "cuadrante"].toLowerCase(), 
                           'crime':config.currentName})
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
        mouseover: highlightFeature,
        click: highlightFeature,
        mouseout: resetHighlight
    });
    
}




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
    mapType === 'sectores' ? api_url = '/api/v1/list/sectores/all' : api_url = '/api/v1/list/cuadrantes/all';
    $.getJSON(api_url, function (list) {
        mapData = list
        findRange=function(name) {
            var ext = d3.extent(mapData.rows, function(d) {
                if(d.crime === name)
                    if(mapType === "sectores")
                        return d.count / d.population * 100000;
                    else
                        return d.count;
            })
            
            
            return(ext);};
        
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
        
        //legend.addTo(map);
        info.addTo(map);
        info.update();
        document.getElementById("seltarget").onmouseover = controlEnter;
        document.getElementById("seltarget").onmouseout = controlLeave; 
        L.control.layers(null,baseMaps, {position: 'topleft'}).addTo(map);
        L.control.locate({drawCircle: false, 
                          locateOptions: {enableHighAccuracy: true }}).addTo(map);
        var hash = new L.Hash(map);
    });
});



homTotal = 823,rncvTotal = 3867,rvcvTotal = 6208,rvsvTotal = 10583,violTotal = 461,homTotalRate = 9.4,rncvTotalRate = 44,rvcvTotalRate = 70.7,rvsvTotalRate = 120.5,violTotalRate = 5.2;

var margin={top:10,left:0,bottom:10,right:0},width=parseInt(d3.select('#map-homicide').style('width')),width=width-margin.left-margin.right,mapRatio=1.5,height=width*mapRatio;var data,crimeData;var width=parseInt(d3.select('#map-homicide').style('width')),height=400;comma=d3.format('0,000');function daysInMonth(month,year){return new Date(year,month,0).getDate();}
createQuantized=function(domain,name){return(d3.scale.quantize().domain(domain).range(d3.range(9).map(function(i){return name+i+'-9';})));};var max=d3.max(d3.entries(data),function(d){return d3.max(d3.entries(d.value),function(e){return d3.max(e.value);});});var projection=d3.geo.projection(function(x,y){return[x,y];}).precision(0).scale(1).translate([0,0]);var path=d3.geo.path().projection(matrix(.41,0,0,.41,-45,25));function matrix(a,b,c,d,tx,ty){return d3.geo.transform({point:function(x,y){this.stream.point(a*x+b*y+tx,c*x+d*y+ty);}});}
var svgHomicide=d3.select("#map-homicide").append('div').attr('style','margin-left:0px;border: 1px dashed #d0c0a8;').append("svg").attr("width",width).attr("height",height);var svgRNCV=d3.select("#map-rncv").append("svg").attr("width",width).attr("height",height);var svgRVCV=d3.select("#map-rvcv").append("svg").attr("width",width).attr("height",height);var svgRVSV=d3.select("#map-rvsv").append("svg").attr("width",width).attr("height",height);var svgVIOL=d3.select("#map-viol").append("svg").attr("width",width).attr("height",height);_.sortedFind=function sortedFind(list,item,key){return(item,list[_.sortedIndex(list,item,key)]);};tip=function(crimeCode){return(d3.tip().attr('class','d3-tip').offset([-10,0]).html(function(d){if(topoName==="sectores"){obj=_.findWhere(cuadrantesMap.rows,{'sector':d.properties['sector'].toUpperCase(),'crime':value.toUpperCase()});rate=Math.round(obj['count']/obj['population']*100000*10)/10;return"<span>"+d.properties.sector+(topoName==="sectores"?"":" - "+d.properties.cuadrante)+
" ⇨ "+rate+"</span>";}
else{obj=_.findWhere(cuadrantesMap.rows,{'cuadrante':d.properties['cuadrante'].toUpperCase(),'crime':value.toUpperCase()});rate=obj[topoName==='cuadrantes'?'count':'difference'];return"<span>"+d.properties.sector+(topoName==="sectores"?"":" - "+d.properties.cuadrante)+
" ⇨ "+rate+"</span>";}}));};tipHom=tip(value);svgHomicide.call(tipHom);createMap=function(df,svg,crime,crimeCode,colorFun,titleId,topoNam,tipFun,seriesName){type=topoName==="sectores"?"sectores":"cuadrantes";var features=svg.append("g").attr("class","features");features.attr("class","subdivisions").selectAll("path").data(topojson.feature(df,df.objects[type]).features).enter().append("path").attr("class",function(d){if(topoName==="sectores"){obj=_.sortedFind(cuadrantesMap.rows,{'sector':d.properties['sector'].toUpperCase(),'crime':crimeCode.toUpperCase()},'sector');return colorFun(obj['count']/obj['population']*100000)}
else{obj=_.sortedFind(cuadrantesMap.rows,{'cuadrante':d.properties['cuadrante'].toUpperCase(),'crime':crimeCode.toUpperCase()},'cuadrante');if(typeof(obj)!=="undefined")
return colorFun(obj[topoName==='cuadrantes'?'count':'difference'])
else{console.log(d.properties['cuadrante'].toUpperCase())}}}).attr("d",path)
.on("mouseover",tipHom.show).on("mouseout",tipHom.hide).on("mousedown",function(d){if(topoName==="sectores")
var url="/api/v1/sectores/"+encodeURIComponent(d.properties['sector'].toUpperCase())+'/crimes';else
var url="/api/v1/cuadrantes/"+encodeURIComponent(d.properties['cuadrante'].toUpperCase())+'/crimes';d3.json(url+'/'+value+'/series',function(data){series=_.map(data.rows,function(x){return summer(x)})
series.unshift(value);_.forEach(data.rows,function(d,i){d['rate']=(d.count/daysInMonth(d.date.substr(5,6),d.date.substr(0,4))*30)/d.population*100000*12})
line_options.data=MG.convert.date(data.rows,'date','%Y-%m');line_options.target='#chart-homicide';MG.data_graphic(line_options);d3.select(titleId).text(value+" / "+d.properties.sector+(topoName==="sectores"?"":" / "+d.properties.cuadrante));})
});var zoom=d3.behavior.zoom().scaleExtent([1,Infinity]).on("zoom",zoomed);svg.call(zoom);function zoomed(){features.attr("transform","translate("+zoom.translate()+")scale("+zoom.scale()+")").selectAll("path").style("stroke-width",0.5/zoom.scale()+"px");}}
d3.select(self.frameElement).style("height",height+"px");function createLineChart(selection,totalCrime,labelText,color,dates){name=totalCrime[0];var chart1=c3.generate({padding:{right:27,},bindto:selection,point:{show:false},regions:[{start:cuadrantesMap.rows[0].start_period1+'-15',end:cuadrantesMap.rows[0].end_period1+'-15'},{start:cuadrantesMap.rows[0].start_period2+'-15',end:cuadrantesMap.rows[0].end_period2+'-15',class:'foo'}],data:{x:'x',columns:[dates,totalCrime],color:function(d){return color}},axis:{x:{type:'timeseries',tick:{count:4,format:'%Y-%B'}},y:{tick:{format:function(d){return d%1==0?d:""}},min:0,label:{text:labelText,position:'outer-middle'},padding:{top:0,bottom:0}}},tooltip:{format:{title:function(d){var format=d3.time.format("%Y-%B");return format(d);},value:function(value,ratio,id){var format=d3.format('');return format(value);}
}}});return chart1;}
createLegend=function(selection,colorFun){d3.select(selection).selectAll("*").remove();var legend=d3.select(selection).append('ul').attr('class','list-inline');var keys=legend.selectAll('li.key').data(colorFun.range());keys.enter().append('li').attr('class',function(d){return('key '+String(d))}).text(function(d){var r=colorFun.invertExtent(d);return d3.round(r[0],0);});}
var line_options={description:'',height:350,y_label:labelText,area:false,buffer:0,left:85,right:25,top:25,full_width:true,interpolate:"linear",x_accessor:'date',xax_count:4,yax_count:3,xax_format:d3.time.format('%b')};line_options.mouseover=function(d,i){var target=line_options.target;d3.select(target+' text.mg-active-datapoint').text(date_txt+d3.time.format('%b-%Y')(d.date)+count_txt+d.count+rate_txt+d3.round(d.rate,1));};if(topoName==="sectores"){line_options.y_accessor='rate'}
else{line_options.y_accessor='count'}
d3.json(mapFile,function(error,df){if(topoName=="sectores")
var url="/api/v1/sectores/all/crimes/HOMICIDIO%20DOLOSO/period";else if(topoName=="cuadrantes")
var url="/api/v1/cuadrantes/all/crimes/HOMICIDIO%20DOLOSO/period";else
var url="/api/v1/cuadrantes/all/crimes/HOMICIDIO%20DOLOSO/period/change";d3.json('/api/v1/df/crimes/all/series',function(data){all_df=data.rows;d3.json(url,function(cuadrantes){cuadrantesMap=cuadrantes;if(topoName=="sectores")
summer=annualizedRate
else
summer=crimeCounts;var dates=_.uniq(_.pluck(data.rows,'date'));dates=_.map(dates,function(x){return x+'-15'});dates.unshift("x")
byCrime=_.groupBy(data.rows,'crime')
HomicidesA=_.flatten([value,_.pluck(_.groupBy(all_df,'crime')[value],'count')])
HomicidesA=_.flatten([value,_.map(_.groupBy(all_df,'crime')[value],function(x){return summer(x)})])
_.forEach(byCrime['HOMICIDIO DOLOSO'],function(d,i){d['rate']=(d.count/daysInMonth(d.date.substr(5,6),d.date.substr(0,4))*30)/d.population*100000*12})
line_options.data=MG.convert.date(byCrime['HOMICIDIO DOLOSO'],'date','%Y-%m');line_options.target='#chart-homicide';if(topoName==="cuadrantes-change"){var markers=[{'date':new Date(new Date(cuadrantesMap.rows[0]['end_period1']+'-01T00:00:00.000Z')),'label':''},{'date':new Date(new Date(cuadrantesMap.rows[0]['end_period2']+'-01T00:00:00.000Z')),'label':''},{'date':new Date(new Date(cuadrantesMap.rows[0]['start_period1']+'-01T00:00:00.000Z')),'label':''},{'date':new Date(new Date(cuadrantesMap.rows[0]['start_period2']+'-01T00:00:00.000Z')),'label':''}];line_options.markers=markers;}
MG.data_graphic(line_options);findRange=function(name){name=name.toUpperCase();var ext=d3.extent(cuadrantesMap.rows,function(d){if(d.crime===name){if(topoName==="sectores")
if(d.population)
return d.count/d.population*100000;else
return 0;else if(topoName==="cuadrantes"){if((d.crime=='HOMICIDIO DOLOSO'|d.crime=='LESIONES POR ARMA DE FUEGO')&(d.cuadrante=='N-4.4.4'|d.cuadrante=='C-2.1.16'|d.cuadrante=='N-2.2.1'|d.cuadrante=='O-2.5.7'|d.cuadrante=='O-2.2.4'|d.cuadrante=='N-1.3.10'|d.cuadrante=='P-1.5.7'|d.cudrante=='P-3.1.1'))
return 0;if(d.population)
return d.count
else
return 0;}
else{if((d.crime=='HOMICIDIO DOLOSO'|d.crime=='LESIONES POR ARMA DE FUEGO')&(d.cuadrante=='N-4.4.4'|d.cuadrante=='C-2.1.16'|d.cuadrante=='N-2.2.1'|d.cuadrante=='O-2.5.7'|d.cuadrante=='O-2.2.4'|d.cuadrante=='N-1.3.10'|d.cuadrante=='P-1.5.7'|d.cudrante=='P-3.1.1'))
return 0;if(d.population)
return d.difference;else
return 0;}}});if(ext[0]<0)
if(Math.abs(ext[0])>ext[1]){return([ext[0],0,Math.abs(ext[0])])}else
return([-ext[1],0,ext[1]]);else
return(ext);}
if(topoName==="cuadrantes-change"){var monthNames=shortMonths;var start_period1=new Date(cuadrantesMap.rows[0].start_period1+'-15');var start_period2=new Date(cuadrantesMap.rows[0].start_period2+'-15');var end_period1=new Date(cuadrantesMap.rows[0].end_period1+'-15');var end_period2=new Date(cuadrantesMap.rows[0].end_period2+'-15');var dates=monthNames[start_period1.getMonth()]+' '+start_period1.getFullYear()+' - '+monthNames[end_period1.getMonth()]+' '+end_period1.getFullYear()+toText+monthNames[start_period2.getMonth()]+' '+start_period2.getFullYear()+' - '+monthNames[end_period2.getMonth()]+' '+end_period2.getFullYear()
d3.select('#hom-date').text(changesText+dates);}else{var monthNames=longMonths;var startDate=new Date(cuadrantesMap.rows[0].start_date+'-15');var endDate=new Date(cuadrantesMap.rows[0].end_date+'-15');var dates=monthNames[startDate.getMonth()]+' '+startDate.getFullYear()+toText+monthNames[endDate.getMonth()]+' '+endDate.getFullYear();d3.select('#hom-date').text((topoName=="sectores"?sectorMapTitle:cuadMapTitle)+dates);}
quantizeRed=createQuantized(findRange('homicidio doloso'),mapColors.hom)
console.time("findmap");createMap(df,svgHomicide,'Homicides','homicidio doloso',quantizeRed,'#homicide-title',topoName,tipHom,HomicidesA[0]);console.timeEnd("findmap");createLegend('#legend-homicides',quantizeRed)
});});});annualizedRate=function(x){return Math.round(x.count/x.population*100000*12*10)/10}
crimeCounts=function(x){return x.count}
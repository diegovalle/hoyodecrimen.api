//var partialURL = 'https://hoyodecrimen.com';
var i;
var errors = [];
require("utils").dump(casper.cli.options);

partialURL = casper.cli.options['url'];

// var url = '/api/v1/crimes';

// const request = require('request');

// request(partialURL + url, function(error, response, body) {
//     if (!error && response.statusCode === 200) {
//         const fbResponse = JSON.parse(body);
//         console.log("Got a response: ", fbResponse.rows);
//     } else {
//         console.log("Got an error: ", error, ", status code: ", response.statusCode);
//     }
// });

casper.test.begin(
    'Visit hoyodecrimen pages and check for errors',
    1,
    function suite(test) {
        casper.start(partialURL + '/', function() {
            this.wait(35000, function() {
                test.assertTitle('Crimen en la Ciudad de México - Averigua' +
                                 ' cuantos delitos se cometieron por tu rumbo',
                                 'homepage title is the one expected');
                //test.assertExists('svg path', 'chart exists');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 11;
                }, '/ 10 charts of crime + 1 leaflet map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-main-area').length === 5;
                }, '/ 5 charts of crime');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > g.mg-barplot').length === 5;
                }, '/ 5 bar plots of crime');
            });
        });

        casper.thenOpen(partialURL + '/en/', function() {
            this.wait(35000, function() {
                test.assertTitle('Mexico City Crime - See how your' +
                                 ' neighborhood rated for violent and ' +
                                 'property crimes',
                                 'homepage title is the one expected');
                //test.assertExists('svg path', 'chart exists');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 11;
                }, '/en/ 10 charts of crime + 1 leaflet map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-main-area').length === 5;
                }, '/en/ 5 charts of crime');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > g.mg-barplot').length === 5;
                }, '/en/ 5 bar plots of crime');
            });
        });

        casper.thenOpen(partialURL + '/tasas', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/tasas');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/tasas- crime drop down');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 72;
                }, '/tasas - map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/tasas - line chart');
            });
        });

        casper.thenOpen(partialURL + '/en/rates', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/rates');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/rates - crime dropdown');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 72;
                }, '/rates -  map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/rates - line chart');
            });
        });

        casper.thenOpen(partialURL + '/numero', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/numero');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/numero - crime dropdown');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 848;
                }, '/numero - map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/numero - line chart');
            });
        });

        casper.thenOpen(partialURL + '/en/counts', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/counts');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/counts - crime dropdown');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 848;
                }, '/counts -  map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/counts - line chart');
            });
        });

        casper.thenOpen(partialURL + '/mapa', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('#slider-date').length === 1;
                }, '/mapa - slider-date');
                test.assertEval(function() {
                    return __utils__
                        .findAll('#slider-hour').length === 1;
                }, '/mapa - slider hour');
                test.assertEval(function() {
                    return __utils__
                        .findAll('.leaflet-container').length === 1;
                }, '/mapa - carto map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/mapa - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/en/map', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('#slider-date').length === 1;
                }, '/en/map - slider-date');
                test.assertEval(function() {
                    return __utils__
                        .findAll('#slider-hour').length === 1;
                }, '/en/map - slider hour');
                test.assertEval(function() {
                    return __utils__
                        .findAll('.leaflet-container').length === 1;
                }, '/en/map - carto map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/en/map - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/sectores-mapa', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 2;
                }, '/sectores-mapa - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 75;
                }, '/sectores-mapa - carto map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/sectores-mapa - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/en/sectores-map', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 2;
                }, '/en/sectores - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 75;
                }, '/en/sectores - map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/en/sectores - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/cuadrantes-mapa', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 2;
                }, '/cuadrantes-mapa - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 847;
                }, '/cuadrantes-mapa - map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/cuadrantes-mapa - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/en/cuadrantes-map', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 2;
                }, '/en/cuadrantes-map - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g > path').length === 847;
                }, '/en/cuadrantes-map - map');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/en/cuadrantes-map - crime dropdown');
            });
        });

        casper.thenOpen(partialURL + '/crimen', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length >= 5;
                }, '/crimen - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('div#lineHOMICIDIO-DOLOSO svg path.mg-main-line').length === 3;
                }, '/crimen - 3 lines for homicides');
            });
        });

        casper.thenOpen(partialURL + '/en/crime', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length >= 5;
                }, '/crimen - map and chart');
                test.assertEval(function() {
                    return __utils__
                        .findAll('div#lineHOMICIDIO-DOLOSO svg path.mg-main-line').length === 3;
                }, '/crimen - 3 lines for homicides');
            });
        });

        casper.thenOpen(partialURL + '/charts', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 72;
                }, '/charts - svg');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 72;
                }, '/charts - lines');
            });
        });

        casper.thenOpen(partialURL + '/en/charts', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg').length === 72;
                }, '/en/charts - svg');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 72;
                }, '/en/charts - lines');
            });
        });

        casper.thenOpen(partialURL + '/hora', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g.mg-histogram').length >= 5;
                }, '/hora - charts');
            });
        });

        casper.thenOpen(partialURL + '/en/hours', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g.mg-histogram').length >= 5;
                }, '/en/hours - charts');
            });
        });

        casper.thenOpen(partialURL + '/dia', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g.mg-histogram').length >= 5;
                }, '/dia - svg');
            });
        });

        casper.thenOpen(partialURL + '/en/days', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg g.mg-histogram').length >= 5;
                }, '/en/days - svg');
            });
        });

        casper.thenOpen(partialURL + '/tendencias', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/tendencias');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/tendencias - crime dropdown');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 848;
                }, '/tendencias - map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/tendencias - line chart');
            });
        });

        casper.thenOpen(partialURL + '/en/trends', function() {
            this.wait(35000, function() {
                test.assertEval(function() {
                    return __utils__
                        .findAll('.chart-crime').length === 1;
                }, '/en/trend');
                test.assertEval(function() {
                    return __utils__
                        .findAll('option').length >= 5;
                }, '/en/trend - crime dropdown');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg path').length === 848;
                }, '/en/trend -  map of sectores');
                test.assertEval(function() {
                    return __utils__
                        .findAll('svg > path.mg-line1-color').length === 1;
                }, '/en/trends - line chart');
            });
        });


        casper.thenOpen(partialURL + '/acerca', function() {
        });
        casper.thenOpen(partialURL + '/en/about', function() {
        });
        casper.thenOpen(partialURL + '/apple-touch-icon.png', function() {
        });
        casper.thenOpen(partialURL + '/favicon.ico', function() {
        });

        casper.thenOpen(partialURL + '/robots.txt', function() {
        });
        casper.thenOpen(partialURL + '/sitemap.xml', function() {
        });
        casper.thenOpen(partialURL + '/google055ef027e7764e4d.html', function() {
        });
        casper.thenOpen(partialURL + '/mu-01188fe9-0b813050-b0f51076-c96f41fb.txt', function() {
        });

        casper.test.on("fail", function () {
            setTimeout(function(){
                phantom.exit(1);
            }, 0);
        });

        casper.on('page.error', function(msg, trace) {
            this.echo('Error:    ' + msg, 'ERROR');
            this.echo('file:     ' + trace[0].file, 'WARNING');
            this.echo('line:     ' + trace[0].line, 'WARNING');
            this.echo('function: ' + trace[0]['function'], 'WARNING');
            errors.push(msg);
            test.fail('console error');
        });

        casper.on('resource.received', function(resource) {
            var status = resource.status;
            if (status >= 400) {
                test.fail('Resource ' + resource.url +
                          ' failed to load (' + status + ')', 'error');
                casper.log('Resource ' + resource.url +
                           ' failed to load (' + status + ')', 'error');

                errors.push({
                    url: resource.url,
                    status: resource.status
                });
            }
        });

        casper.run(function() {
            if (errors.length > 0) {
                this.echo(errors.length +
                          ' Javascript errors found', 'WARNING');
            } else {
                this.echo(errors.length + ' Javascript errors found', 'INFO');
            }
            casper.exit();
        });
    }
);

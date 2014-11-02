var top5;
var app = angular.module('myApp', ['pascalprecht.translate','ngTable', 'ngResource'])
    .controller('DemoCtrl', function($scope, $timeout, $resource, ngTableParams) {
        
        var Api = $resource(anuglar_table_url);
        Api.get(function(data) {
            $timeout(function() {
                // update table params
                // params.total(data.total);
                // set new data
                top5 = data.rows;
                params1 = new ngTableParams({
                    page: 1,            // show first page
                    count: 10,          // count per page
                    sorting: {
                        name: 'asc'     // initial sorting
                    }
                }, {
                    total: 0,           // length of data
                    counts: [],
                    getData: function($defer, params) {
                        // ajax request to api
                        $defer.resolve(top5)
                    }
                });
                params2 = new ngTableParams({
                    page: 1,            // show first page
                    count: 10,          // count per page
                    sorting: {
                        name: 'asc'     // initial sorting
                    }
                }, {
                    total: 0,           // length of data
                    counts: [],
        getData: function($defer, params) {
            // ajax request to api
            $defer.resolve(top5)
        }
                });
                params3 = new ngTableParams({
                    page: 1,            // show first page
                    count: 10,          // count per page
                    sorting: {
                        name: 'asc'     // initial sorting
                    }
                }, {
                    total: 0,           // length of data
                    counts: [],
                    getData: function($defer, params) {
                        // ajax request to api
                        $defer.resolve(top5)
                    }
                });
params4 = new ngTableParams({
    page: 1,            // show first page
    count: 10,          // count per page
    sorting: {
        name: 'asc'     // initial sorting
    }
}, {
    total: 0,           // length of data
    counts: [],
    getData: function($defer, params) {
        // ajax request to api
        $defer.resolve(top5)
        }
});
                params5 = new ngTableParams({
                    page: 1,            // show first page
                    count: 10,          // count per page
                    sorting: {
                        name: 'asc'     // initial sorting
                    }
                }, {
                    total: 0,           // length of data
                    counts: [],
                    getData: function($defer, params) {
                        // ajax request to api
                        $defer.resolve(top5)
                    }
                });
                $scope.tableParams1 = params1;
                $scope.tableParams2 = params2;
                $scope.tableParams3 = params3;
                $scope.tableParams4 = params4;
                $scope.tableParams5 = params5;
            }, 500);
        });
    
        
    });

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

app.config(['$translateProvider', function ($translateProvider) {
    $translateProvider.translations('en', {
        'TITLE': 'Hello',
        'FOO': 'This is a paragraph'
    });
    
    $translateProvider.translations('de', {
        'TITLE': 'Hallo',
        'FOO': 'Dies ist ein Paragraph'
    });
    
    $translateProvider.preferredLanguage('en');
}]);





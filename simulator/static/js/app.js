var app = angular.module('app', [])
.config(function($httpProvider) {
   $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});
// Diretiva para carregar os charts.
app.directive('highchart', function () {
    return {
        restrict: 'E',
        template: '<div></div>',
        replace: true,
    
        link: function (scope, element, attrs) {
    
            scope.$watch(function () { return attrs.chart; }, function () {
    
                if (!attrs.chart) return;
    
                var charts = JSON.parse(attrs.chart);
    
                $(element[0]).highcharts(charts);
    
            });
        }
    };
    });
var app = angular.module('app', []).config(function($httpProvider) {
   $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

app.controller('SimuladorController', function($scope) {
   $scope.rho = 0.8;
});
(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http) {
       $scope.rho = 0.8;
       $scope.results = {
           'e_w': null,
           'v_w': null,
           'e_nq': null,
           'v_nq': null
       };
       $scope.simular = function(rho) {
        $http.post('/simular/' + rho + '/')
          .then( res => $scope.results = res.data);
       }
    });
})();
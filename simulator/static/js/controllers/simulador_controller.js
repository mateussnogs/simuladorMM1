(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http) {
        $scope.rho = 0.8;
        $scope.disciplina = 'FCFS';
        $scope.kmin = 100;
        $scope.rodadas = 32;
        $scope.showLoader = false;
        $scope.results = {
           'e_w': null,
           'v_w': null,
           'e_nq': null,
           'v_nq': null
        };
        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            $scope.showLoader = true;
            console.log('vou rodar')
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.results = res.data;
                $scope.showLoader = false;
            });
        }
    });
})();
(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http) {
        $scope.rho = 0.8;
        $scope.disciplina = 'FCFS';
        $scope.kmin = 100000;
        $scope.rodadas = 1;
        $scope.showLoader = false;
        $scope.results = {
           'e_w': null,
           'v_w': null,
           'e_nq': null,
           'v_nq': null
        };
        $scope.chartsW ={
            '0.2': null,
            '0.4': null,
            '0.6': null,
            '0.8': null,
            '0.9': null
        }
        $scope.chartsNq ={
            '0.2': null,
            '0.4': null,
            '0.6': null,
            '0.8': null,
            '0.9': null
        }
        $scope.plotCharts = function (rho){
            $scope.chartsW[rho] = {
                chart: {
                    type: 'line'
                },
                plotOptions:{
                    series:{
                        pointStart: 0	
                    }
                },
                series:  [Range($scope.kmin), $scope.results['EWs']],
                title: {
                    text: "E[W]"
                },
                xAxis: {
                title: {
                    text: 'k'
                }
            }
            };
        }

        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            $scope.showLoader = true;
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.results = res.data;
                $scope.showLoader = false;
            });
        }
    });
})();
(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http) {
        $scope.rho = 0.8;
        $scope.disciplina = 'FCFS';
        $scope.kmin = 1000;
        $scope.rodadas = 3200;
        $scope.showLoader = false;
        $scope.results = {
           'e_w': null,
           'v_w': null,
           'e_nq': null,
           'v_nq': null
        };
        $scope.plotCharts = function (rho, disciplina) {
            var chart = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chartW',
                    width: 420
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots['W']
                },{
                    name: 'Medias moveis',
                    data: $scope.plots['MMW']
                }],
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            var chart1 = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chartV',
                    width: 420
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'V(W)',
                    data: $scope.plots['V']
                },{
                    name: 'Medias moveis',
                    data: $scope.plots['MMV']
                }],
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            $scope.chartReady = true;
        };

        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            $scope.showLoader = true;
            $scope.results = {
                'e_w': null,
                'v_w': null,
                'e_nq': null,
                'v_nq': null,
                'ic_ew_low': null,
                'ic_ew_high': null,
                'ic_ew_pres': null,
                'ic_enq_low': null,
                'ic_enq_high': null,
                'ic_enq_pres': null,
                'ic_vwt_low': null,
                'ic_vwt_high': null,
                'ic_vwt_pres': null,
                'ic_vwchi_low': null,
                'ic_vwchi_high': null,
                'ic_vwchi_pres': null,
                'ic_vnqt_low': null,
                'ic_vnqt_high': null,
                'ic_vnqt_pres': null,
                'ic_vnqchi_low': null,
                'ic_vnqchi_high': null,
                'ic_vnqchi_pres': null
             };
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.results = res.data;
                $scope.showLoader = false;
            });
        }
        $scope.simular_toplot = function(rho, disciplina, kmin, rodadas) {
            console.log('rodar');
            $scope.chartReady = false;
            $scope.showLoader = true;
            $http.post('/simulartoplot/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.plots = res.data;
                $scope.showLoader = false;
                console.log('parei')
                $scope.plotCharts(rho, disciplina);
            });
        }
    });
})();
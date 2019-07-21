(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http, $interval) {
        $scope.rho = 0.9;
        $scope.rodada = 0
        $scope.disciplina = 'FCFS';
        $scope.kmin = 2500;
        $scope.rodadas = 3200;
        $scope.showLoader = false;
        $scope.rodada_atual = null;
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
                    width: 520
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
                    width: 520
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
            var chart2 = new Highcharts.Chart({
                chart: {
                    renderTo: 'chartENq',
                    width: 1200
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E(Nq)',
                    data: $scope.plots['ENq']
                }],/*{
                    name: 'Medias moveis',
                    data: $scope.plots['MMENq']
                }],*/
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            var chart3 = new Highcharts.Chart({
                chart: {
                    renderTo: 'chartVNq',
                    width: 1200
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'V(Nq)',
                    data: $scope.plots['VNq']
                }],/*{
                    name: 'Medias moveis',
                    data: $scope.plots['MMVNq']
                }],*/
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            $scope.chartReady = true;
        };

        $scope.get_rodada = function() {            
            $http.get('/rodada')
            .then(function(res) {
                $scope.res = res.data;
                $scope.rodada = $scope.res['rodada_atual']+1;
            });
        };

        var check_status;
        $scope.status_simulador = function() {
            
            $http.get('/status')
            .then(function(res) {
                $scope.res = res.data;
                if ($scope.res['status'] == 'ended') {
                    $scope.showLoader = false;                
                    $interval.cancel($scope.rodada_atual);
                    $interval.cancel(check_status);
                    $http.get('/resultado')
                    .then(function(result) {
                        $scope.results = result.data;
                    });
                }
            });
        };

        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            // var rodada;
            $scope.rodada_atual = $interval($scope.get_rodada, 1000, rodadas);
            check_status = $interval($scope.status_simulador, 1000, rodadas);
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
                $scope.get_rodada(); // pega rodada ultima vez para ter o ultimo valor
                $scope.results = res.data;
                // $scope.showLoader = false;                
                // $interval.cancel(rodada);
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
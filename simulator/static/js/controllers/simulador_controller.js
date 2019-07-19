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
        $scope.plotCharts = function () {
            var chart = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chart2',
                    width: 1000
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots[0]['W']
                },{
                    name: 'V(W)',
                    data: $scope.plots[0]['V']
                }],
                title: {
                    text: 'Taxa 0,2'
                }
            });
            var chart2 = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chart4',
                    width: 1000
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots[1]['W']
                },{
                    name: 'V(W)',
                    data: $scope.plots[1]['V']
                }],
                title: {
                    text: 'Taxa 0,4'
                }
            });
            var chart3 = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chart6',
                    width: 1000
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots[2]['W']
                },{
                    name: 'V(W)',
                    data: $scope.plots[2]['V']
                }],
                title: {
                    text: 'Taxa 0,6'
                }
            });
            var chart4 = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chart8',
                    width: 1000
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots[3]['W']
                },{
                    name: 'V(W)',
                    data: $scope.plots[3]['V']
                }],
                title: {
                    text: 'Taxa 0,8'
                }
            });
            var chart5 = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chart9',
                    width: 1000
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E[W]',
                    data: $scope.plots[4]['W']
                },{
                    name: 'V(W)',
                    data: $scope.plots[4]['V']
                }],
                title: {
                    text: 'Taxa 0,9'
                }
            });
        };

        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            $scope.showLoader = true;
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.results = res.data;
                $scope.showLoader = false;
            });
        }
        $scope.simular_toplot = function(rho, disciplina, kmin, rodadas) {
            let r = [0.2, 0.4, 0.6, 0.8, 0.9]
            let plots = []
            for( let i in r){
               console.log('rodar');
                $http.post('/simulartoplot/' + r[i] + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
                .then(function(res) {
                    plots.push(res.data);
                    $scope.showLoader = false;
                    console.log('parei')
                });
            }
            $scope.plots = plots;
        }
    });
})();
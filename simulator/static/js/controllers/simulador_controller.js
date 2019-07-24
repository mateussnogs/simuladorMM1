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
        $scope.check_status = null;
        $scope.simulando = false;
        $scope.results = {
           'e_w': null,
           'v_w': null,
           'e_nq': null,
           'v_nq': null
        };

        // para acessar elemento: analiticos[DISCIPLINA][METRICA][UTILIZACAO]
        $scope.analiticos = {
            'FCFS':{            
                'EW': {'0.2': 0.25, '0.4': 0.66, '0.6': 1.50, '0.8': 4.00, '0.9': 9.00 },
                'VW': {'0.2': 0.56, '0.4': 1.77, '0.6': 5.24, '0.8': 24.00, '0.9': 99.00},
            },
            'LCFS':{
                'EW': {'0.2': 0.25, '0.4': 0.66, '0.6': 1.50, '0.8': 4.00, '0.9': 9.00 },
                'VW': {'0.2': 0.71, '0.4': 3.25, '0.6': 16.50, '0.8': 184.00, '0.9': 1719.00},
            }
        };

        $scope.plotCharts = function (rho, disciplina) {
            var chart = new Highcharts.Chart({
                
                chart: {
                    renderTo: 'chartEW',
                    width: 800
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
                    renderTo: 'chartVW',
                    width:800
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
                    width: 800
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'E(Nq)',
                    data: $scope.plots['ENq']
                },{
                    name: 'Medias moveis',
                    data: $scope.plots['MMNq']
                }],
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            var chart3 = new Highcharts.Chart({
                chart: {
                    renderTo: 'chartVNq',
                    width: 800
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: 'V(Nq)',
                    data: $scope.plots['VNq']
                },{
                    name: 'Medias moveis',
                    data: $scope.plots['MMVNq']
                }],
                title: {
                    text: 'Disciplina ' + disciplina + ' e Taxa ' + rho
                }
            });
            $scope.chartReady = true;
            $scope.showLoader = false;
        };

        $scope.plotRChart = function (metrica, icname) {
            let icrange = [$scope.results[icname + 'low'], $scope.results[icname + 'high']];
            //metrica = 'toplot_' + metrica;
            let l = $scope.results['toplot_' + metrica].length;
            let icarangear = [];
            for(var i=0; i<l; i++){
                icarangear[i] = [i, icrange[0], icrange[1]];
            }
            var chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'graph_results',
                    width: 1200
                },
                plotOptions: {
                    series: {
                        pointStart: 1
                    }
                },
                series: [{
                    name: name,
                    data: $scope.results['toplot_' + metrica],
                    color: 'black'
                },{
                    type: 'arearange',
                    name: 'IC',
                    data: icarangear,
                    color: 'yellow'
                }],
            });            
        };

        $scope.plotICChart = function (metrica, icname) {         
            let inf = $scope.results[icname + 'low']
            let sup = $scope.results[icname + 'high']
            let center = (inf+sup)/2;
            var chart_ic_ew = new Highcharts.Chart({

                chart: {
                    renderTo: 'ic_ew',
                    inverted: false
                },
                title: {
                    text: 'Confidence intervals'
                },
        
                xAxis: {
                    categories: ['Item #1']
                },
        
                yAxis: [{
                    title: {
                        text: metrica
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos['FCFS'][metrica.toString()]['0.9'],
                                   color: 'red',
                                   width: 1
                    }]
                }],
        
        
                plotOptions: {
                    columnrange: {
                        grouping: false,
                        color: 'navy'
                    },
                    scatter: {
                        color: 'navy',
                        marker: {
                            symbol: 'diamond'
                   
                        }
                    }        
                },                
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                series: [{
                    type: 'columnrange',
                    pointWidth: 2,
                    data: [
                        [inf, sup],
                    //  [inf_chi, sup_chi]
                    ]            
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [sup, sup], // plota a linha superior
                    //  [sup_chi, sup_chi]  
                    ]            
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [inf, inf], // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ]            
                }, {
                    type: 'scatter',
                    data: [
                        [center], // ponto do centro
                    //  [center_chi]  
                    ]
                }]
            });
        };

        $scope.get_rodada = function() {            
            $http.get('/rodada')
            .then(function(res) {
                $scope.res = res.data;
                $scope.rodada = $scope.res['rodada_atual']+1;
            });
        };

        $scope.status_simulador = function() {
            $http.get('/status')
            .then(function(res) {
                $scope.res = res.data;
                if ($scope.res['status'] == 'ended') { // simulacao acabou
                    $scope.showLoader = false;                
                    $interval.cancel($scope.rodada_atual); // para de checar rodada atual
                    $interval.cancel($scope.check_status); // para de checar status do simulador
                    $scope.simulando = false;
                    $http.get('/resultado') // pega resultado da simulacao
                    .then(function(result) {
                        $scope.results = result.data;
                        console.log(result.data)
                    });
                }
            });
        };

        $scope.simular = function(rho, disciplina, kmin, rodadas) {
            $scope.simulando = true;
            $http.get('/limpar') // limpa logs de simulaçoes passadas
                .then(function(result) {
                    console.log(result.data)
                });
            $scope.rodada_atual = $interval($scope.get_rodada, 1000, rodadas); // ativa checagem rodada
            $scope.check_status = $interval($scope.status_simulador, 1000, rodadas); // ativa checagem simulacao
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
                'ic_vnqchi_pres': null,
                'toplot_EW': null,
                'toplot_VW': null,
                'toplot_ENq': null,
                'toplot_VNq': null
             };
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.results = res.data; // obsoleto(response, de fato, ja nao vem mais por aqui)
            });
        }
        $scope.simular_toplot = function(rho, disciplina, kmin, rodadas) {
            console.log('rodar');
            $scope.chartReady = false;
            $scope.showLoader = true;
            $http.post('/simulartoplot/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/')
            .then(function(res) {
                $scope.plots = res.data;
                console.log('parei')
                $scope.plotCharts(rho, disciplina);
            });
        }
    });
})();
(function() {
    'use strict';
    angular.module('app').controller('SimuladorController', function($scope, $http, $interval) {
        $scope.rho = 0.9;
        $scope.rodada = 0
        $scope.disciplina = 'FCFS';
        $scope.kmin = 2500;
        $scope.rodadas = 3200;
        $scope.seed_esperta = false;
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
                'EW': {'0.2': 0.25, '0.4': 0.6667, '0.6': 1.50, '0.8': 4.00, '0.9': 9.00 },
                'VW': {'0.2': 0.5625, '0.4': 1.7778, '0.6': 5.25, '0.8': 24.00, '0.9': 99.00},
                'ENq': {'0.2': 0.05, '0.4': 0.2667, '0.6': 0.9, '0.8': 3.20, '0.9': 8.10},
                'VNq': {'0.2': 0.0725, '0.4': 0.5511, '0.6': 2.79, '0.8': 18.56, '0.9': 88.29}
            },
            'LCFS':{
                'EW': {'0.2': 0.25, '0.4': 0.6667, '0.6': 1.50, '0.8': 4.00, '0.9': 9.00 },
                'VW': {'0.2': 0.7187, '0.4': 3.2592, '0.6': 16.50, '0.8': 184.00, '0.9': 1719.00},
                'ENq': {'0.2': 0.05, '0.4': 0.2667, '0.6': 0.9, '0.8': 3.20, '0.9': 8.10},
                'VNq': {'0.2': 0.0725, '0.4': 0.5511, '0.6': 2.79, '0.8': 18.56, '0.9': 88.29}
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

        $scope.plotICCharts = function (disciplina, rho) {         
            var chart_ic_ew = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_ew',
                    inverted: false,
                    width: 350,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                xAxis: {
                    categories: ['E[W]']
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['EW'][rho],
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
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [$scope.results['ic_ew_low'], $scope.results['ic_ew_high']]
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC T-Student'
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_ew_high'], $scope.results['ic_ew_high']] // plota a linha superior
                    //  [sup_chi, sup_chi]  
                    ],
                    enableMouseTracking: false         
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_ew_low'], $scope.results['ic_ew_low']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                }, {
                    type: 'scatter',
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [($scope.results['ic_ew_low'] + $scope.results['ic_ew_high'])/2] // ponto do centro
                    //  [center_chi]  
                    ],
                    enableMouseTracking: false
                }]
            });
            var chart_ic_vw = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_vw',
                    inverted: false,
                    width: 350,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                xAxis: {
                    categories: ['T-Stu V(W)', 'Chi V(W)']
                },
                yAxis: [{
                    title: {
                        text:' Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['VW'][rho],
                                   color: 'red',
                                   width: 1
                    }]
                }],
                plotOptions: {
                    
                    columnrange: {
                        grouping: false,
                        color: 'navy',
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
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y,4);
                        }
                    },
                    pointWidth: 2,
                    data: [
                        [$scope.results['ic_vwt_low'], $scope.results['ic_vwt_high']],
                        [$scope.results['ic_vwchi_low'], $scope.results['ic_vwchi_high']]
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC T-Student'
                }, /*{
                    type: 'columnrange',
                    pointWidth: 2,
                    data: [
                        [$scope.results['ic_vwchi_low'], $scope.results['ic_vwchi_high']]
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC Chi-Quadrado'
                },*/{
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vwt_high'], $scope.results['ic_vwt_high']], // plota a linha superior
                        [$scope.results['ic_vwchi_high'], $scope.results['ic_vwchi_high']] // plota a linha superior
                    //  [sup_chi, sup_chi]  
                    ],
                    enableMouseTracking: false         
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vwt_low'], $scope.results['ic_vwt_low']], // plota a linha inferior
                        [$scope.results['ic_vwchi_low'], $scope.results['ic_vwchi_low']] // plota a linha superior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                },/* {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vwchi_high'], $scope.results['ic_vwchi_high']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vwchi_low'], $scope.results['ic_vwchi_low']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                },*/ {
                    type: 'scatter',
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [($scope.results['ic_vwt_low'] + $scope.results['ic_vwt_high'])/2], // ponto do centro
                        [($scope.results['ic_vwchi_low'] + $scope.results['ic_vwchi_high'])/2] // ponto do centro
                    //  [center_chi]  
                    ],
                    enableMouseTracking: false
                }]
            });
            var chart_ic_enq = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_enq',
                    inverted: false,
                    width: 350,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                xAxis: {
                    categories: ['E[Nq]']
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['ENq'][rho],
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
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [$scope.results['ic_enq_low'], $scope.results['ic_enq_high']]
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC T-Student'
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_enq_high'], $scope.results['ic_enq_high']] // plota a linha superior
                    //  [sup_chi, sup_chi]  
                    ],
                    enableMouseTracking: false         
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_enq_low'], $scope.results['ic_enq_low']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                }, {
                    type: 'scatter',
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [($scope.results['ic_enq_low'] + $scope.results['ic_enq_high'])/2] // ponto do centro
                    //  [center_chi]  
                    ],
                    enableMouseTracking: false
                }]
            });
            var chart_ic_vnq = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_vnq',
                    inverted: false,
                    width:350
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                xAxis: {
                    categories: ['T-Stu V(Nq)', 'Chi V(Nq)']
                },
                yAxis: [{
                    title: {
                        text:' Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['VNq'][rho],
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
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [$scope.results['ic_vnqt_low'], $scope.results['ic_vnqt_high']],
                        [$scope.results['ic_vnqchi_low'], $scope.results['ic_vnqchi_high']],
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC T-Student'
                },/* {
                    type: 'columnrange',
                    pointWidth: 2,
                    data: [
                        [$scope.results['ic_vnqchi_low'], $scope.results['ic_vnqchi_high']]
                    //  [inf_chi, sup_chi]
                    ],
                    name: 'IC Chi-Quadrado'
                },*/{
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vnqt_high'], $scope.results['ic_vnqt_high']], // plota a linha superior
                        [$scope.results['ic_vnqchi_high'], $scope.results['ic_vnqchi_high']]
                    //  [sup_chi, sup_chi]  
                    ],
                    enableMouseTracking: false         
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vnqt_low'], $scope.results['ic_vnqt_low']], // plota a linha inferior
                        [$scope.results['ic_vnqchi_low'], $scope.results['ic_vnqchi_low']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                },/* {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vnqchi_high'], $scope.results['ic_vnqchi_high']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                }, {
                    type: 'columnrange',
                    pointWidth: 15,
                    minPointLength: 2,
                    data: [
                        [$scope.results['ic_vnqchi_low'], $scope.results['ic_vnqchi_low']] // plota a linha inferior
                    //  [inf_chi, inf_chi]  
                    ] ,
                    enableMouseTracking: false           
                },*/ {
                    type: 'scatter',
                    dataLabels: {
                        enabled: true,
                        // inside: true,
                        formatter: function () {
                            return Highcharts.numberFormat(this.y, 4);
                        }
                    },
                    data: [
                        [($scope.results['ic_vnqt_low'] + $scope.results['ic_vnqt_high'])/2], // ponto do centro
                        [($scope.results['ic_vnqchi_low'] + $scope.results['ic_vnqchi_high'])/2] // ponto do centro
                    //  [center_chi]  
                    ],
                    enableMouseTracking: false
                }]
            });

        };

        $scope.plotICCharts_kmin = function (disciplina, rho) {         
            var chart_ic_ew = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_ew',
                    inverted: false,
                    width: 500,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['EW'][rho],
                                   color: 'red',
                                   width: 1,
                                   zIndex: 5
                    }]
                }],            
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                series: [{
                    type: 'columnrange',
                    name: 'ICs',
                    data: $scope.results['ic_ew'],
                    enableMouseTracking: false,
                    color: '#7cb5ec'
                }]
            });
            var chart_ic_vw = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_vw',
                    inverted: false,
                    width: 500,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['VW'][rho],
                                   color: 'red',
                                   width: 1,
                                   zIndex: 5
                    }]
                }],            
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    columnrange: {
                        grouping: false
                    }
                },
                series: [{
                    type: 'columnrange',
                    name: 'ICs',
                    data: $scope.results['ic_vwt'],
                    enableMouseTracking: false,
                    color: '#7cb5ec'
                }, {
                    type: 'columnrange',
                    name: 'ICs',
                    data: $scope.results['ic_vwchi'],
                    enableMouseTracking: false,
                    color: '#7cb5ec',
                    opacity: 0.6
                }]
            });
            var chart_ic_enq = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_enq',
                    inverted: false,
                    width: 500,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['ENq'][rho],
                                   color: 'red',
                                   width: 1,
                                   zIndex: 5
                    }]
                }],            
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    columnrange: {
                        grouping: false
                    }
                },
                series: [{
                    type: 'columnrange',
                    name: 'ICs',
                    data: $scope.results['ic_enq'],
                    enableMouseTracking: false,
                    color: '#7cb5ec'
                }]
            });
            var chart_ic_vnq = new Highcharts.Chart({
                chart: {
                    renderTo: 'ic_vnq',
                    inverted: false,
                    width: 500,
                },
                title: {
                    text: 'Intervalo de Confiança'
                },
                yAxis: [{
                    title: {
                        text:  'Valor Analítico'
                    },
                    gridZIndex: -1,
                    // plota a linha com o valor do analitico pra mostrar se cai no IC ou nao
                    plotLines: [{  value: $scope.analiticos[disciplina]['VNq'][rho],
                                   color: 'red',
                                   width: 1,
                                   zIndex: 5
                    }]
                }],        
                plotOptions: {
                    columnrange: {
                        grouping: false
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
                    name: 'ICs',
                    data: $scope.results['ic_vnqt'],
                    enableMouseTracking: false,
                    color: '#7cb5ec'
                }, {
                    type: 'columnrange',
                    name: 'ICs',
                    data: $scope.results['ic_vnqchi'],
                    enableMouseTracking: false,
                    color: '#7cb5ec',
                    opacity: 0.6
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

        $scope.status_simulador = function(disciplina, rho) {
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
                        var date = new Date();
                        $scope.tempo_process = ((date.getTime() - $scope.momento_inicial)/1000)/60;
                        if($scope.hasKResults){
                            $scope.plotICCharts_kmin($scope.disciplina, $scope.rho);
                        }
                        else{
                            $scope.plotICCharts($scope.disciplina, $scope.rho);
                        }
                        console.log(result.data)
                    });
                }
            });
        };

        $scope.simular = function(rho, disciplina, kmin, rodadas, seed_esperta) {
            $scope.hasKResults = false;
            var date = new Date();
            $scope.tempo_process = null;
            $scope.simulando = true;
            $http.get('/limpar') // limpa logs de simulaçoes passadas
                .then(function(result) {
                    console.log(result.data)
                });
                $scope.momento_inicial = date.getTime();
            $scope.rodada_atual = $interval($scope.get_rodada, 1000, rodadas); // ativa checagem rodada
            $scope.check_status = $interval($scope.status_simulador, 1000, rodadas); // ativa checagem simulacao
            $scope.showLoader = true;
            $scope.disciplina = disciplina;
            $scope.rho = rho;
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
             seed_esperta = seed_esperta ? 1:0;
            $http.post('/simular/' + rho + '/' + disciplina + '/' + kmin + '/' + rodadas + '/' + seed_esperta + '/')
            .then(function(res) {
                $scope.results = res.data; // obsoleto(response, de fato, ja nao vem mais por aqui)
                $scope.hasTableResults = true;
            });
        }
        $scope.simularkmin = function(rho, disciplina, rodadas, seed_esperta) {
            $scope.hasTableResults = false;
            var date = new Date();
            $scope.tempo_process = null;
            $scope.simulando = true;
            $http.get('/limpar') // limpa logs de simulaçoes passadas
                .then(function(result) {
                    console.log(result.data)
                });
            $scope.momento_inicial = date.getTime();
            $scope.rodada_atual = $interval($scope.get_rodada, 1000, rodadas); // ativa checagem rodada
            $scope.check_status = $interval($scope.status_simulador, 1000, rodadas); // ativa checagem simulacao
            $scope.showLoader = true;
            $scope.disciplina = disciplina;
            $scope.rho = rho;
            seed_esperta = seed_esperta ? 1:0;
            $http.post('/simular_kmin/' + rho + '/' + disciplina + '/' + rodadas + '/' + seed_esperta + '/')
            .then(function(res) {
                $scope.results = res.data; // obsoleto(response, de fato, ja nao vem mais por aqui)
                $scope.hasKResults = true;
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
        $scope.simular_deterministic = function(disciplina) {
            $http.post('/simulardeterministico/' + disciplina + '/')
            .then(function(res) {
                console.log('runed')
                $scope.respDeterministico = res.data;
            });
        }
        $scope.startanimation = function(disciplina){
            resetWatch();
            startWatch();
            $http.post('/simulardeterministico/' + disciplina + '/')
            .then(function(res) {
                console.log('runed')
                $scope.respDeterministico = res.data;
            });
            var img1 = $("#x1");
            var img2 = $("#x2");
            var img3 = $("#x3");
            var img4 = $("#x4");
            var img5 = $("#x5");
            var img6 = $("#x6");
            console.log('add')
            img1.addClass("man1");
            img2.addClass("man2");
            img3.addClass("man3");
            img4.addClass("man4");
            img5.addClass("man5");
            img6.addClass("man6");
            setTimeout(function() {
                img1.removeClass("man1");
                img2.removeClass("man2");
                img3.removeClass("man3");
                img4.removeClass("man4");
                img5.removeClass("man5");
                img6.removeClass("man6");
                setTimeout(function() {
                    console.log('add')
                    img1.addClass("man1");
                    img2.addClass("man2");
                    img3.addClass("man3");
                    img4.addClass("man4");
                    img5.addClass("man5");
                    img6.addClass("man6");
                    setTimeout(function() {
                        img1.removeClass("man1");
                        img2.removeClass("man2");
                        img3.removeClass("man3");
                        img4.removeClass("man4");
                        img5.removeClass("man5");
                        img6.removeClass("man6");
                        setTimeout(function() {
                            console.log('add')
                            img1.addClass("man1");
                            img2.addClass("man2");
                            img3.addClass("man3");
                            img4.addClass("man4");
                            img5.addClass("man5");
                            img6.addClass("man6");
                            setTimeout(function() {
                                stopWatch();
                            }, 35000);
                        }, 1000);
                    }, 34000);
                }, 1000);
            }, 34000);
        }

        //Function to display clock
        var timer = null;
        var min_txt = document.getElementById("min");
        if(min_txt){
            var min = Number(min_txt.innerHTML);
        }
        var sec_txt = document.getElementById("sec");
        if(sec_txt){
            var sec = Number(sec_txt.innerHTML);
        }
        var msec_txt = document.getElementById("msec"); 
        if(msec_txt){
            var msec = Number(msec_txt.innerHTML);
        }
        function stopTimeMilliseconds(timer) {
            if (timer) { 
                clearInterval(timer);
                return timer;
            }
            else return timer;
        }
        function startTimeMilliseconds() {
            var currDate = new Date();
            return currDate.getTime();	
        }
        function getElapsedTimeMilliseconds(startMilliseconds) {
            if (startMilliseconds > 0) {
                var currDate = new Date();
                var elapsedMilliseconds = (currDate.getTime() - startMilliseconds);
                return elapsedMilliseconds;
            }
        else {
            return elapsedMilliseconds = 0;
            }
        }
        function startWatch() { 
            // START TIMER
            timer = stopTimeMilliseconds(timer); 
            var startMilliseconds = startTimeMilliseconds();
            timer = setInterval(function() { 
                var elapsedMilliseconds = getElapsedTimeMilliseconds(startMilliseconds); 
                if (msec < 10) {
                    msec_txt.innerHTML = "00" + msec; 
                }
                else if (msec < 100) {
                    msec_txt.innerHTML = "0" + msec;
                }
                else {
                    msec_txt.innerHTML = msec;
                }
                if (sec < 10) {
                    sec_txt.innerHTML = "0" + sec;
                }
                else {
                    sec_txt.innerHTML = sec; 
                }
                min_txt.innerHTML = min; 
                msec = elapsedMilliseconds;
                if (min >= 59 && sec >=59 && msec > 900) {
                    timer = stopTimeMilliseconds(timer);
                    return true;
                }
                if (sec > 59) {
                    sec = 0;
                    min++;
                }
                if (msec > 999) {
                    msec = 0;
                    sec++;
                    startWatch();
                }
            }, 10);
        }
        function stopWatch() {
            // STOP TIMER
            timer = stopTimeMilliseconds(timer);
            return true;
        }
        function resetWatch() {
            // REZERO TIMER
            timer = stopTimeMilliseconds(timer);
            msec_txt.innerHTML = "000"; 
            msec = 0;
            sec_txt.innerHTML = "00"; 
            sec = 0;
            min_txt.innerHTML = "0"; 
            min = 0;
            return true;
        }
    });
})();
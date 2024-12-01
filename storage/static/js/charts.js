/** 
 * @module charts 
 */
(function (window) {

    /**
     * Чертит графики в соответствии с указанными параметрами
     * 
     * @param {object} params
     * @returns {Chart}
     */
    const draw = function (params) {
        const opts = $.extend({
            canvas: null,
            labels: [],
            datasets: [],
            chart_type: 'line',
            chart_mode: 'vertical',
            datalabels: null,
            outlabels: null
        }, params)

        const no_grids = ['pie', 'doughnut']

        let display_legend = $.grep(opts.datasets, (n, i) => { return ('label' in n) }).length > 0
        let is_horizontal = (opts.chart_mode == 'horizontal')
        const ctx = document.getElementById(opts.canvas).getContext('2d')
        return new Chart(ctx, {
            type: opts.chart_type,
            plugins: [ChartDataLabels],
            data: {
                labels: opts.labels,
                datasets: opts.datasets,
            },
            options: {
                indexAxis: is_horizontal ? 'y' : 'x',
                responsive: true,
                aspectRatio: 1.5,

                maintainAspectRatio: false,
                borderWidth: 2,
                layout: {
                    padding: {
                        top: no_grids.includes(opts.chart_type) ? 50 : 20,
                        bottom: no_grids.includes(opts.chart_type) ? 35 : null
                    }
                },

                cutout: opts.chart_type == 'doughnut' ? '70%' : '0%',
                
                plugins: {
                    legend: {
                        display: display_legend,
                        position: is_horizontal ? 'top' : 'right',
                        maxWidth: 400,
                        labels: {
                            padding: 20,
                        }
                    },

                    datalabels: (() => {
                        if (opts.datalabels) {
                            const ret = {};
                            for (var option in opts.datalabels) {
                                if (option == 'formatter') {
                                    ret.formatter = eval(opts.datalabels.formatter)
                                } else {
                                    ret[option] = opts.datalabels[option]
                                }
                            }
                            return ret
                        }
                        return null
                    })(),
                    
                    outlabels: (() => {
                        if (opts.outlabels) {
                            const ret = {};
                            for (var option in opts.outlabels) {
                                if (option == 'formatter') {
                                    ret.formatter = eval(opts.outlabels.formatter)
                                } else {
                                    ret[option] = opts.outlabels[option]
                                }
                            }
                            return ret
                        }
                        return null
                    })(),
                },
                elements: {
                    bar: {
                        borderWidth: 0,
                    },
                    point: {
                        radius: 5,
                    }
                },

                scales: {
                    y: {
                        grid: {
                            drawBorder: no_grids.includes(opts.chart_type) ? false : true,
                            display: no_grids.includes(opts.chart_type) ? false : true
                        },
                        ticks: {
                            display: no_grids.includes(opts.chart_type) ? false : true,
                            callback: function (value, index, values) {
                                maxlen = 40
                                val = this.getLabelForValue(value)
                                if (val && val.length > maxlen) {
                                    val = val.substring(0, maxlen) + '...'
                                }
                                return val
                            },
                        }
                    },
                    x: {
                        grid: {
                            drawBorder: no_grids.includes(opts.chart_type) ? false : true,
                            display: no_grids.includes(opts.chart_type) ? false : true
                        },
                        ticks: { display: no_grids.includes(opts.chart_type) ? false : true }
                    }
                }
            }
        })
    }


    /**
     * Рисует чарты на основе данных полученных посредством форм
     * 
     * @param {string} forms Селектор форм посредством которых получают данные для чартов
     */
    const draw_form_dependent_charts = function (forms) {
        const charts = {};
        const process = function (form) {
            let currentChart = null
            let msg = null
            app.loading.show()
            $.ajax({ method: "GET", url: form.attr('action'), data: form.serialize() })
                .done(res => {
                    if (res.error) {
                        msg = res.error
                    } else {
                        canvas_id = form.attr('data-canvas')
                        $('#' + canvas_id).show()
                        charts[canvas_id] && charts[canvas_id].destroy()
                        try {
                            if (form.attr('data-chart_mode') == 'horizontal') {
                                $('#' + canvas_id).parent().css('height', 30 * res.labels.length * res.datasets.length + 80 + 'px')
                            }
                            currentChart = draw({
                                canvas: canvas_id,
                                labels: res.labels,
                                datasets: res.datasets,
                                datalabels: res.datalabels ? res.datalabels : null,
                                outlabels: res.outlabels ? res.outlabels : null,
                                chart_type: form.attr('data-chart_type') || 'line',
                                chart_mode: form.attr('data-chart_mode') || 'vertical'
                            })
                        } catch (err) {
                            currentChart && currentChart.destroy()
                            msg = err.message
                        }
                        charts[canvas_id] = currentChart
                    }
                })
                .fail(() => msg= 'Ошибка')
                .always(() => app.loading.hide(msg))
        }

        $(forms).each(function () {
            const form = $(this)
            if (form.hasClass('auto_submit_once') || (form.find('.submit_on_change').find(":selected").index() >= 0)) {
                process(form)
            }
            form.find('.submit_on_change').on('change', function () {
                $(this).trigger('change.before-app-handlers')
                if ($(this).val() || ($(this).find(":selected").index() >= 0)) {
                    process(form)
                }
            })
        })

        return charts
    }


    /**
     * Рисует чарты на основе дата-параметров канваса (канвасы отбираются по атрибуту data-chart-type)
     * Данные берутся из url в data-source или из первой формы в data-form
     * В data-form можно указать несколько форм через заяпятую: "#form1, #form2", в запрос будут добавлены данные из этих форм.
     */
    const draw_canvas_dependent_charts = function () {
        const charts = {}
        const process = function(canvas) {
            const forms = canvas.attr('data-form') ? canvas.attr('data-form').split(/\s*,\s*/).map(form => $(form)) : []
            const params = forms ? forms.map(form => form.serialize()).filter(qs => qs).join('&') : ''
            const canvasId = canvas.attr('id')
            const chartType = canvas.attr('data-chart-type')
            const chartMode = canvas.attr('data-chart-mode') ? canvas.attr('data-chart-mode') : 'vertical'
            const url = canvas.attr('data-source') ? canvas.attr('data-source') : forms ? forms[0].attr('action') : ''
            let chart = null
    
            let msg = null
            app.loading.show()
            
            $.get(url, params)
                .done(res => {
                    if ('error' in res) {
                        msg = res.error
                    } else {
                        canvas.show()
                        charts[canvasId] && charts[canvasId].destroy()
                        try {
                            if (chartMode == 'horizontal') {
                                canvas.parent().css('height', 30 * res.labels.length * res.datasets.length + 80 + 'px')
                            }
                            chart = draw({
                                canvas: canvasId, 
                                labels: res.labels, 
                                datasets: res.datasets, 
                                datalabels: res.datalabels ? res.datalabels : null,
                                outlabels: res.outlabels ? res.outlabels : null,
                                chart_type: chartType, 
                                chart_mode: chartMode
                            })
                        }
                        catch (err) {
                            chart && chart.destroy()
                            msg = err.message
                        }
                        charts[canvasId] = chart
                    }
                })
                .fail(() => msg = 'Ошибка')
                .always(() => app.loading.hide(msg))
        }
    
        const init = (container = $(document)) => {
            container.find('canvas[data-chart-type]').each(function () {
                const canvas = $(this)
                process(canvas)
                if (canvas.attr('data-form')) {
                    canvas.attr('data-form').split(/\s*,\s*/).forEach(function (fid) {
                        const form = $(fid)
                        form.find('.forward').on('change', function () {
                            $(this).trigger('change.before-app-handlers')
                            if ($(this).val() || ($(this).find(":selected").index() >= 0)) {
                                process(canvas);
                            }
                        })
                    })
                }
            })
        }

        $(document).on('process-ajax-container', function (e) {
            init($(e.target))
        })

        init()

        return charts
    }


    const charts = () => {
        draw_form_dependent_charts('.charts_filter_form, .charts-filter-form')
        draw_canvas_dependent_charts()

        return {
            draw: draw,
        }
    }
    

    if (typeof (window.charts) === 'undefined') {
        window.charts = charts()
    }
})(window)
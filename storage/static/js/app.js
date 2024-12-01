/** 
 * @module app 
 */
(function (window) {

    /**
     * Html-код спиннера
     */
    const spinnerHtml = '<div class="spinner-border" role="status"><span class="visually-hidden">Загрузка...</span></div>'


    const uniqId = (() => {
        let i = 0;
        return () => {
            return i++;
        }
    })();

    
    /**
     * Генератор натуральных чисел
     * n = new naturals(10)
     * console.log(n.next())
     */
    const naturals = function (initial = 0) {
        this.i = initial
        this.next = () => this.i++
    }


    /**
     * Таймер
     * 
     * @param {*} time Время на которое устанавливают таймер (секунды)
     * @param {*} updateCallback Вызывается на каждом шаге таймера
     * @param {*} completeCallback Вызывается по истечению таймера
     */
    const timer = function (time, updateCallback=undefined, completeCallback=undefined) {
        var instance = this,
            seconds,
            interval

        this.start = () => {
            clearInterval(interval)
            interval = 0
            seconds = time
            updateCallback && updateCallback(seconds)
            seconds--
            interval = setInterval(() => {
                updateCallback && updateCallback(seconds)
                if (seconds == 0) {
                    completeCallback && completeCallback()
                    instance.stop()
                }
                seconds--
            }, 1000)
          }
        
        this.stop = () => { clearInterval(interval) }
    }


    /**
     * base64 в blob
     * 
     * @param {string} dataURI 
     * @returns {Blob}
     */
    const dataURIToBlob = function(dataURI) {
        const splitDataURI = dataURI.split(',')
        const byteString = splitDataURI[0].indexOf('base64') >= 0 ? atob(splitDataURI[1]) : decodeURI(splitDataURI[1])
        const mimeString = splitDataURI[0].split(':')[1].split(';')[0]
        const ia = new Uint8Array(byteString.length)
        for (let i = 0; i < byteString.length; i++)
            ia[i] = byteString.charCodeAt(i)
        return new Blob([ia], { type: mimeString })
    }


    /**
     * Проверяет, является ли переданный параметр объектом jquery
     * 
     * @param {mixed} obj 
     */
    const isjQueryObj = obj => {
        return (obj && (obj instanceof jQuery || obj.constructor.prototype.jquery))
    }


    const processContainer = c => {
        c.each(function () {
            let cont = $(this)
            cont.find('.ajax-container, .ajax_container').each(window.app.ajaxContainersInitializer)
            cont.trigger('process-ajax-container')
        })
    }


    /**
     * Чистит ошибки прикрепленные к указанному полю формы
     * 
     * @param {*} input Объект поля формы
     */
    const clearInputValidateErrors = input => {
        input.removeClass('is-invalid')
        input.parent().find('.invalid-feedback').each(function () { $(this).remove() })
    }
    
    /**
     * Чистит ошибки прикрепленные к указанному блоку html-кода
     * 
     * @param {*} block Объект jquery
     */
    const clearBlockValidateErrors = block => {
        block.parent().find('.invalid-feedback').each(function () { $(this).remove() })
        block.closest('.border').removeClass('border-danger border-3')
    }


    /**
     * Чистит ошибки прикрепленные к форме, форма указывается объектом
     * 
     * @param {*} form Объект формы
     */
    const clearFormValidateErrors = form => {
        form.find('.is-invalid').each(function () { $(this).removeClass('is-invalid') })
        form.find('.invalid-feedback').each(function () { $(this).remove() })
    }


    /**
     * Прикрепляет к полям указанной формы ошибки с соответствующими ключами
     * 
     * @param {*} form Объект формы
     * @param {*} errors словарь массивов ошибок
     */
    const handleFormErrors = (form, errors) => {
        for (var key in errors) {
            let errorsRow = errors[key]
            let errorsList = []
            for (let i = 0; i < errorsRow.length; i++) {
                errorsList.push('<span class="invalid-feedback d-block"><strong>' + errorsRow[i] + '</strong></span>')
            }
            let input = form.find('[name="' + key + '"]')
            if (input.length > 0) {
                input.on('change input', () => clearInputValidateErrors(input))
                input.addClass('is-invalid')
                input.parent().append($(errorsList.join('')))
            } else {
                let block = form.find('[data-prefix="' + key + '"]')
                if (block.length > 0) {
                    form.on('submit', () => clearBlockValidateErrors(block))
                    block.parent().prepend($(errorsList.join('')))
                    block.closest('.border').addClass('border-danger border-3')
                } else {
                    form.prepend($(errorsList.join('')))
                }
            }
        }

        // Скролл к первой ошибке 
        const firstIF = $('.invalid-feedback').eq(0)
        if (firstIF.closest('.border').hasClass('border-danger border-3')) {
            firstIF.closest('.border').get(0).scrollIntoView()
        } else {
            firstIF.closest('div').get(0).scrollIntoView()
        }
    }


    /**
     * Возвращает из объекта xhr имя файла
     * 
     * @param {*} xhr 
     * @param {*} disp 
     * @returns {string} Имя файла
     */
    const getXHRFilename = (xhr, disp = 'attachment') => {
        let filename = ''
        let disposition = xhr.getResponseHeader('Content-Disposition')
        if (disposition && disposition.indexOf(disp) !== -1) {
            let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
            let matches = filenameRegex.exec(disposition)
            if (matches != null && matches[1]) {
                filename = decodeURIComponent(matches[1].replace(/['"]/g, ''))
            }
        }
        return filename
    }


    /**
     * Показ/Обновление/Сокрытие спинера или сообщений 
     * обозначающих загрузку данных или длительные процессы
     * 
     * @returns {object} Объект содержащий  функции show, update и hide
     */
    const loading = function () {

        let count = 0
        const container = $('<div class="loading__outer"><div class="loading__inner"></div></div>')
        container.hide().appendTo('body')

        const payload = {
            html(msg) {
                if (!/class="spinner-border"/.test(msg)) {
                    msg = '<div class="alert alert-warning shadow">' + msg + '</div>'
                }
                container.find('.loading__inner').html(msg)
            }
        }

        return {
            show(msg = spinnerHtml) {
                payload.html(msg)
                container.show()
                count++
            },

            update(msg) {
                msg && payload.html(msg)
            },

            hide(msg = null) {
                count--
                msg && payload.html(msg)
                setTimeout(() => { (count < 1) && container.hide() }, msg ? 2500 : 0)
            }
        }
    }()


    /**
    * Основные рабочие модальные окна, основная и вспомогательная
    */
    const infoModals = function () {
        // Основная модалка
        const mainModal = $(`
           <div class="modal fade" id="main_modal" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1"
               aria-labelledby="staticBackdropLabel" aria-hidden="true" data-bs-focus="false">
               <div class="modal-dialog modal-dialog-centered">
                   <div class="modal-content shadow-lg overflow-hidden">
                       <div class="modal-header ps-4 pe-4">
                           <h4 class="modal-title text-expressive w-75 lh-sm"></h4>
                           <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                       </div>
                       <div id="main_modal_body" class="modal-body ps-4 pe-4"></div>
                       <div class="modal-footer"></div>
                   </div>
               </div>
           </div>
           `)
        // Вспомогательная модалка
        const secondaryModal = $(`
           <div class="modal fade" id="secondary_modal" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1"
               aria-labelledby="staticBackdropLabel" aria-hidden="true" data-bs-focus="false">
               <div class="modal-dialog modal-dialog-centered">
                   <div class="modal-content shadow-lg overflow-hidden">
                       <div class="modal-header ps-4 pe-4">
                           <h4 class="modal-title text-expressive w-75 lh-sm"></h4>
                           <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                       </div>
                       <div id="secondary_modal_body" class="modal-body ps-4 pe-4"></div>
                       <div class="modal-footer"></div>
                   </div>
               </div>
           </div>
           `)
        // Шаблон для создания дополнительных модалок, в случае, если не хватило первых двух.
        const blankModalTemplate = `
            <div class="modal fade" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1"
               aria-labelledby="staticBackdropLabel" aria-hidden="true" data-bs-focus="false">
               <div class="modal-dialog modal-dialog-centered">
                   <div class="modal-content shadow-lg overflow-hidden">
                       <div class="modal-header ps-4 pe-4">
                           <h4 class="modal-title text-expressive w-75 lh-sm"></h4>
                           <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                       </div>
                       <div class="modal-body ps-4 pe-4"></div>
                       <div class="modal-footer"></div>
                   </div>
               </div>
           </div>
            `

        const setEventsHandlers = function (m) {
            m.on('hide.bs.modal', function (e) {
                if (m.attr('data-modal-close-handler')) {
                    eval(m.attr('data-modal-close-handler'))(e)
                }
            })
        }

        const modals = [mainModal, secondaryModal]

        const getAllowedModal = () => {
            for (let i = 0; i < modals.length; i++) {
                let m = modals[i]
                if (!m.hasClass('in') && !m.hasClass('show')) {
                    return m
                }
            }
            m = $(blankModalTemplate)
            initModal(m)
            modals.push(m)
            return modals[modals.length - 1]
        }

        const getOpenedModals = () => {
            const tmp = []
            for (let i = 0; i < modals.length; i++) {
                let m = modals[i]
                if (m.hasClass('in') || m.hasClass('show')) {
                    tmp.push(m)
                }
            }
            return tmp
        }

        const resetModal = modal => {
            modal.find('.modal-dialog').removeClass(['modal-sm', 'modal-md', 'modal-xl', 'modal-lg', 'modal-fullscreen'])
            modal.removeAttr('data-target')
                .removeAttr('data-modal-close-href')
                .removeAttr('data-modal-close-target')
                .removeAttr('data-modal-close-handler')
                .removeAttr('data-notify-close-href')
                .removeAttr('data-notify-close-target')
                .removeAttr('data-modal-sticked')
                .removeAttr('data-form-no-reset')
                .removeAttr('data-form-submit-confirm')
                .removeAttr('data-form-submit-confirm-title')
                .removeAttr('data-form-submit-confirm-body')
                .removeAttr('data-form-submit-confirm-callback')
                .removeAttr('data-form-submit-confirm-size')
            modal.find('.modal-dialog').removeClass('modal-dialog-scrollable')
            modal.find('.modal-body').html('')
            modal.find('.modal-footer').html('')
        }

        const initModal = modal => {
            resetModal(modal)
            setEventsHandlers(modal)
            modal.appendTo('body')
            modal.on('click', '[data-bs-dismiss="modal"]', function (e) {
                if (modal.attr('data-modal-close-href')) {
                    e.preventDefault()
                    let msg = null
                    loading.show()
                    $.get({ url: modal.attr('data-modal-close-href'), cache: false })
                        .done(res => {
                            if (typeof res === 'object') {
                                if ('success' in res) {
                                    if ((res.success == false) && ('error' in res)) notify.error(res.error)
                                    if ((res.success == true) && ('message' in res)) notify.info(res.message)
                                }
                            } else if (modal.attr('data-modal-close-target')) {
                                $(modal.attr('data-modal-close-target')).html(res)
                                processContainer($(modal.attr('data-modal-close-target')))
                            }
                        })
                        .fail(() => msg = 'Ошибка')
                        .always(() => {
                            loading.hide(msg)
                            resetModal(modal)
                        })
                } else {
                    resetModal(modal)
                }
            })
        }

        const getFormData = form => {
            let formData = new FormData(form.get(0))
            try {
                return eval(form.attr('data-formdata-processor'))(formData)
            } catch (err) {
                return formData
            }
        }

        const handleClickToShow = (link, m) => {
            resetModal(m)
            const url = link.attr('data-href') ? link.attr('data-href') : link.attr('href')
            
            m.attr('data-target', link.attr('data-target'))
            m.attr('data-modal-close-href', link.attr('data-modal-close-href'))
            m.attr('data-modal-close-target', link.attr('data-modal-close-target'))
            m.attr('data-modal-close-handler', link.attr('data-modal-close-handler'))
            m.attr('data-notify-close-href', link.attr('data-notify-close-href'))
            m.attr('data-notify-close-target', link.attr('data-notify-close-target'))
            m.attr('data-modal-sticked', link.attr('data-modal-sticked'))
            m.attr('data-form-no-reset', link.attr('data-form-no-reset'))
            m.attr('data-form-submit-confirm', link.attr('data-form-submit-confirm'))
            m.attr('data-form-submit-confirm-title', link.attr('data-form-submit-confirm-title'))
            m.attr('data-form-submit-confirm-body', link.attr('data-form-submit-confirm-body'))
            m.attr('data-form-submit-confirm-callback', link.attr('data-form-submit-confirm-callback'))
            m.attr('data-form-submit-confirm-size', link.attr('data-form-submit-confirm-size'))

            if (link.attr('data-modal-scrollable')) {
                m.find('.modal-dialog').addClass('modal-dialog-scrollable')
            }

            let msg = null
            loading.show()
            $.ajax({ 
                method: 'GET',
                url: url, 
                processData: false,
                contentType: false,
                cache: false
            })
                .done(res => {
                    if (typeof res === 'object') {
                        if ('success' in res) {
                            if ((res.success == false) && ('error' in res)) notify.error(res.error)
                            if ((res.success == true) && ('message' in res)) notify.info(res.message)
                        }
                    } else {
                        if (link.attr('data-modal-size')) {
                            m.find('.modal-dialog').addClass(link.attr('data-modal-size'))
                        } else {
                            m.find('.modal-dialog').addClass('modal-lg')
                        }
                        m.find('.modal-title').html(link.attr('data-modal-title') || link.attr('title') || link.text())
                        m.find('.modal-body').html(res)
                        m.modal('show')
                        processContainer(m.find('.modal-body'))
                    }
                })
                .fail(() => msg = 'Ошибка')
                .always(() => loading.hide(msg))
            
            if (link.attr('data-modal-close-handler')) {
                m.modal().on('hide.bs.modal', function () {

                })
            }
        }

        $(document).on('click', '.modal_link, .modal-link', function (e) {
            e.preventDefault()
            handleClickToShow($(this), getAllowedModal())
        })

        $(document).on('submit', '.modal-content form:not(.ajax_form, .ajax-form, [target="_blank"])', function (e) {
        //m.find('.modal-content form:not(.ajax_form, .ajax-form)').on('submit', function (e) {
            const submittedBtn = $(this).find("input[type=submit]:focus" )
            e.preventDefault()
            const form = $(this)
            const m = form.closest('.modal')

            const submit = function() {
                return new Promise(function(resolve, reject) {
                    // Из данных форм указанных в атрибуте "data-grab-form", текущая формирует QueryString для своего обработчика
                    let grabForms = form.attr('data-grab-form')
                    if (grabForms) {
                        let qs = ''
                        let grabFormsList = grabForms.split(/\s*,\s*/)
                        for (let i = 0; i < grabFormsList.length; i++) {
                            let f = $(grabFormsList[i])
                            if (f) {
                                qs = qs + '&' + (new URLSearchParams(new FormData($(f).get(0)))).toString()
                            }
                        }
                        if (/[?]/.test(form.attr('action'))) {
                            form.attr('action', form.attr('action') + '&' + qs)
                        } else {
                            form.attr('action', form.attr('action') + '?' + qs)
                        }
                    }

                    let context = m.attr('data-target') || $(this).attr('data-target')
                    loading.show()
                    clearFormValidateErrors(form)

                    formdata = getFormData(form)
                    try {
                        if (submittedBtn.length > 0) {
                            formdata.set(submittedBtn.attr('name'), submittedBtn.attr('value'))
                        }
                    } catch (err) {
                        console.log(err)
                    }

                    $.ajax({
                        method: form.attr('method'),
                        url: form.attr('action'),
                        data: formdata,
                        processData: false,
                        contentType: false,
                        cache: false,
                        xhr: function () {
                            let xhr = new XMLHttpRequest()
                            xhr.onreadystatechange = function () {
                                if (xhr.readyState == 2) {
                                    if (xhr.status == 200) {
                                        if ((new RegExp('filename')).test(xhr.getResponseHeader("content-disposition"))) {
                                            xhr.responseType = 'blob'
                                        }
                                    }
                                }
                            }
                            return xhr
                        }
                    })
                        .done((res, status, xhr) => {
                            if (res instanceof Blob) {
                                let lnk = document.createElement("a")
                                lnk.href = URL.createObjectURL(res)
                                lnk.download = getXHRFilename(xhr)
                                lnk.click()
                                m.modal('hide')
                            } else if (typeof res === 'object') {
                                if (('success' in res)) {
                                    let notifyCloseCallback = undefined
                                    if ('redirect_url' in res) notifyCloseCallback = () => window.location.href = res.redirect_url
                                    
                                    if (res.success == false) {
                                        if ('errors' in res) handleFormErrors(form, res.errors)
                                        if ('error' in res) notify.error(res.error, notifyCloseCallback, size='modal-md')
                                        reject(false)
                                    } else {
                                        m.modal('hide')
                                        if ((notifyCloseCallback == undefined) && m.attr('data-notify-close-href')) {
                                            notifyCloseCallback = (nm) => {
                                                if (('close_opened_modals' in res) && res.close_opened_modals == true) { 
                                                    infoModals.getOpenedModals().forEach(function(m) {
                                                        !m.attr('data-modal-sticked') && m.modal('hide')
                                                    })
                                                }
                                                let msg = null
                                                loading.show()
                                                $.get({ url: m.attr('data-notify-close-href'), cache: false })
                                                    .done(res => {
                                                        if (typeof res === 'object') {
                                                            if ('success' in res) {
                                                                if ((res.success == false) && ('error' in res)) msg = res.error
                                                                if ((res.success == true) && ('message' in res)) msg = res.message
                                                            }
                                                        } else if (m.attr('data-notify-close-target')) {
                                                            $(m.attr('data-notify-close-target')).html(res)
                                                            processContainer($(m.attr('data-notify-close-target')))
                                                        }
                                                    })
                                                    .fail(() => msg = 'Ошибка')
                                                    .always(() => {
                                                        loading.hide(msg)
                                                        nm.modal('hide')
                                                    })
                                            }
                                        }
                                        notify.info(res.message, notifyCloseCallback)
                                    }

                                } else if ('redirect_url' in res) {
                                    window.location.href = res.redirect_url

                                } else if ('open_in_modal' in res) {
                                    const tmpLink = $('<a class="modal-link"></a>')
                                    for (var key of Object.keys(res.open_in_modal)) {
                                        tmpLink.attr(key, res.open_in_modal[key])
                                    }
                                    handleClickToShow(tmpLink, getAllowedModal())
                                    if ('close_prev_modals' in res) { 
                                        infoModals.getOpenedModals().forEach(function(m) {
                                            !m.attr('data-modal-sticked') && m.modal('hide')
                                        })
                                    }
                                }
                                
                            } else {
                                if (context) { 
                                    $(context).html(res)
                                    processContainer($(context))
                                }
                                if (!m.attr('data-modal-sticked') && !form.attr('data-modal-sticked')) { m.modal('hide') }
                                if (!m.attr('data-form-no-reset') && !form.attr('data-form-no-reset')) {
                                    form.trigger('reset')
                                }
                            }
                            resolve(true)
                        })
                        .fail(() => {
                            loading.hide('Ошибка')
                            m.modal('hide')
                            //notify.error('Ошибка')
                            reject(false)
                        })
                        .always(() => loading.hide())
    
                })
            }

            if (m.attr('data-form-submit-confirm')) {
                let scmBody = m.attr('data-form-submit-confirm-body')
                const scmBodyCallback = m.attr('data-form-submit-confirm-callback')
                if (scmBodyCallback != undefined) {
                    scmBody = eval(scmBodyCallback)(m)
                }
                submitConfirmModal.show(
                    m.attr('data-form-submit-confirm-title'), scmBody, m.attr('data-form-submit-confirm-size'))
                submitConfirmModal.process()
                    .then(result => submit())
                    .then(() => submitConfirmModal.hide())
                    .catch(err => submitConfirmModal.hide())
            } else {
                submit().catch(err => {})
            }
        })
        
        modals.forEach(modal => initModal(modal))

        return{
            'getOpenedModals': getOpenedModals,
            'getAllowedModal': getAllowedModal
        }
    }()


    /**
     * Диалоговые модалки подтверждения
     */
    const dialogModals = function () {

        const confirmModal = $(`
            <div class="modal fade" id="confirm_dialog_modal" role="dialog" data-bs-keyboard="true" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-expressive">Подтверждение</h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4" data-default-body="Вы уверены?"></div>
                        <div class="modal-footer">
                            <a class="btn btn-primary btn-ok">Подтверждаю</a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        </div>
                    </div>
                </div>
            </div>
            `)

        const deleteModal = $(`
            <div class="modal fade" id="delete_dialog_modal" role="dialog" data-bs-keyboard="true" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-expressive">Удаление</h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4" data-default-body="Вы уверены что хотите удалить?"></div>
                        <div class="modal-footer">
                            <a class="btn btn-danger btn-ok">Удалить</a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        </div>
                    </div>
                </div>
            </div>
            `)

        const resetModal = modal => {
            const modalBody = modal.find('.modal-body')
            const modalMainBtn = modal.find('.btn-ok')
            modalMainBtn
                .removeAttr('data-href')
                .removeAttr('href')
                .removeAttr('data-target')
                .removeAttr('data-clean')
                .removeAttr('data-notify-close-href')
                .removeAttr('data-notify-close-target')
                .removeAttr('target')
            modalBody.html(modalBody.attr('data-default-body'))
        }

        const handleClickToShow = (a, modal) => {
            const modalBody = modal.find('.modal-body')
            const modalMainBtn = modal.find('.btn-ok')
            resetModal(modal)
            if (a.attr('data-no-ajax')) {
                modalMainBtn.attr('href', a.attr('data-href') || a.attr('href'))
                if (a.attr('target')) modalMainBtn.attr('target', a.attr('target'))
            } else {
                modalMainBtn.attr('data-href', a.attr('data-href'))
                modalMainBtn.attr('data-target', a.attr('data-target'))
                modalMainBtn.attr('data-clean', a.attr('data-clean'))
                modalMainBtn.attr('data-notify-close-href', a.attr('data-notify-close-href'))
                modalMainBtn.attr('data-notify-close-target', a.attr('data-notify-close-target'))
            }
            if (a.attr('data-modal-body')) {
                modalBody.html(a.attr('data-modal-body'))
            }
            modal.modal('show')
        }

        $(document).on('click', '.dialog_confirm, .dialog-confirm', function (e) {
            e.preventDefault()
            handleClickToShow($(this), confirmModal)
        })

        $(document).on('click', '.dialog_delete, .dialog-delete', function (e) {
            e.preventDefault()
            handleClickToShow($(this), deleteModal)
        })

            ;[confirmModal, deleteModal].forEach(modal => {
                resetModal(modal)
                modal.appendTo('body')
                modal.on('click', '.btn-ok', function (e) {
                    const modalMainBtn = $(this)
                    if (modalMainBtn.attr('data-href')) {
                        e.preventDefault()
                        let msg = null
                        loading.show()
                        $.get({ url: modalMainBtn.attr('data-href'), cache: false })
                            .done(res => {
                                if ((typeof res === 'object') && ('success' in res)) {
                                    let notifyCloseCallback = undefined
                                    if ('redirect_url' in res) notifyCloseCallback = () => window.location.href = res.redirect_url

                                    if ((notifyCloseCallback == undefined) && modalMainBtn.attr('data-notify-close-href')) {
                                        notifyCloseCallback = nm => {
                                            if (('close_opened_modals' in res) && res.close_opened_modals == true) { 
                                                infoModals.getOpenedModals().forEach(function(m) {
                                                    !m.attr('data-modal-sticked') && m.modal('hide')
                                                })
                                            }
                                            let msg = null
                                            loading.show()
                                            $.get({ url: modalMainBtn.attr('data-notify-close-href'), cache: false })
                                                .done(r => {
                                                    if (modalMainBtn.attr('data-notify-close-target')) {
                                                        $(modalMainBtn.attr('data-notify-close-target')).html(r)
                                                        processContainer($(modalMainBtn.attr('data-notify-close-target')))
                                                    }
                                                })
                                                .fail(() => msg = 'Ошибка')
                                                .always(() => loading.hide(msg))
                                        }
                                    }

                                    if ((res.success == false) && ('error' in res)) notify.error(res.error, notifyCloseCallback)
                                    if ((res.success == true) && ('message' in res)) notify.info(res.message, notifyCloseCallback)

                                } else if (modalMainBtn.attr('data-target')) {
                                    if (modalMainBtn.attr('data-clean')) {
                                        $.each(modalMainBtn.attr('data-clean').split(/\s*,\s*/), function (i, elm) {
                                            $(elm).each(function () {
                                                $(this).html('')
                                            })
                                        })
                                    }
                                    $(modalMainBtn.attr('data-target')).html(res)
                                    processContainer($(modalMainBtn.attr('data-target')))
                                }
                            })
                            .fail(() => msg = 'Ошибка')
                            .always(() => {
                                loading.hide(msg)
                                modalMainBtn.closest('.modal').modal('hide')
                            })
                    }
                    if (modalMainBtn.attr('target')) {
                        modalMainBtn.closest('.modal').modal('hide')
                    }
                })
            })
    }()


    /**
     * Показ в модальных окнах уведомлений информативного характера или ошибки
     * 
     * @returns {object} Объект содержащий функции info и error
     */
    const notify = function () {

        const infoModal = $(`
            <div class="modal fade" id="notify_modal" role="dialog" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-expressive">Уведомление</h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4"></div>
                        <div class="modal-footer d-flex justify-content-center">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Закрыть</button>
                        </div>
                    </div>
                </div>
            </div>
            `)

        const errorModal = $(`
            <div class="modal fade" id="error_modal" role="dialog" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-danger text-expressive">Ошибка</h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4"></div>
                        <div class="modal-footer d-flex justify-content-center">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Закрыть</button>
                        </div>
                    </div>
                </div>
            </div>
            `)

        /**
         * Показ модалки
         * 
         * @param {*} modal Объект модального окна
         * @param {*} msg Сообщение
         * @param {*} dismissCallback Функция обратного вызова, выполняется разово, при закрытии текущего окна
         * @param {*} size Bootstrap класс размера модалки
         */
        const process = (modal, msg, dismissCallback, size) => {
            modal.find('.modal-dialog')
                .removeClass(['modal-sm', 'modal-md', 'modal-xl', 'modal-lg', 'modal-fullscreen'])
                .addClass(size)

            modal.find('.modal-body').html(msg)
            modal.modal('show')
            if (dismissCallback != undefined) {
                modal.on('click.callback', '[data-bs-dismiss="modal"]', () => {
                    dismissCallback(modal)
                    modal.off('click.callback')
                })
            }
        }

        infoModal.appendTo('body')
        errorModal.appendTo('body')

        return {
            info(msg, dismissCallback = undefined, size=null) {
                size = size ? size : msg.length < 200 ? 'modal-md' : 'modal-lg'
                process(infoModal, msg, dismissCallback, size)
            },

            error(msg, dismissCallback = undefined, size=null) {
                size = size ? size : msg.length < 200 ? 'modal-md' : 'modal-lg'
                process(errorModal, msg, dismissCallback, size)
            }
        }
    }()


    /**
     * Модалка выбора, ввода параметров,
     * подразумевается, что в качестве контента будут выступать 
     * различные формы с полями - для выбора параметров
     */
    const paramsModal = function () {

        const modal = $(`
            <div class="modal fade" role="dialog" data-bs-backdrop="static" data-bs-keyboard="true" tabindex="-1"
               aria-labelledby="staticBackdropLabel" aria-hidden="true" data-bs-focus="false">

                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-expressive">Параметры</h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4"></div>
                        <div class="modal-footer">
                            <a class="btn btn-primary btn-ok">Готово</a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        </div>
                    </div>
                </div>
            </div>
        `)

        /**
         * Показ модалки
         * 
         * @param {*} title Заголовок модального окна
         * @param {*} data Контент
         * @param {*} size размер модалки
         * @param {*} dismissCallback Функция обратного вызова, выполняется разово, при закрытии текущего окна
         */
        const show = (title, data, size='modal-md', dismissCallback) => {
            modal.find('.modal-dialog').addClass(size)
            modal.find('.modal-title:first').html(title)
            modal.find('.modal-body:first').html(data)
            modal.modal('show')
            if (dismissCallback != undefined) {
                modal.on('click.callback', '[data-bs-dismiss="modal"]', () => {
                    dismissCallback(modal)
                    modal.off('click.callback')
                })
            }
        }

        /**
         * После нажатия кнопки "Готово" возвращает
         * объект FormData с данными формы в модалке
         * 
         * @returns Promise
         */
        const process = function () {
            return new Promise((resolve, reject) => {
                modal.find('.btn-ok').on('click', function (e) {
                    e.preventDefault()
                    modal.off('hidden.bs.modal', () => reject(false))
                    resolve(new FormData(modal.find('.modal-body:first').find('form:first').get(0)))
                })
                modal.on('hidden.bs.modal', () => reject(false))
              })
        }

        const resetModal = modal => {
            modal.find('.modal-dialog').removeClass(['modal-sm', 'modal-md', 'modal-xl', 'modal-lg', 'modal-fullscreen'])
            modal.find('.modal-title:first').html('Параметры')
            modal.find('.modal-body:first').html('')
        }

        modal.on('hidden.bs.modal' , () => resetModal(modal))
        modal.appendTo('body')

        return {
            show: show,
            hide: () => modal.modal('hide'),
            process: process
        }

    }()


    /**
     * Диалоговое окно для подтверждения отправки формы
     */
    const submitConfirmModal = function () {
        // Диалоговое окно для подтверждения отправки формы
        const modal = $(`
            <div class="modal fade" role="dialog" data-bs-keyboard="true" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg overflow-hidden">
                        <div class="modal-header ps-4 pe-4">
                            <h4 class="modal-title text-expressive lh-1"></h4>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body ps-4 pe-4"></div>
                        <div class="modal-footer">
                            <a class="btn btn-primary btn-ok">ДА</a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">НЕТ</button>
                        </div>
                    </div>
                </div>
            </div>
            `)

        /**
         * Показ модалки
         * 
         * @param {*} title Заголовок модального окна
         * @param {*} data Контент
         * @param {*} size размер модалки
         * @param {*} dismissCallback Функция обратного вызова, выполняется разово, при закрытии текущего окна
         */
        const show = (title='Подтверждение', data='Вы уверены?', size='modal-md', dismissCallback) => {
            modal.find('.modal-dialog').addClass(size)
            modal.find('.modal-title:first').html(title)
            modal.find('.modal-body:first').html(data)
            modal.modal('show')
            if (dismissCallback != undefined) {
                modal.on('click.callback', '[data-bs-dismiss="modal"]', () => {
                    dismissCallback(modal)
                    modal.off('click.callback')
                })
            }
        }

        /**
         * После нажатия кнопки "Да" возвращает true
         * 
         * @returns Promise
         */
        const process = function () {
            return new Promise((resolve, reject) => {
                modal.find('.btn-ok').on('click', function (e) {
                    e.preventDefault()
                    modal.off('hidden.bs.modal', () => reject(false))
                    resolve(true)
                })
                modal.on('hidden.bs.modal', () => reject(false))
              })
        }

        const resetModal = modal => {
            modal.find('.modal-dialog').removeClass(['modal-sm', 'modal-md', 'modal-xl', 'modal-lg', 'modal-fullscreen'])
            modal.find('.modal-title:first').html('Параметры')
            modal.find('.modal-body:first').html('')
        }

        modal.on('hidden.bs.modal' , () => resetModal(modal))
        modal.appendTo('body')

        return {
            show: show,
            hide: () => modal.modal('hide'),
            process: process
        }
    }()


    /**
     * Ajax отправка указанной формы, при этом она может забрать и данные других, указанных параметром "data-form" форм.
     * Ответом на отправленные данные могут быть текстовые данные, json-объект ошибок, файл данных.
     * 
     * @param {string|object} f селектор или jquery-объект формы
     * @param {string} c Место, куда записывается результат отправки формы
     */
    const sendAjaxForm = (f, c = null) => {
        const form = isjQueryObj(f) ? f : $(f)
        const context = c ? c : form.attr('data-target')

        let msg = null
        loading.show()
        clearFormValidateErrors(form)

        const prepareData = form => {
            const forms = form.attr('data-form') ? form.attr('data-form').split(/\s*,\s*/).map(frm => $(frm)) : []
            if (form.attr('method').toUpperCase() == 'GET') {
                forms.push(form)
                return forms.map(form => form.serialize()).filter(qs => qs).join('&')
            } else {
                let formData = new FormData(form.get(0))
                for (var frm in forms) {
                    let frmData = new FormData(frm.get(0))
                    for (var pair of frmData.entries()) {
                        formData.append(pair[0], pair[1]);
                    }
                }
                return formData
            }
        }

        $.ajax({
            method: form.attr('method'),
            url: form.attr('action'),
            data: prepareData(form),
            processData: false,
            contentType: false,
            cache: false,
            xhr: function () {
                let xhr = new XMLHttpRequest()
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == 2) {
                        if (xhr.status == 200) {
                            if ((new RegExp('filename')).test(xhr.getResponseHeader("content-disposition"))) {
                                xhr.responseType = 'blob'
                            }
                        }
                    }
                }
                return xhr
            }
        })
            .done((res, status, xhr) => {
                if (res instanceof Blob) {
                    let lnk = document.createElement("a")
                    lnk.href = URL.createObjectURL(res)
                    lnk.download = getXHRFilename(xhr)
                    lnk.click()

                } else if ((typeof res === 'object') && ('success' in res)) {
                    let notifyCloseCallback = undefined
                    if ('redirect_url' in res) notifyCloseCallback = () => window.location.href = res.redirect_url
                    if ((res.success == false) && ('errors' in res))  handleFormErrors(form, res.errors)
                    if ((res.success == false) && ('error' in res)) notify.error(res.error, notifyCloseCallback)
                    if ((res.success == true) && ('message' in res)) notify.info(res.message, notifyCloseCallback)

                } else if ((typeof res === 'object') && ('redirect_url' in res)) {
                    window.location.href = res.redirect_url

                } else {
                    if (context) {
                        $(context).html(res)
                        processContainer($(context))
                    }
                    form.attr('data-reset') && form.trigger('reset')
                }
            })

            .fail(() => msg = 'Ошибка')
            .always(() => loading.hide(msg))
    }


    const app = () => {

        // При клике на элементе с классом ".form_based_link"
        // формирует для него href-атрибут на основе обработчика и данных указанных data-атрибутом форм,
        // при этом в data-extra-params можно указать дополнительные параметры в формате QueryString
        $(document).on('mousedown', '.form_based_link, .form-based-link', function () {
            const a = $(this)
            const forms = a.attr('data-form') ? a.attr('data-form').split(/\s*,\s*/).map(form => $(form)) : []
            const params = forms ? forms.map(form => form.serialize()).filter(qs => qs).join('&') : ''
            const extraParams = a.attr('data-extra-params') ? a.attr('data-extra-params') : ''
            let action = forms[0].attr('action')
            if (!/\?/i.test(action)) { action = action + '?' }
            if (a.attr('data-href') !== undefined) {
                a.attr('data-href', action + '&' + params + '&' + extraParams)
            } else {
                a.attr('href', action + '&' + params + '&' + extraParams)
            }
        })


        // При клике на элементе с классом ".form_grab_link"
        // добавляет к его href-атрибуту данные из указанных data-атрибутом форм,
        // при этом в data-extra-params можно указать дополнительные параметры в формате QueryString
        $(document).on('mousedown', '.form_grab_link, .form-grab-link', function () {
            const a = $(this)
            const forms = a.attr('data-form') ? a.attr('data-form').split(/\s*,\s*/).map(form => $(form)) : []
            const params = forms ? forms.map(form => form.serialize()).filter(qs => qs).join('&') : ''
            const extraParams = a.attr('data-extra-params') ? a.attr('data-extra-params') : ''
            if (a.attr('data-href')) {
                a.attr('data-href', a.attr('data-href').split('?')[0] + '?' + params + '&' + extraParams)
            } else {
                a.attr('href', a.attr('href').split('?')[0] + '?' + params + '&' + extraParams)
            }
        })


        // При клике на элементе с классом ".ajax_link" происходит ajax-запрос по ссылке из
        // атрибутов href или data-href, результат записывается в элемент указанный в атрибуте "data-target"
        $(document).on('click', '.ajax_link, .ajax-link', function (e) {
            if (!$(e.target).closest('.selectable_list__item__actions').length) {
                e.preventDefault()
                const link = $(this)
                const url = link.attr('data-href') ? link.attr('data-href') : link.attr('href')
                let msg = null
                loading.show()
                $.ajax(url)
                    .done(res => {
                        if ((typeof res === 'object') && ('success' in res)) {
                            let notifyCloseCallback = undefined
                            if ('redirect_url' in res) notifyCloseCallback = () => window.location.href = res.redirect_url
                            if ((res.success == false) && ('error' in res)) notify.error(res.error, notifyCloseCallback)
                            if ((res.success == true) && ('message' in res)) notify.info(res.message, notifyCloseCallback) 
                        } else {
                            $(link.attr('data-target')).html(res)
                            processContainer($(link.attr('data-target')))
                        }
                    })
                    .fail(() => msg = 'Ошибка')
                    .always(() => loading.hide())
            }
        })


        // Автоматическая подгрузка данных в элементы с классом ".ajax_container".
        // Источник данных укзывается в атрибуте data-source или формируется на базе первой формы, в указанных атрибутом data-form,
        // при этом в data-extra-params можно указать дополнительные параметры в формате QueryString
        // В атрибуте "data-refresh-time" можно указать период перезагрузки данных в контейнере
        const processAjaxContainers = (c, forms, hideSpinner=true) => {
            const url = c.attr('data-source') ? c.attr('data-source') : forms.length ? forms[0].attr('action') : undefined
            if (!url) return
            const params = forms ? forms.map(form => form.serialize()).filter(qs => qs).join('&') : ''
            const extraParams = c.attr('data-extra-params') ? c.attr('data-extra-params') : ''
            if (!hideSpinner) {
                c.html('<div class="d-flex justify-content-center align-items-center">' + spinnerHtml + '</div>')
            }
            $.get(url, extraParams ? [params, extraParams].join('&') : params)
                .done(res => {
                    c.html(res)
                    processContainer(c)
                })
        }
        
        const ajaxContainersInitializer = function () {
            const c = $(this)
            let rt = c.attr('data-refresh-time')
            const forms = c.attr('data-form') ? c.attr('data-form').split(/\s*,\s*/).map(form => $(form)) : []

            forms.forEach(function (form) {
                form.find('.forward').on('change', function () {
                    $(this).trigger('change.before-app-handlers')
                    if (
                        $(this).val() 
                        || ($(this).find(":selected").index() >= 0)
                        || ($(this).find("input:checked").index() >= 0)
                    ) {
                        processAjaxContainers(c, forms, Boolean(c.attr('data-hide-spinner')))
                    }
                })
            })
            processAjaxContainers(c, forms, Boolean(c.attr('data-hide-spinner')))
            if (rt) {
                if (rt < 5000) { rt = 5000 }
                setInterval(processAjaxContainers, rt, ...[c, forms])
            }
        }

        $('.ajax-container, .ajax_container').each(ajaxContainersInitializer)


        // Внутри элементов с атрибутом "data-selector" формирует внутристраничное меню с ссылками на 
        // элементы указанные селектором в "data-selector"
        ;(function () {
            const process = container => {
                $(container).find('[data-selector]').each(function () {
                    const c = $(this)
                    const selector = c.attr('data-selector')
                    selector && $(selector).each(function () {
                        const target = $(this)
                        $('<li class="my-1"><a class="text-link" href="" role="button">' + target.html() + '</a></li>')
                            .on('click', function () {
                                $('html, body').stop().animate({ scrollTop: target.offset().top }, 300)
                                return false
                            })
                            .appendTo(c)
                    })
                })
            }
            process(document)
            $(document).on('process-ajax-container', function (e) {
                process(e.target)
            })
        })()


        // При отправке форм с классом ".ajax_form", отправка, собственно, происходит по ajax.
        // Результат отправки записывается в элемент указанный в атрибуте "data-target" формы.
        // Если определен атрибут "data-reset" формы, то после получения результата отправки формы, она чистится.
        // Также, если данные формы не проходят валидацию, соответствующие ошибки показываются около соответствующих полей.
        // При некоторых, не касающихся данных, ошибках, оные могут показыватся в модальном окне информирования об ошибке.
        $(document).on('submit', '.ajax_form, .ajax-form', function (e) {
            e.preventDefault()
            sendAjaxForm(this)
        })


        // Для форм с классом ".data_filter_form" поддерживаются все то же самое что и для форм с классом ".ajax_form",
        // вся функциональность отрабатывает единоразово, автоматической отправкой формы, если у формы указан класс ".auto_submit_once"
        // и еще, при каждом изменении данных в поле с классом ".submit_on_change"
        ;(function () {
            const init = container => {
                $(container).find('.data_filter_form, .data-filter-form').each(function () {
                    const form = $(this)
                    if (form.hasClass('auto_submit_once')) {
                        sendAjaxForm(form)
                    }
                    form.find('.submit_on_change').on('change', function () {
                        $(this).trigger('change.before-app-handlers')
                        if ($(this).val() || ($(this).find(":selected").index() >= 0)) {
                            sendAjaxForm(form)
                        }
                    })
                })
            }

            init(document)
            $(document).on('process-ajax-container', function (e) {
                init(e.target)
            })
        })()


        // Группа элементов (.selectable_list, .selectable_list__item, .selectable_list__item--active)
        // При клике на элементе списка - он выделяется соответственно имеющимся стилям
        // Если у элемента указан атрибут data-click="true", то на нем будет автоматически произведен клик
        ;(function () {
            $(document).on('click', '.selectable_list__item', function (e) {
                if (!$(e.target).closest('.selectable_list__item__actions').length) {
                    const item = $(this)
                    item.closest('.selectable_list').find('.selectable_list__item').each(function () {
                        $(this).removeClass('selectable_list__item--active')
                    })
                    item.addClass('selectable_list__item--active')
                }
            })
        })()

        
        // Если у элемента указан атрибут data-clean, то при клике на нем, будут очишены элемены,
        // идентификаторы которых указаны данным отрибутом.
        // Идентификаторы указываются через запятую
        ;(function () {
            $(document).on('click', '[data-clean]', function (e) {
                if (!$(e.target).closest('.selectable_list__item__actions').length) {
                    $(this).attr('data-clean').split(/\s*,\s*/).map(id => $(id).html(''))
                }
            })
        })()


        // Если у элемента указан атрибут data-click="true", то на нем будет автоматически произведен клик
        ;(function () {
            const process = container => {
                $(container).find('[data-click=true]').each(function () {
                    $(this).click()
                })
            }
            process(document)
            $(document).on('process-ajax-container', function (e) {
                process(e.target)
            })
        })()


        // Подключение placeholders для полей дат
        ;(function () {
            const init = container => {
                $(container).find('input[type="date"], input[type="datetime"], input[type="datetime-local"], input[type="month"], input[type="time"], input[type="week"]').each(function () {
                    const el = $(this)
                    if (!el.attr('placeholder')) return
                    const type = el.attr('type')
                    if (el.val() == '') el.attr('type', 'text')
                    el.focus(() => {
                        el.attr('type', type)
                        el.click()
                    })
                    el.blur(() => {
                        if (el.val() == '') el.attr('type', 'text')
                    })
                })
            }

            init(document)
            $(document).on('process-ajax-container', function (e) {
                init(e.target)
            })
        })()


        // Подгрузка дополнительных полей или данных в формах.
        // В пределах одной формы, в контейнер с атрибутами data-forward и data-source, 
        // при изменении значения в полях формы указанных их серекторами в data-forward 
        // в сам контейнер грузятся данные из ссылки data-source, параметром передается значения этих самых полей.
        $(document).on('change', 'input, select, textarea', function () {
            $(this).trigger('change.before-app-handlers')
            const forward = $(this)
            const form = forward.closest('form')

            form.find('[data-forward]').each(function () {
                var abort = true
                var wait = false
                const c = $(this)

                const cForwards = c.attr('data-forward') ? 
                    c.attr('data-forward').split(/\s*,\s*/).map(fwd => form.find(fwd + ':first')) : []

                for (key in cForwards) {
                    if (forward.is(cForwards[key])) {
                        abort = false
                        if (!forward.val()) c.html('')
                    } 
                    if (!cForwards[key].val()) wait = true
                }

                if (!abort && !wait) {
                    data = {}
                    for (key in cForwards) {
                        data[cForwards[key].attr('name')] = cForwards[key].val()
                    }

                    if (cForwards.length == 1) {
                        data[cForwards[key].attr('name')] = cForwards[key].val()
                        data['forward'] = cForwards[0].val() // Для обратной совместимости
                    }

                    for (key in cForwards) {
                        if (forward.is(cForwards[key])) {
                            loading.show()
                            $.ajax({ method: 'GET', url: c.attr('data-source'), data: data })
                                .done(res => {
                                    c.html(res)
                                    processContainer(c)
                                })
                                .fail(() => { loading.hide('Ошибка') })
                                .always(() => loading.hide())
                            break
                        }
                    }
                }
            })
        })


        // При изменении данных в поле с атрибутом "data-formdata-source", происходит подгрузка данных из
        // указанной этим атрибутом ссылки и автозаполнение полей текущей формы подгруженными данными.
        // Параметром, со своим именем, передается значение данного поля.
        $(document).on('change', '[data-formdata-source]', function () {
            const forward = $(this)
            const form = forward.closest('form')
            const data = {}
            if (!forward.val()) return
            data[forward.attr('name')] = forward.val()
            loading.show()
            $.get(forward.attr('data-formdata-source'), data)
                .done(res => {
                    if (typeof res === 'object') {
                        if (('success' in res)) {
                            if (res.success == false) {
                                if ('error' in res) { notify.error(res.error) }
                            } else {
                                form.find('input, select, textarea').each(function () {
                                    const field = $(this)
                                    if ((field.attr('name') in res.data)) {
                                        let val = res.data[field.attr('name')]

                                        // checkbox
                                        if (val && (val.constructor === Array)) {
                                            if ($.inArray(parseInt(field.val()), val) !== -1 ) {
                                                console.log(field.val())
                                                field.prop('checked', 'checked')
                                            } else {
                                                field.prop('checked', '')
                                            }
                                        }

                                        // simple select 
                                        else if (val && (typeof val === 'object')) {
                                            if (('replace' in val) && (val.replace == true)) {
                                                field.empty()
                                            }
                                            for (let i = 0; i < val.options.length; i++) {
                                                field.append($('<option>', { 
                                                    value: val.options[i][0], 
                                                    text: val.options[i][1] 
                                                }))
                                            }
                                            field.val(val.value)
                                        }

                                        else {
                                            field.val(val)
                                        }

                                        field.change()
                                    }
                                })
                            }
                        }
                    }
                })
                .fail(err => loading.hide('Ошибка'))
                .always(() => loading.hide())
        })


        // Автоподгонка высоты в зависимости от содержимого для 
        // полей textarea с атрибутом data-height-auto
        ;(function () {
            const autosize = tarea => {
                const offset = tarea.offsetHeight - tarea.clientHeight
                $(tarea).css('height', 'auto').css('height', tarea.scrollHeight + offset)
            }

            const init = cont => {
                $(cont).find('textarea[data-height-auto]').each(function () { 
                    setTimeout(() => autosize(this), 500)
                    autosize(this) 
                })
            }

            $(document).on('change keyup input focus', 'textarea[data-height-auto]', function () { 
                autosize(this) 
            })
            init(document)
            $(document).on('process-ajax-container', function (e) { init(e.target) })
        })()


        // Автоподконка блоков с атрибутом "data-height-in-viewport" так, чтобы блок помещался 
        // в окно просмотра, при необходимости, в блок добавляется скролл
        // Решение не универсально
        ;(function () {
            const setHeightInViewport = elm => {
                elm.css('max-height', window.innerHeight - elm.offset().top)
                elm.parents().each(function () {
                    const c = $(this)
                    elm.css('max-height', parseInt(elm.css('max-height')) - parseInt(c.css('padding-bottom')))
                })
            }

            const init = container => {
                $(container).find('[data-height-in-viewport]').each(function () {
                    const elm = $(this)
                    elm.addClass('expressive-scroll overflow-auto')
                    $(window).resize(() => setHeightInViewport(elm))
                    setHeightInViewport(elm)
                })
            }

            init(document)
            $(document).on('process-ajax-container', function (e) { init(e.target) })
        })()

        // Для мультиселектов с атрибутом "data-selection-limit" ограничивает количество выбираемых
        // значений количеством указанным а этом атрибуте.
        $(document).on('click', 'select[data-selection-limit] option', function () {
            const option = $(this)
            const select = option.parent('select')
            const limit = select.attr('data-selection-limit')
            if (limit) {
                if (Object.keys(select.val()).length > limit) {
                    option.prop('selected', false)
                    if (Object.keys(select.val()).length > limit) {
                        select.val(select.val().slice(0, limit))
                    }
                }
            }
        })
        // Этот код подобен предыдущему блоку, но закрывает пробел предыдущего, когда 
        // элементы выбираются мышью с нажатой кнопкой, скольжением
        $(document).on('click', 'select[data-selection-limit]', function () {
            const select = $(this)
            const limit = select.attr('data-selection-limit')
            if (limit) {
                if (Object.keys(select.val()).length > limit) {
                    if (Object.keys(select.val()).length > limit) {
                        select.val(select.val().slice(0, limit))
                    }
                }
            }
        })


        // Кнопка прокрутки страницы в начало
        ;(function () {
            const backToTopBtn = $('<button type="button" class="btn btn-primary opacity-50 border btn-floating back_to_top" style="z-index: 999;" title="Наверх"><i class="bi bi-arrow-up"></i></button>')
            backToTopBtn.hide()
            backToTopBtn.appendTo('body')
            backToTopBtn.on('click', function () { document.body.scrollTop = document.documentElement.scrollTop = 0 })
            $(window).scroll(function () {
                if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20)
                    backToTopBtn.show()
                else
                    backToTopBtn.hide()
            })
        })()
		
        
		// Обработка выбора количества записей на странице
		$(document).on('change', '.count_per_page', function () {
            $(this).trigger('change.before-app-handlers')
			const s = $(this)
			if (s.val()) {
				const context = s.attr('data-target')
				if (!context) {
					window.location.href = s.val()
				} else {
					loading.show()
					$.get(s.val())
					    .done(res => $(context).html(res))
					    .fail(() => loading.hide('Ошибка'))
					    .always(() => loading.hide())
				}
			}
		})


        // Для полей с атрибутом data-text-upper=true при вводе, текст переводится в верхний регистр
        $(document).on('input', '[data-text-upper=true]', function () {
            $(this).val($(this).val().toUpperCase())
        })

        
        // Подключение очистки полей autocomplete light по нажатию на кнопку "Reset"
        ;(function () {
            const init = container => {
                $(container).find('form').each(function () {
                    $(this).on('reset', function () {
                        $(this).find('[data-autocomplete-light-function=select2]').each(function() {
                            $(this).empty().trigger('change')
                        })
                    })
                })
            }

            $(document).on('process-ajax-container', function (e) { init(e.target) })
            init(document)
        })()


        // Реализация показ/сокрытие для полей с паролем
        ;(function () {
            const init = container => {
                $(container).find('input[type="password"]').each(function () {
                    const field = $(this)
                    const parent = field.closest('div')

                    if (!field.hasClass('password-control__input')) {
                        field.addClass('password-control__input')
                    }

                    if (!parent.hasClass('position-relative')) {
                        parent.addClass('position-relative')
                    }

                    if (!parent.find('.password-control').length) {
                        $('<a href="#" class="password-control text-body"><i class="bi bi-eye fs-5"></i></a>')
                            .appendTo(parent)
                    }
                })

            }

            $(document).on('click', '.password-control', function(e) {
                e.preventDefault()
                const btn = $(this)
                const field = btn.closest('div').find('.password-control__input:first')
                if (field.attr('type') == 'password') {
                    btn.html('<i class="bi bi-eye-slash fs-5"></i>')
                    field.attr('type', 'text')
                } else {
                    btn.html('<i class="bi bi-eye fs-5"></i>')
                    field.attr('type', 'password')
                }
            })

            init(document)
            $(document).on('process-ajax-container', function (e) { init(e.target) })
        })()


        // В каждый контейнер чекбоксов с атрибутом "data-slaved-checkboxes" добавляется
        // мастер-чекбокс, который, по клику на нем, проецирует свое состояние на всю группу
        // Решение для связки [crispy-bootstrap5, django CheckboxSelectMultiple]
        ;(function () {
            const nums = new naturals()

            const init = container => {
                $(container).find('[data-slaved-checkboxes]').each(function () {
                    const cbxsContainer = $(this)
                    const slavedCbxs = cbxsContainer.find('input[type="checkbox"]')
                    const masterCbxNum = nums.next()
                    const masterCbxCont = $(`
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" name="master_${masterCbxNum}" id="id_master_${masterCbxNum}"> 
                            <label for="id_master_${masterCbxNum}" class="form-check-label text-expressive">Все</label>
                        </div>
                    `)

                    cbxsContainer.find('.form-check:first').closest('div').before(masterCbxCont)
                    masterCbxCont.find('input[type="checkbox"]').on('click', function () {
                        const masterCbx = $(this)
                        slavedCbxs.each(function () { 
                            $(this).prop('checked', masterCbx.prop('checked'))
                        })
                    })
                })
            }

            $(document).on('process-ajax-container', function (e) { init(e.target) })
            init(document)
        })()


        /** Инициализация bootstrap tooltips */
        ;(function () {
            const initTooltips = cont => $(cont).find('[data-bs-toggle="tooltip"]').each(function () { 
                new bootstrap.Tooltip(this) 
            })
            initTooltips(document)
            $(document).on('process-ajax-container', function (e) {
                initTooltips(e.target)
            })
        })()

        
        /** Инициализация bootstrap popover */
        ;(function () {
            const initPopovers = cont => $(cont).find('[data-bs-toggle="popover"]').each(function () { 
                new bootstrap.Popover(this)
            })
            initPopovers(document)
            $(document).on('process-ajax-container', function (e) {
                initPopovers(e.target)
            })
        })()


        /** 
         * Превью выбранного для загрузки изображения 
         * Функционал отрабатывает для полей загрузки файла с атрибутом "data-image-preview"
         */
        ;(function () {
            const img = src => src ? `<img src=${src} class="img-fluid img-thumbnail shadow shadow-md">` : ''
            const init = container => {
                $(container).find('[data-image-preview]').each(function () {
                    const field = $(this)
                    const clsBtn = '<a title="Удалить" role="button" class="link-danger preview--delete" style="position:absolute; top:-12px; right:-6px;"><i class="bi bi-x-circle-fill fs-5"></i></a>'
                    const displ = $('<div class="mt-3 position-relative"></div>')
                    const defaultSrc = field.closest('div').siblings('.input-group:first').find('a:first').attr('href')
                    const removeCheckbox = field.closest('div').siblings('.input-group:first').find('input[type=checkbox]:first')
                    const getDefaultSrc = () => removeCheckbox.length && !removeCheckbox.get(0).checked ? defaultSrc : !removeCheckbox.length ? defaultSrc: ''
                    const show = content => displ.html(`${content && ($(content).attr('src') != defaultSrc) ? clsBtn : ''}${content}`)

                    removeCheckbox.length && removeCheckbox.on('change', function () {
                        if ($.inArray(displ.find('img[src]:first').attr('src'), [defaultSrc, '', undefined]) !== -1) {
                            show(img(getDefaultSrc()))
                        }
                    })

                    field.on('change', function () {
                        let file = this.files[0]
                        if (file) {
                            const reader = new FileReader()
                            reader.onload = function (e) {
                                show(img(e.target.result)) 
                            }
                            reader.readAsDataURL(file)
                        } else {
                            show(img(getDefaultSrc()))
                        }
                    })

                    $(container).on('click', '.preview--delete', function () {
                        show(img(getDefaultSrc())) 
                        field.wrap('<form>').closest('form').get(0).reset()
                        field.unwrap()
                    })

                    field.closest('div').append(displ)
                    show(img(getDefaultSrc())) 
                })
            }

            init(document)
            $(document).on('process-ajax-container', function (e) { init(e.target) })
        })()


        /** 
         * Подключение glightbox галереи для элементов с классом "glightbox"
         */
        ;(function () {
            const init = container => { 
                try {
                    GLightbox({ 'selector': '.glightbox' }) 
                } catch (err) {
                    true
                }
            }

            $(document).on('process-ajax-container', function (e) { init(e.target) })
            init(document)
        })()


        /**
         * Для инпутов с атрибутом "data-formatted-number" автоматически
         * форматирует вводимое число, разделяя пробелами. (100000 -> 100 000)
         * 
         * При этом, на стороне сервера возникает необходимость обратного удаления этих пробелов 
         * (необходимость преобразования строки в число)
         */
        ;(function () {
            const numberFormat = input => {
                input.attr('type', 'text')
                //val = input.val().replace(/[^0-9.,]/g, '')
                //if (val.indexOf(".") != '-1') {
                //    val = val.substring(0, val.indexOf(".") + 3)
                //} 
                //val = val.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
                //input.val(val)
                let val = input.val().replace(/[^0-9.,]/g, '')
                val = val.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
                input.val(val)
            }

            const init = container => { 
                $(container).on('input', 'input[data-formatted-number]', function () {
                    numberFormat($(this))
                })

                $(container).find('input[data-formatted-number]').each(function () {
                    numberFormat($(this))
                })
            }

            $(document).on('process-ajax-container', function (e) { init(e.target) })
            init(document)
        })()


        /**
         * Для таблиц, при указании для колонки(td) в tfoot атрибута data-total-by-col="[позиция]"
         * в эту колонку записывается сумма значений в input-тах в колонках из tbody в соответствующей позиции 
         */
        ;(function () {
            const tables = []

            const calcByPosition = (table, pos) => {
                let result = 0
                table.find('tbody:first').find('tr:not([style="display: none;"])').each(function () {
                    let val = $(this).find(`td:nth-child(${pos})`).find(`input:first`).val()
                    val = val ? val.replace(/[^0-9.,]/g, '') : 0
                    if (val) result += parseFloat(val) 
                })
                return result
            }

            const calc = table => {
                table.find('[data-total-by-col]').each(function () {
                    const resultPlace = $(this)
                    let result = calcByPosition(table, resultPlace.attr('data-total-by-col'))
                    resultPlace.html(new Intl.NumberFormat('ru-RU').format(result.toFixed(2)))
                })
            }

            const process = container => {
                $(container).find('[data-total-by-col]').each(function () {
                    const table = $(this).closest('table')
                    const tid = table.getPath()
                    if (!(tid in tables)) {
                        tables.push(tid)
                        table.on('input', 'input', function () { calc(table) })
                        table.on('subform-add', function () { calc(table) })
                        table.on('subform-delete', function () { calc(table) })
                        calc(table)
                    }
                })
            }

            $(document).on('process-ajax-container', function (e) { process(e.target) })
            process(document)
        })()


        /**
         * Для формы с атрибутами id и method=post, расположенной в модалке, 
         * кнопку отправки формы переносит в футер модалки
         */
        ;(function () {
            const process = container => {
                $(container).find('form[id][method=post] input[type="submit"]').each(function () {
                    const btn = $(this)
                    const form = btn.closest('form')
                    const modal = btn.closest('.modal')
                    const modalFooter = modal.find('.modal-footer:first')
                    if (modalFooter.length) {
                        modalFooter.html(btn.addClass('mt-2 mb-2 me-2').attr('form', form.attr('id')))
                    }
                })
            }
            process(document)
            $(document).on('process-ajax-container', function (e) {
                process(e.target)
            })
        })()


        /**
         * Функционал сортировки по полям для таблиц с классом .table-sortable
         * 
         * Для таблицы указывается дата атрибут data-form, где указывается идентификатор формы-фильтра.
         * В заголовке таблицы, для полей по которым можно упорядочить данные, задаются 
         * дата атрибуты data-order-field, которые, должны содержать наименование поля в данных.
         * Также, вместе с data-order-field указывается атрибут data-order-type в котором, 
         * для первичного показа, для поля по которому произведено первичное упорядочивание, 
         * можно указать тип этого упорядочивания (DESC, ASC)
         */
        ;(function () {
            const getOrCreateOrderByField = form => {
                const orderByFieldName = 'order_by'
                if (form.find(`input[name="${orderByFieldName}"]`).length == 0) {
                    $(`<input type="hidden" name="${orderByFieldName}" />`).appendTo(form)
                }
                return form.find(`input[name="${orderByFieldName}"]:first`)
            }

            const process = cont => {
                $(cont).find('.table-sortable').each(function () {
                    const table = $(this)
                    const forms = table.attr('data-form') ? table.attr('data-form').split(/\s*,\s*/).map(form => $(form)) : []
                    
                    if (forms.length > 0) {
                        table.find('[data-order-field]').each(function () {
                            const th = $(this)
                            const field = th.attr('data-order-field')
                            const orderType = th.attr('data-order-type')
                            if (field && orderType) {
                                getOrCreateOrderByField(forms[0]).val(orderType == 'DESC' ? `-${field}` : field)
                                const arrowClass = orderType == 'DESC' ? 'order_desc' : 'order_asc'
                                th.html(`<div class="${arrowClass}">${th.text()}</div>`)
                            }
                            th.on('click', function () {
                                getOrCreateOrderByField(forms[0]).val(orderType == 'DESC' ? field : `-${field}`)
                                forms[0].submit()
                            })
                        })
                    }
                })
            }

            process(document)
            $(document).on('process-ajax-container', function (e) {
                process(e.target)
            })
        })()


        return {
            timer: timer,
            naturals: naturals,
            dataURIToBlob: dataURIToBlob,
            isjQueryObj: isjQueryObj,
            loading: loading,
            notify: notify,
            sendAjaxForm: sendAjaxForm,
            ajaxContainersInitializer: ajaxContainersInitializer,
            paramsModal: paramsModal
        }
    }


    if (typeof (window.app) === 'undefined') {
        window.app = app()
    }
})(window)


////////// JQuery ext //////////


$.urlParam = function(name, dflt=null){
    const results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href)
    if (results == null)  return dflt
    return decodeURI(results[1]) || 0
}


$.fn.cursorToPos = function(pos) {
    if ($(this).get(0).setSelectionRange) {
        $(this).get(0).setSelectionRange(pos, pos);
    } else if ($(this).get(0).createTextRange) {
        var range = $(this).get(0).createTextRange();
        range.collapse(true);
        range.moveEnd('character', pos);
        range.moveStart('character', pos);
        range.select();
    }
};


$.fn.cursorToEnd = function () {
    return this.each(function () {
        $(this).focus()
        if (this.setSelectionRange) {
            const len = $(this).val().length * 2
            if (this.type === 'number') {
                this.type = 'text'
                this.setSelectionRange(len, len)
                this.type = 'number'
            } else {
                this.setSelectionRange(len, len)
            }
        } else {
            $(this).val($(this).val())
        }
        this.scrollTop = 999999
    })
}


$.fn.extend({
    getPath: function() {
        var pathes = [];

        this.each(function(index, element) {
            var path, $node = jQuery(element);

            while ($node.length) {
                var realNode = $node.get(0), name = realNode.localName;
                if (!name) { break; }

                name = name.toLowerCase();
                var parent = $node.parent();
                var sameTagSiblings = parent.children(name);

                if (sameTagSiblings.length > 1)
                {
                    var allSiblings = parent.children();
                    var index = allSiblings.index(realNode) + 1;
                    if (index > 0) {
                        name += ':nth-child(' + index + ')';
                    }
                }

                path = name + (path ? ' > ' + path : '');
                $node = parent;
            }

            pathes.push(path);
        });

        return pathes.join(',');
    }
});
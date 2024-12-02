/**
 * Показ и сокрытие блока с субформами материалов при
 * выборе значения в поле работы или очистки оного поля.
 * Относится к форма добавления/редактирования задачи.
 */
;(function () {
    const process = (sel) => {
        const val = sel.find(":selected").val()
        const subformsWrapper = sel.closest('form').find('#task_material_list-subforms')
        if (subformsWrapper.length) {
            val ? subformsWrapper.show() : subformsWrapper.hide() 
        }
    }

    const init = cont => {
        $(cont).find('#task-form select[name="s_work"]').each(function () {
            const sel = $(this)
            sel.on('change', function () { process(sel) })
            process(sel)
        })
    }

    $(document).on('process-ajax-container', function (e) { init(e.target) })
    init(document)
})()
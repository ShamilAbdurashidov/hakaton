document.addEventListener("DOMContentLoaded", function () {
    const subformTemplates = [];
    const subformNextNum = [];
    const subformActuals = [];

    const getPrefix = formset => formset.attr('data-prefix');

    const normalizeSubformTemplatesPrefix = prefix => prefix.replace(RegExp('-(\\d+)-', 'g'), '--num--');

    const getSubformTemplate = prefix => { 
        let normalizedPrefix = normalizeSubformTemplatesPrefix(prefix)
        let tpt = subformTemplates[normalizedPrefix].clone(); 
        if (prefix != normalizedPrefix) {
            tpt.html(tpt.html().replace(RegExp(normalizedPrefix.replace(RegExp('--num--'), '-0-'), 'g'), prefix));
        }
        return tpt;
    }

    const hasSubformTemplate = prefix => normalizeSubformTemplatesPrefix(prefix) in subformTemplates;

    const setSubformTemplate = (prefix, template) => {
        //template.wrap('<form>').closest('form').get(0).reset();
        //template.unwrap();
        template.find("span.select2").remove();
        template.find("select.modelselect2forwardextras").select2();
        subformTemplates[normalizeSubformTemplatesPrefix(prefix)] = template;
    };

    const getSubformNextNum = prefix => {
        subformNextNum[prefix] = $('.formset[data-prefix="'+ prefix +'"]:first').children('.subform').length;
        return subformNextNum[prefix];
    }

    const initSubformActuals = prefix => {
        subformActuals[prefix] = $('.formset[data-prefix="'+ prefix +'"]:first').children('.subform').length;
    }
    
    const incrementSubformActuals = prefix => {
        subformActuals[prefix] = subformActuals[prefix] + 1;
    }

    const decrementSubformActuals = prefix => {
        subformActuals[prefix] = subformActuals[prefix] - 1;
    }

    const subformDelBtn = subform => {
        if (subform.closest('.formset').prop("tagName") == 'TBODY') {
            return subform.children('td').children('.subform--delete');
        }
        return subform.children('.subform--delete');
    }

    const addBtnContainer = formset => {
        if (formset.prop("tagName") == 'TBODY') {
            return formset.children('tr:last').find('td .add-btn-container');
        }
        return formset.children('.add-btn-container');
    }

    const handleDelete = function () {
        const closeBtn = $(this);
        const subform = closeBtn.closest('.subform');
        const formset = subform.closest('.formset');
        const prefix = getPrefix(formset);
        const MAX_NUM_FORMS = $('#id_' + prefix + '-MAX_NUM_FORMS');
        const MIN_NUM_FORMS = $('#id_' + prefix + '-MIN_NUM_FORMS');
        
        subform.fadeOut(300, () => { 
            const matches = subform.html().match(RegExp(prefix + '-(\\d+)-'));
            const subformIdx = matches[1];

            formset.append('<input type="hidden" name="' + prefix + '-' + subformIdx + '-DELETE" value="1">')
            subform.hide(); 
            formset.trigger('subform-delete')
            decrementSubformActuals(prefix)

            if (parseInt(MAX_NUM_FORMS.val()) > subformActuals[prefix]) {
                addBtnContainer(formset).find('.subform--add').show();
            }

            if (MIN_NUM_FORMS && (parseInt(MIN_NUM_FORMS.val()) >= subformActuals[prefix])) {
                subformDelBtn(formset.children('.subform ')).hide()
            }
        });
    };

    const handleAdd = function (e) {
        const formset = $(this).closest('.formset');
        const prefix = getPrefix(formset);
        const TOTAL_FORMS = $('#id_' + prefix + '-TOTAL_FORMS');
        const MAX_NUM_FORMS = $('#id_' + prefix + '-MAX_NUM_FORMS');
        const MIN_NUM_FORMS = $('#id_' + prefix + '-MIN_NUM_FORMS');

        const newSubform = getSubformTemplate(prefix);

        newSubform.html(newSubform.html().replace(RegExp(prefix + '-(\\d+)-', 'g'), prefix + '-' + getSubformNextNum(prefix) + '-'));
        newSubform.addClass('position-relative');
        newSubform.hide();

        newSubform.find('.formset.expand').each(function () { 
            addAddBtn($(this));
        });

        newSubform.find('.subform').each(function () { addCloseBtn($(this)) });

        formset.children('.subform:last').after(newSubform);
        addCloseBtn(newSubform);
        if (newSubform.find('.formset').length) {
            init(newSubform.get(0))
        }
        newSubform.fadeIn(300);
        formset.trigger('subform-add')

        TOTAL_FORMS.val(formset.children('.subform').length);
        incrementSubformActuals(prefix);
        if (parseInt(MAX_NUM_FORMS.val()) <= subformActuals[prefix]) {
            $(this).hide();
        }

        if (MIN_NUM_FORMS && (parseInt(MIN_NUM_FORMS.val()) < subformActuals[prefix])) {
            subformDelBtn(formset.children('.subform ')).show()
        }
    };

    const addCloseBtn = subform => {
        if (!subform.hasClass('disabled') && !subformDelBtn(subform).length) {
            subform.addClass('position-relative');
            var btn = $('<a title="Удалить" role="button" class="link-danger subform--delete"><i class="bi bi-x-circle-fill fs-5"></i></a>');
            
            if (subform.closest('.formset').prop("tagName") == 'TBODY') {
                //var btn = $(`
                //<a title="Удалить" role="button" class="link-danger subform--delete d-flex align-items-center"><span class="border border-secondary" style="margin-top:2px; height:1px; width:9px;"></span><i class="bi bi-x-circle-fill fs-5"></i></a>`);
                const td = subform.find('td:last')
                //btn.css({top: 10, right: -26, position:'absolute'});
                btn.css({top: 10, right: -9, position:'absolute'});
                td.append(btn)

            } else {
                btn.css({top: -15, right: -10, position:'absolute'});
                subform.prepend(btn);
            }

            btn.on('click', handleDelete);
        }
    };

    const addAddBtn = formset => {
        if (!addBtnContainer(formset).length) {
            const btn = $('<div class="text-end add-btn-container"><a class="subform--add" role="button"><i class="bi bi-plus-circle me-1"></i>Добавить</a></div>');
            
            if (formset.prop("tagName") == 'TBODY') {
                const tr = $(`<tr><td colspan="42" class="text-end"></td></tr>`) 
                tr.find('td').append(btn)
                formset.append(tr)

            } else {
                formset.append(btn)
            }
            
            btn.children('.subform--add').on('click', handleAdd);
        }
    }

    const init = function(container) {
        $(container).find('.formset.expand').each(function () {
            const formset = $(this);
            const prefix = getPrefix(formset);
            const TOTAL_FORMS = $('#id_' + prefix + '-TOTAL_FORMS');
            const MAX_NUM_FORMS = $('#id_' + prefix + '-MAX_NUM_FORMS');
            const MIN_NUM_FORMS = $('#id_' + prefix + '-MIN_NUM_FORMS');

            initSubformActuals(prefix)
    
            if (!hasSubformTemplate(prefix)) {
                setSubformTemplate(prefix, formset.children('.subform:last').clone())
            }

            formset.children('.subform').each(function () { addCloseBtn($(this)) });
            if(formset.children('.subform').length != formset.children('.subform.disabled').length) {
                addAddBtn(formset);
            }

            if (parseInt(MAX_NUM_FORMS.val()) == parseInt(TOTAL_FORMS.val())) {
                addBtnContainer(formset).find('.subform--add').hide();
            }

            if (MIN_NUM_FORMS && (parseInt(MIN_NUM_FORMS.val()) >= parseInt(TOTAL_FORMS.val()))) {
                subformDelBtn(formset.children('.subform ')).hide()
            }
            
        });
    };

    init(document)
    $(document).on('process-ajax-container', function (e) {
        init(e.target)
    })

})
from dal import autocomplete, forward


class ForwardExtrasMixin(object):
    def __init__(self, url=None, forward=None, unselect_if_forward_changed=None, *args, **kwargs):
        self.unselect_if_forward_changed = unselect_if_forward_changed
        super(ForwardExtrasMixin, self).__init__(url, forward, *args, **kwargs)

    def build_attrs(self, *args, **kwargs):
        attrs = super(ForwardExtrasMixin, self).build_attrs(*args, **kwargs)

        if self.unselect_if_forward_changed is not None and self.forward is not None:
            values = []
            for fw in self.forward:
                if isinstance(fw, str):
                    values.append(fw)
                elif isinstance(fw, forward.Field):
                    values.append(fw.src)
            if values:
                attrs.setdefault('data-autocomplete-light-unselect-if-forward-changed', ','.join(values))
        return attrs

    class Media:
        js = (
            'common/select2forwardextras.js',
        )


class ModelSelect2ForwardExtras(ForwardExtrasMixin, autocomplete.ModelSelect2):
    pass


class ModelSelect2MultipleForwardExtras(ForwardExtrasMixin, autocomplete.ModelSelect2Multiple):
    pass


class ListSelect2ForwardExtras(ForwardExtrasMixin, autocomplete.ListSelect2):
    pass
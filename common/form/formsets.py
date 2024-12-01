from django.forms.models import BaseModelFormSet


class ModelFormSet(BaseModelFormSet):

    def save_new(self, form, commit=True, **kwargs):
        return form.save(commit=commit, **kwargs)

    def save_existing(self, form, instance, commit=True, **kwargs):
        return form.save(commit=commit, **kwargs)
    
    def save(self, commit=True, **kwargs):
        if not commit:
            self.saved_forms = []

            def save_m2m():
                for form in self.saved_forms:
                    form.save_m2m()

            self.save_m2m = save_m2m
        if self.edit_only:
            return self.save_existing_objects(commit, **kwargs)
        else:
            return self.save_existing_objects(commit, **kwargs) + self.save_new_objects(commit, **kwargs)
        
    def save_existing_objects(self, commit=True, **kwargs):
        self.changed_objects = []
        self.deleted_objects = []
        if not self.initial_forms:
            return []

        saved_instances = []
        forms_to_delete = self.deleted_forms
        for form in self.initial_forms:
            obj = form.instance
            # If the pk is None, it means either:
            # 1. The object is an unexpected empty model, created by invalid
            #    POST data such as an object outside the formset's queryset.
            # 2. The object was already deleted from the database.
            if obj.pk is None:
                continue
            if form in forms_to_delete:
                self.deleted_objects.append(obj)
                self.delete_existing(obj, commit=commit)
            elif form.has_changed():
                self.changed_objects.append((obj, form.changed_data))
                saved_instances.append(self.save_existing(form, obj, commit=commit, **kwargs))
                if not commit:
                    self.saved_forms.append(form)
        return saved_instances

    def save_new_objects(self, commit=True, **kwargs):
        self.new_objects = []
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(self.save_new(form, commit=commit, **kwargs))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects
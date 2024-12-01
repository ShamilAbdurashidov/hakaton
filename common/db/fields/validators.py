
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


def validate_file_size(value):
    filesize = value.size
    max_size = 5242880  #5 МБ
    if filesize > max_size:
        raise ValidationError(_("Размер файла не должен превышать %(maxsize)s. Текущий размер файла: %(filesize)s") % {
            'maxsize': filesizeformat(max_size), 'filesize': filesizeformat(filesize)})
import os
# import magic
# from django.core.exceptions import ValidationError


# def validate_is_jpg_or_png(file):
    # valid_mime_types = ['application/pdf']
    # file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    # if file_mime_type not in valid_mime_types:
    #     raise ValidationError('Unsupported file type.')
    # valid_file_extensions = ['.pdf']
    # ext = os.path.splitext(file.name)[1]
    # if ext.lower() not in valid_file_extensions:
    #     raise ValidationError('Unacceptable file extension.')
from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value


# -*- coding: utf-8 -*-

# CKEditor
# https://github.com/django-ckeditor/django-ckeditor

CKEDITOR_CONFIGS = {
    'default': {
        # 'toolbar': 'Basic',
        'toolbar': [
            ['Undo', 'Redo'],
            ['Format', 'FontSize'],
            ['Bold', 'Italic', 'Underline', 'SpellChecker'],
            ['NumberedList', 'BulletedList', "Indent", "Outdent",
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Image', 'Table', 'Link', 'Unlink',
             'SectionLink', 'Subscript', 'Superscript'],
            ['Source'],
            ['Maximize'],
        ],
        'width': '100%',
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_IMAGE_QUALITY = 90
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    APP_TITLE = 'Flask Demo'
    # SWAGGER_UI_JSONEDITOR = True

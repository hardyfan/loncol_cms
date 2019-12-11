from django.apps import AppConfig

default_app_config = 'apps.base.BaseConfig'
VERBOSE_APP_NAME = u"内容"


class BaseConfig(AppConfig):
    name = 'apps.base'
    verbose_name = VERBOSE_APP_NAME
    main_menu_index = 0

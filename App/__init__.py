import os

if os.environ.get('RUN_MAIN', None) != 'true':
    default_app_config = 'BoschMCM_API.myAppConfig.MyAppConfig'


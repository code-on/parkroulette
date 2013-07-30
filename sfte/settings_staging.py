from settings import MIDDLEWARE_CLASSES, INSTALLED_APPS

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar',)
INTERNAL_IPS = ('217.12.211.117', '107.3.149.69')
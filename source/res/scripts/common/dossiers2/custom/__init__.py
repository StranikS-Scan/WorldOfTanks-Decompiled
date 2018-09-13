# Embedded file name: scripts/common/dossiers2/custom/__init__.py


def init():
    from dossiers2.custom.cache import buildCache
    buildCache()
    from dossiers2.custom.dependencies import init as dependencies_init
    dependencies_init()

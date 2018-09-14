# Embedded file name: scripts/client/gui/login/__init__.py
from gui import GUI_SETTINGS
if GUI_SETTINGS.socialNetworkLogin['enabled']:
    from social_networks import Manager, SOCIAL_NETWORKS
    g_loginManager = Manager()
else:
    from Manager import Manager
    g_loginManager = Manager()
__all__ = ['g_loginManager']

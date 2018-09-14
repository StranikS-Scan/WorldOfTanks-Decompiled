# Embedded file name: scripts/client/gui/wgnc/__init__.py
from gui.wgnc.provider import g_instance as g_wgncProvider
from gui.wgnc.events import g_wgncEvents
from gui.wgnc import settings as wgnc_settings
__all__ = ('g_wgncProvider', 'g_wgncEvents', 'wgnc_settings')

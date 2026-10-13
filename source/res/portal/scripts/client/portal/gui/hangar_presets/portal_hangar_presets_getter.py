# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/hangar_presets/portal_hangar_presets_getter.py
from gui.hangar_presets import DefaultPresetsGetter
from portal_common.portal_constants import QUEUE_TYPE

class PortalHangarPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.PORTAL

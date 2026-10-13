# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/hangar_presets/__init__.py
from gui.shared.system_factory import registerHangarPresetsReader, registerHangarPresetGetter
from portal.gui.hangar_presets.portal_hangar_presets_reader import PortalHangarPresetsReader
from portal.gui.hangar_presets.portal_hangar_presets_getter import PortalHangarPresetsGetter
from portal_common.portal_constants import QUEUE_TYPE

def registerPortalHangarPresets():
    registerHangarPresetsReader(PortalHangarPresetsReader)
    registerHangarPresetGetter(QUEUE_TYPE.PORTAL, PortalHangarPresetsGetter)

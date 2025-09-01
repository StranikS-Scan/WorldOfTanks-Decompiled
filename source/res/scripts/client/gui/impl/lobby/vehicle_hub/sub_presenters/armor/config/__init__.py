# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/config/__init__.py
from __future__ import absolute_import
import typing
import ResMgr
import section2dict
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.schemas import configSchema
if typing.TYPE_CHECKING:
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.models import ConfigModel
CONFIG_PATH = 'gui/armor_inspector.xml'
__config = None

def getConfig():
    global __config
    if __config is not None:
        return __config
    else:
        root = ResMgr.openSection(CONFIG_PATH)
        rawData = section2dict.parse(root)
        __config = configSchema.deserialize(rawData)
        return __config

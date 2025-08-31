# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_tankman_tooltip_adapters.py
from gui.impl.lobby.tooltips.tankman_tooltip_adapters import TankmanInfoAdapter
from gui.impl import backport
from gui.impl.gen import R
from gui.doc_loaders.event_settings_loader import getVehicleCharacteristics
from white_tiger_common.wt_constants import WT_TAGS
_IMG_PATH = R.images.gui.maps.icons
_STR_PATH = R.strings.event.tankmanTooltip

class WTTankmanInfoAdapter(TankmanInfoAdapter):
    __slots__ = ()

    def getLabel(self):
        vehicleType = self._tankmanInfo.vehicleDescr.type
        if WT_TAGS.WT_BOSS in vehicleType.tags:
            return backport.text(_STR_PATH.status.boss())
        return backport.text(_STR_PATH.status.boss_2025()) if WT_TAGS.WT_BOSS_2025 in vehicleType.tags else backport.text(_STR_PATH.status.hunter(), vehicle=vehicleType.userString)

    def getDescription(self):
        vehicleName = self._tankmanInfo.vehicleDescr.name
        info = getVehicleCharacteristics().get(vehicleName)
        return backport.text(_STR_PATH.dyn(info.role).descr())

    def getSkillsLabel(self):
        pass

    def getSkills(self):
        return []

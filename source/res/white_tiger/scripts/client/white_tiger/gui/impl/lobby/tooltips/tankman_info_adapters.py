# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/tankman_info_adapters.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.tooltips.tankman_tooltip_adapters import TankmanInfoAdapter
from white_tiger.gui.doc_loaders.gui_settings_loader import getVehicleCharacteristics
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
_STR_PATH = R.strings.white_tiger_lobby.tankmanTooltip

class WTTankmanInfoAdapter(TankmanInfoAdapter):
    __slots__ = ()

    def getLabel(self):
        vehicleType = self._tankmanInfo.vehicleDescr.type
        return backport.text(_STR_PATH.status.boss()) if WT_VEHICLE_TAGS.BOSS in vehicleType.tags else backport.text(_STR_PATH.status.hunter(), vehicle=vehicleType.userString)

    def getDescription(self):
        vehicleName = self._tankmanInfo.vehicleDescr.name
        info = getVehicleCharacteristics().get(vehicleName)
        return backport.text(_STR_PATH.dyn(info.role).descr())

    def getSkillsLabel(self):
        pass

    def getSkills(self):
        return []

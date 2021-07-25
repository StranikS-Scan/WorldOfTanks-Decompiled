# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/main_tank_setup/hangar.py
from BWUtil import AsyncReturn
from async import async
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntroAmmunitionSetupWindow, isIntroOptionalDevicesSetupShown, isIntroEpicBattleAbilitiesShown
from gui.impl.lobby.tank_setup.main_tank_setup.base import MainTankSetupView

class HangarMainTankSetupView(MainTankSetupView):
    __slots__ = ()

    @async
    def _doSwitch(self, setupName, slotID):
        if setupName == TankSetupConstants.OPT_DEVICES and not isIntroOptionalDevicesSetupShown():
            yield showIntroAmmunitionSetupWindow(setupName)
        if setupName == TankSetupConstants.BATTLE_ABILITIES and not isIntroEpicBattleAbilitiesShown():
            yield showIntroAmmunitionSetupWindow(setupName)
        if self._viewModel is not None:
            yield super(HangarMainTankSetupView, self)._doSwitch(setupName, slotID)
        raise AsyncReturn(None)
        return

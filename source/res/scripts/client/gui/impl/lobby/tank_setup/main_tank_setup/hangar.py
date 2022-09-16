# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/main_tank_setup/hangar.py
from BWUtil import AsyncReturn
from wg_async import wg_async
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntro
from gui.impl.lobby.tank_setup.main_tank_setup.base import MainTankSetupView

class HangarMainTankSetupView(MainTankSetupView):
    __slots__ = ()

    @wg_async
    def _doSwitch(self, setupName, slotID):
        yield showIntro(setupName)
        if self._viewModel is not None:
            yield super(HangarMainTankSetupView, self)._doSwitch(setupName, slotID)
        raise AsyncReturn(None)
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/steam_mode.py
import WGC
from gui import DialogsInterface
from base_wgc_mode import BaseWgcMode
from helpers import dependency
from skeletons.gameplay import IGameplayLogic

class SteamMode(BaseWgcMode):
    __gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self, view):
        super(SteamMode, self).__init__(view, None)
        return

    def onPopulate(self):
        if self.__checkWgcAvailable():
            super(SteamMode, self).onPopulate()

    def updateForm(self):
        if self._loginManager.wgcAvailable:
            self._view.as_showSteamLoginFormS({'userName': WGC.getUserName()})
        else:
            self._view.as_showSteamLoginFormS({})

    def _onWgcError(self):
        self._loginManager.tryPrepareWGCLogin()
        self.__checkWgcAvailable()

    def __checkWgcAvailable(self):
        if not self._loginManager.wgcAvailable:
            DialogsInterface.showI18nInfoDialog('steamStartNeeded', self.__onDialogCallback)
            return False
        return True

    def __onDialogCallback(self, _):
        self.__gameplay.quitFromGame()

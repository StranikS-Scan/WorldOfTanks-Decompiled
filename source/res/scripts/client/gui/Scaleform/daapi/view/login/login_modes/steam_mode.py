# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/steam_mode.py
import LGC
from gui import DialogsInterface
from base_lgc_mode import BaseLgcMode
from helpers import dependency
from skeletons.gameplay import IGameplayLogic

class SteamMode(BaseLgcMode):
    __gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self, view):
        super(SteamMode, self).__init__(view, None)
        return

    def onPopulate(self):
        if self.__checkLgcAvailable():
            super(SteamMode, self).onPopulate()

    def updateForm(self):
        if self._loginManager.lgcAvailable:
            self._view.as_showSteamLoginFormS({'userName': LGC.getUserName()})
        else:
            self._view.as_showSteamLoginFormS({})

    def _onLgcError(self):
        self._loginManager.tryPrepareLGCLogin()
        self.__checkLgcAvailable()

    def __checkLgcAvailable(self):
        if not self._loginManager.lgcAvailable:
            DialogsInterface.showI18nInfoDialog('steamStartNeeded', self.__onDialogCallback)
            return False
        return True

    def __onDialogCallback(self, _):
        self.__gameplay.quitFromGame()

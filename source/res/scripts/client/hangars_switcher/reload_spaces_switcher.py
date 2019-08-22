# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/reload_spaces_switcher.py
from helpers import dependency
from skeletons.hangars_switcher import HangarNames
from skeletons.hangars_switcher import IHangarsSwitcher
from skeletons.gui.shared.utils import IHangarSpaceReloader
from gui.impl.gen import R
from gui.impl import backport
_HANGAR_PARAMS = {HangarNames.BATTLE_ROYALE: ('h26_battle_royale', 'battleRoyale/hangarLoading', backport.image(R.images.gui.maps.icons.lobby.brWaitingBg())),
 HangarNames.FESTIVAL: ('h20_wot_bday', 'festival/hangarLoading', backport.image(R.images.gui.maps.icons.lobby.brWaitingBg()))}

class ReloadSpacesSwitcher(IHangarsSwitcher):
    hangarSpaceReloader = dependency.descriptor(IHangarSpaceReloader)

    def switchToHangar(self, hangarName):
        if hangarName not in _HANGAR_PARAMS:
            return
        spaceName, waitingMessage, backgroundImage = _HANGAR_PARAMS[hangarName]
        self.hangarSpaceReloader.changeHangarSpace(spaceName, waitingMessage, backgroundImage)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_ctrl.py
import WWISE
from helpers import dependency
from historical_battles.skeletons.gui.sound_controller import IHBSoundController
from historical_battles.gui.sounds.sound_constants import HangarParallaxState
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
_FRONT_STATES = [HangarParallaxState.DEFENSIVE, HangarParallaxState.LAST_STAND, HangarParallaxState.ATTACK]

class HBSoundController(IHBSoundController):
    _gameEventController = dependency.descriptor(IGameEventController)

    def init(self):
        self._gameEventController.onSelectedFrontChanged += self.__updateFront

    def fini(self):
        self._gameEventController.onSelectedFrontChanged -= self.__updateFront

    def start(self):
        if self._gameEventController.isEnabled():
            self.__updateFront()

    def activateBattleSoundRemapping(self):
        WWISE.activateRemapping(HB_GAME_PARAMS_KEY)

    def deactivateBattleSoundRemapping(self):
        WWISE.deactivateRemapping(HB_GAME_PARAMS_KEY)

    def __updateFront(self):
        frontController = self._gameEventController.frontController
        selectedFrontID = frontController.getSelectedFrontID()
        state = HangarParallaxState.BLOCK
        if frontController.getFront(selectedFrontID).isAvailable():
            state = _FRONT_STATES[selectedFrontID]
        WWISE.WW_setState(HangarParallaxState.GROUP, state)

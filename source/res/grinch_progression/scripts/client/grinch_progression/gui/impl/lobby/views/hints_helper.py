# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/hints_helper.py
import logging
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from grinch_progression.account_helpers.account_settings import readHintState, setHintState, readCurrentHintState, setCurrentHintState
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import HintState
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from grinch.skeletons.battle_controller import IGrinchController
from tutorial.control.context import GLOBAL_FLAG
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)
BATTLE_BTN_HINT_ID = OnceOnlyHints.GRINCH_PROGRESSION_FIGHT_BUTTON_HINT

class HintsHelper(object):
    __gpController = dependency.descriptor(IGrinchProgressionController)
    _grinchController = dependency.descriptor(IGrinchController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(HintsHelper, self).__init__()
        self.__state = HintState.NONE if not readCurrentHintState() else readCurrentHintState()
        self.__isVisible = False
        self.updateState()

    def clear(self):
        if self.__state == HintState.COINS:
            if self.__gpController.enoughForClaimReward:
                setCurrentHintState(HintState.MOVE)
            else:
                setCurrentHintState(HintState.BATTLE)

    def fightButtonHintShown(self):
        return bool(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(BATTLE_BTN_HINT_ID))

    @property
    def hintState(self):
        return self.__state

    @property
    def isHintVisible(self):
        return self.__isVisible

    def hideHint(self, hintId):
        if not self._grinchController.isInPrimeTime():
            return
        viewedHints = readHintState()
        if hintId and hintId not in viewedHints:
            viewedHints.add(hintId)
            setHintState(viewedHints)
            self.updateState()

    def setFightButtonFlag(self, value):
        if self.hintState == HintState.BATTLE and self.isHintVisible:
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.GRINCH_FIGHT_BUTTON_ACTIVE, value)

    def updateState(self):
        lastState = self.__state
        viewedHints = readHintState()
        enoughForClaim = self.__gpController.enoughForClaimReward
        self.__isVisible = True
        if not self._grinchController.isInPrimeTime():
            self.__isVisible = False
        elif lastState == HintState.NONE:
            if enoughForClaim:
                self.__setState(HintState.MOVE)
            else:
                self.__setState(HintState.VEHICLE)
        elif lastState == HintState.VEHICLE:
            if HintState.VEHICLE.value in viewedHints:
                self.__setState(HintState.COINS)
            elif enoughForClaim:
                self.__setState(HintState.MOVE)
        elif lastState == HintState.COINS:
            if HintState.COINS.value in viewedHints:
                self.__setState(HintState.BATTLE)
            elif enoughForClaim:
                self.__setState(HintState.MOVE)
        elif lastState == HintState.BATTLE:
            if enoughForClaim:
                self.__setState(HintState.MOVE)
                getTutorialGlobalStorage().setValue(GLOBAL_FLAG.GRINCH_FIGHT_BUTTON_ACTIVE, False)
        elif lastState == HintState.MOVE:
            if HintState.MOVE.value in viewedHints:
                self.__isVisible = False
                if not enoughForClaim:
                    self.__setState(HintState.MISSIONS)
        elif lastState == HintState.MISSIONS:
            if HintState.MISSIONS.value in viewedHints:
                self.__setState(HintState.FINISH)
                self.__isVisible = False

    def __setState(self, state):
        self.__state = state
        setCurrentHintState(state)

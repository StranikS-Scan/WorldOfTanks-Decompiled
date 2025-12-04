# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_raccoon_animation_controller.py
import CGF
import Event
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import State
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.ny_constants import NY_HAS_PET_ANIMATION
from new_year.skeletons.new_year import IRaccoonAnimationController
from new_year.cgf.raccoon_customization_components import RaccoonManager, RaccoonMoodStates
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
_STATE_TO_MOOD = {State.FUN: RaccoonMoodStates.HAPPY,
 State.NORMAL: RaccoonMoodStates.NEUTRAL,
 State.SAD: RaccoonMoodStates.SAD}

class RaccoonAnimationController(IRaccoonAnimationController):
    __slots__ = ('__animationsEnabled', '__eventManager')
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(RaccoonAnimationController, self).__init__()
        self.__animationsEnabled = False
        self.__eventManager = Event.EventManager()
        self.onShowGift = Event.Event(self.__eventManager)

    def onConnected(self):
        self.__animationsEnabled = getNYSetting(NY_HAS_PET_ANIMATION)

    def onDisconnect(self):
        self.__eventManager.clear()

    @property
    def __raccoonManager(self):
        return CGF.getManager(self.__hangarSpace.spaceID, RaccoonManager) if self.__hangarSpace.spaceID else None

    def showLetterAction(self):
        if not self.__animationsEnabled:
            self.onShowGift()
            return
        self.__raccoonManager.doLetterAction()

    def releaseLetterAction(self):
        self.__raccoonManager.releaseLetterAction()

    def setAnimationsEnabled(self, enabled):
        setNYSettings(NY_HAS_PET_ANIMATION, enabled)
        self.__animationsEnabled = enabled
        if not self.__animationsEnabled:
            self.__raccoonManager.clearQueue()

    def activateItem(self, name):
        if self.__animationsEnabled:
            self.__raccoonManager.addCommand(name)

    def updateMoodState(self, state):
        manager = self.__raccoonManager
        if manager:
            manager.setMoodState(_STATE_TO_MOOD[state])

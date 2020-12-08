# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_icicle_controller.py
import logging
import typing
from functools import partial
import BigWorld
import WWISE
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from constants import CURRENT_REALM
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.new_year import IIcicleController
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
from vehicle_systems.stricted_loading import makeCallbackWeak
if typing.TYPE_CHECKING:
    from NewYearIcicleObject import NewYearIcicleObject
    from NewYearIciclesIllumination import NewYearIciclesIllumination
_logger = logging.getLogger(__name__)
_CLICK_COOLDOWN = 1.9
_PUZZLE_DURATION = 8.0
_ILLUMINATIONS_SWITCH_INTERVAL = 0.1
_ILLUMINATIONS_DEACTIVATION_DELAY = 1.0
_SEQUENCE = (1, 3, 3, 1, 2, 1, 1, 3, 2)
_SEQUENCE_LENGTH = len(_SEQUENCE)
_ICICLES_COUNT = 3
_ILLUMINATIONS_COUNT = _SEQUENCE_LENGTH + 1
FINAL_ILLUMINATION_ID = _ILLUMINATIONS_COUNT

class IcicleClickStates(object):
    NONE = 0
    CORRECT = 1
    INCORRECT = 2
    COMPLETE = 3


class _SoundEvents(object):
    CORRECT = 'hangar_newyear_puzzle'
    INCORRECT = 'hangar_newyear_puzzle_error'
    COMPLETE = 'hangar_newyear_puzzle_complete'


class _SoundsStateGroup(object):
    GROUP = 'STATE_ext_hangar_newyear_place'
    ACTIVE = 'STATE_ext_hangar_newyear_place_puzzle'
    INACTIVE = 'STATE_ext_hangar_newyear_place_hangar'


class _SoundsSwitchGroup(object):
    GROUP = 'SWITCH_ext_newyear_puzzle_region'
    RU = 'SWITCH_ext_newyear_puzzle_region_ru'
    WORLD = 'SWITCH_ext_newyear_puzzle_region_ww'


class IcicleController(IIcicleController, CallbackDelayer):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__icicles = {}
        self.__illuminations = {}
        self.__puzzleStage = 0
        self.__isIciclesActive = True
        self.__isPuzzleActive = False
        self.__isPuzzleCompleted = False
        self.__soundStateChanged = False

    @property
    def isCompleted(self):
        return self.__isPuzzleCompleted

    @property
    def puzzleStage(self):
        return self.__puzzleStage

    @property
    def isPuzzleActive(self):
        return self.__isPuzzleActive

    def onAvatarBecomePlayer(self):
        self.__clear()
        super(IcicleController, self).onAvatarBecomePlayer()

    def onDisconnected(self):
        self.__clear()
        super(IcicleController, self).onDisconnected()

    def onLobbyStarted(self, *_, **__):
        self.__isIciclesActive = True
        self.__isPuzzleActive = False
        self.__isPuzzleCompleted = bool(self.__getNYIcicleCompletedSetting())
        g_eventBus.addListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.ViewEventType.LOAD_VIEW, self.__onLoadViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def init(self):
        super(IcicleController, self).init()
        switch = _SoundsSwitchGroup.RU if CURRENT_REALM == 'RU' else _SoundsSwitchGroup.WORLD
        WWISE.WW_setSwitch(_SoundsSwitchGroup.GROUP, switch)

    def fini(self):
        CallbackDelayer.destroy(self)
        g_eventBus.removeListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__onLoadViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        super(IcicleController, self).fini()

    def addIcicleEntity(self, icicleEntity):
        icicleID = icicleEntity.objectID
        if icicleID in self.__icicles:
            _logger.error('Duplicated Icicle [id=%s].', icicleID)
        else:
            self.__icicles[icicleID] = icicleEntity

    def removeIcicleEntity(self, icicleEntity):
        icicleID = icicleEntity.objectID
        if icicleID not in self.__icicles:
            _logger.error('Missed Icicle [id=%s].', icicleID)
        else:
            self.__icicles.pop(icicleID)

    def addIlluminationEntity(self, illuminationEntity):
        illuminationID = illuminationEntity.objectID
        if illuminationID in self.__illuminations:
            _logger.error("Duplicated Icicle's Illumination [id=%s].", illuminationID)
        else:
            self.__illuminations[illuminationID] = illuminationEntity

    def removeIlluminationEntity(self, illuminationEntity):
        illuminationID = illuminationEntity.objectID
        if illuminationID not in self.__illuminations:
            _logger.error("Missed Icicle's Illumination [id=%s].", illuminationID)
        else:
            self.__illuminations.pop(illuminationID)

    def handleIcicleClick(self, icicleID):
        if not self.__isIciclesActive:
            return IcicleClickStates.NONE
        if icicleID not in self.__icicles:
            _logger.error("Failed to handle Icicle's click [objectID=%s]. Missing Icicle.", icicleID)
        if _SEQUENCE[self.__puzzleStage] != icicleID:
            self.__processIncorrectClick(icicleID)
            return IcicleClickStates.INCORRECT
        self.__processCorrectClick(icicleID)
        if self.__puzzleStage == _SEQUENCE_LENGTH:
            self.__completePuzzle()
            return IcicleClickStates.COMPLETE
        return IcicleClickStates.CORRECT

    @classmethod
    def __getNYIcicleCompletedSetting(cls):
        settings = cls.__settingsCore.serverSettings.getNewYearStorage()
        return bool(settings.get(NewYearStorageKeys.IS_ICICLES_COMPLETED, False))

    @classmethod
    def __setNYIcicleCompletedSetting(cls, value):
        settings = {NewYearStorageKeys.IS_ICICLES_COMPLETED: value}
        cls.__settingsCore.serverSettings.saveInNewYearStorage(settings)

    def __processIncorrectClick(self, icicleID):
        self.__resetPuzzleStage()
        self.__setIciclesCooldown(icicleID)
        self.__startPuzzle()
        WWISE.WW_eventGlobal(_SoundEvents.INCORRECT)

    def __processCorrectClick(self, icicleID):
        self.__puzzleStage += 1
        self.__setIciclesCooldown(icicleID)
        self.__startPuzzle()
        self.__switchIllumination(self.__puzzleStage, activate=True)
        WWISE.WW_eventGlobal(_SoundEvents.CORRECT)

    def __completePuzzle(self):
        if not self.__isPuzzleCompleted:
            self.__isPuzzleCompleted = True
            self.__setNYIcicleCompletedSetting(value=True)
            self.__switchIllumination(FINAL_ILLUMINATION_ID, activate=True)
            WWISE.WW_eventGlobal(_SoundEvents.COMPLETE)
        BigWorld.callback(_ILLUMINATIONS_DEACTIVATION_DELAY, makeCallbackWeak(self.__resetPuzzleStage))

    def __setIciclesCooldown(self, icicleID):
        self.__isIciclesActive = False
        self.delayCallback(_CLICK_COOLDOWN, partial(self.__onIciclesCooldownOver, icicleID))

    def __onIciclesCooldownOver(self, icicleID):
        self.__isIciclesActive = True
        icicle = self.__icicles.get(icicleID)
        if icicle is not None:
            icicle.resetEffects()
        else:
            _logger.error('Missing Icicle [id=%s].', icicleID)
        for icicle in self.__icicles.itervalues():
            if icicle.isHighlighted:
                icicle.restoreHandCursor()

        return

    def __startPuzzle(self):
        self.delayCallback(_PUZZLE_DURATION, self.__stopPuzzle)
        self.__isPuzzleActive = True
        for icicle in self.__icicles.itervalues():
            icicle.resetEffects()

        WWISE.WW_setState(_SoundsStateGroup.GROUP, _SoundsStateGroup.ACTIVE)
        self.__setSoundStateChanged(value=False)

    def __stopPuzzle(self):
        self.__isPuzzleActive = False
        for icicle in self.__icicles.itervalues():
            icicle.resetEffects()

        if not self.__soundStateChanged:
            WWISE.WW_setState(_SoundsStateGroup.GROUP, _SoundsStateGroup.INACTIVE)

    def __resetPuzzleStage(self):
        self.__deactivateIlluminations()
        self.__puzzleStage = 0
        for icicle in self.__icicles.itervalues():
            icicle.resetEffects()

    def __deactivateIlluminations(self, interval=_ILLUMINATIONS_SWITCH_INTERVAL):
        illuminationIDs = range(self.__puzzleStage, 0, -1)
        if interval:
            self.delayCallback(0.0, partial(self.__deactivateIlluminationsCallback, illuminationIDs, interval))
        else:
            for illuminationID in illuminationIDs:
                self.__switchIllumination(illuminationID, activate=False)

    def __deactivateIlluminationsCallback(self, illuminationIDs, interval):
        if not illuminationIDs:
            return None
        else:
            illuminationID = illuminationIDs.pop(0)
            self.__switchIllumination(illuminationID, activate=False)
            return interval

    def __switchIllumination(self, illuminationID, activate):
        illumination = self.__illuminations.get(illuminationID)
        if illumination is None:
            _logger.error("Missing Icicle's Illumination Entity [objectID=%s]", illuminationID)
            return
        else:
            if activate:
                illumination.activate()
            else:
                illumination.deactivate()
            return

    def __onPreSwitchViewEvent(self, _):
        self.__setSoundStateChanged(value=True)

    def __onLoadViewEvent(self, event):
        if event.alias == VIEW_ALIAS.NY_MAIN_VIEW:
            self.__setSoundStateChanged(value=True)

    def __setSoundStateChanged(self, value):
        self.__soundStateChanged = value

    def __clear(self):
        self.clearCallbacks()
        self.__icicles.clear()
        self.__illuminations.clear()
        self.__puzzleStage = 0

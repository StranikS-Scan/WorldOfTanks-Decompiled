# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/sound_interactive_controller.py
import BigWorld
import SoundGroups
import Event
import sound_constants
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from TeamBaseRecapturable import ITeamBasesRecapturableListener
_UPDATE_TIMER_INTERVAL = 1
_TIME_EVENT_LATS_TWO_MINUTES = 124
_TIME_EVENT_NO_ACTION = 20

class SoundInteractiveController(CallbackDelayer, ITeamBasesRecapturableListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SoundInteractiveController, self).__init__()
        self.__finishTime = 0
        self.__eventLastTwoMinutes = False
        self.__noActionStartTime = -1
        self.onBattleEndWarningSound = Event.Event()
        if self._teamBaseController:
            self._teamBaseController.registerListener(self)
        player = BigWorld.player()
        if player is not None:
            if player.arena.period == ARENA_PERIOD.BATTLE:
                self.__startBattleEvent(player.arena.periodEndTime)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        return

    def finalize(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        CallbackDelayer.destroy(self)

    def onBaseCaptured(self, baseId, newTeam):
        for teamBase in self._teamBaseController.teamBases.values():
            if teamBase.team != newTeam or newTeam == 0:
                return

        self.__startSoundEvent(sound_constants.INTERACTIVE_EVENT_2_BASES_CAPTURED)

    def onVehicleBeingAttacked(self, victimID, attackerID, newHealth):
        player = BigWorld.player()
        isAvatarVehicleDestroyed = victimID == player.playerVehicleID
        if newHealth <= 0 and isAvatarVehicleDestroyed:
            self.__startExplorationSoundEvent()
            return
        elif attackerID <= 0 or attackerID == victimID:
            return
        else:
            victim = BigWorld.entities.get(victimID)
            attacker = BigWorld.entities.get(attackerID)
            if victim is not None and attacker is not None and victim.publicInfo.team == attacker.publicInfo.team:
                return
            if victimID == player.playerVehicleID or attackerID == player.playerVehicleID:
                self.__startFightSoundEvent()
            return

    @property
    def _teamBaseController(self):
        return self._sessionProvider.dynamic.teamBaseRecapturable

    def __onArenaPeriodChange(self, period, endTime, length, additionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__startBattleEvent(endTime)

    def __updateTimer(self):
        timeLeft = self.__finishTime - BigWorld.serverTime()
        if timeLeft > 0:
            self.delayCallback(_UPDATE_TIMER_INTERVAL, self.__updateTimer)
            if timeLeft <= _TIME_EVENT_LATS_TWO_MINUTES and not self.__eventLastTwoMinutes:
                self.__eventLastTwoMinutes = True
                self.__startSoundEvent(sound_constants.INTERACTIVE_EVENT_2_MINUTES_REMAIN)
                self.onBattleEndWarningSound()
        if self.__noActionStartTime > 0:
            eventNoActionTime = BigWorld.serverTime() - self.__noActionStartTime
            if eventNoActionTime >= _TIME_EVENT_NO_ACTION:
                self.__startExplorationSoundEvent()

    def __startFightSoundEvent(self):
        if self.__eventLastTwoMinutes:
            return
        self.__startSoundEvent(sound_constants.INTERACTIVE_EVENT_FIGHT)
        self.__beginRegisteringNoAction()

    def __startExplorationSoundEvent(self):
        if not self.__eventLastTwoMinutes:
            self.__startSoundEvent(sound_constants.INTERACTIVE_EVENT_EXPLORATION)
        self.__noActionStartTime = -1

    def __startBattleEvent(self, endTime):
        self.__startSoundEvent(sound_constants.INTERACTIVE_EVENT_START_BATTLE)
        self.__finishTime = endTime
        self.__updateTimer()
        self.__beginRegisteringNoAction()

    def __beginRegisteringNoAction(self):
        self.__noActionStartTime = BigWorld.serverTime()

    def __startSoundEvent(self, eventName):
        SoundGroups.g_instance.playSound2D(eventName)

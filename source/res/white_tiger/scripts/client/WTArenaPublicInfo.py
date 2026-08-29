# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTArenaPublicInfo.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers.CallbackDelayer import CallbackDelayer
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from cgf_components import sound_helpers
from white_tiger_common.wt_constants import WT_COMPONENT_NAMES, WT_TEAMS, WT_COMPONENT_CONSTANTS

class WTArenaPublicInfo(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __DEBUFF_TIMER_TICK_LENGTH_SECONDS = 1
    __PLAYER_HUNTER_GENERATOR_DESTROYED = 'wt23_hunters_vo_shield_destroyed'
    __PLAYER_HUNTER_LAST_GENERATOR_DESTROYED = 'wt23_hunters_vo_last_generator_destroyed'
    __PLAYER_BOSS_GENERATOR_DESTROYED = 'wt23_w_vo_shield_destroyed'
    __PLAYER_BOSS_LAST_GENERATOR_DESTROYED = 'wt23_w_vo_last_generator_destroyed'
    __GENERATORS_VOICEOVERS = {'generator': {WT_TEAMS.HUNTERS_TEAM: __PLAYER_HUNTER_GENERATOR_DESTROYED,
                   WT_TEAMS.BOSS_TEAM: __PLAYER_BOSS_GENERATOR_DESTROYED},
     'lastGenerator': {WT_TEAMS.HUNTERS_TEAM: __PLAYER_HUNTER_LAST_GENERATOR_DESTROYED,
                       WT_TEAMS.BOSS_TEAM: __PLAYER_BOSS_LAST_GENERATOR_DESTROYED}}

    def __init__(self):
        super(WTArenaPublicInfo, self).__init__()
        self.__cd = CallbackDelayer()
        self.__previousRemainingTime = 0

    def onDestroy(self):
        self.__cd.destroy()
        self.__cd = None
        super(WTArenaPublicInfo, self).onDestroy()
        return

    def set_generatorCounter(self, prev):
        if self.generatorCounter == prev:
            return
        else:
            ctrl = self.entity.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onPublicCounter(self.generatorCounter, self.generatorMax, WT_COMPONENT_NAMES.GENERATORS_COUNTER)
            if self.generatorCounter < prev:
                isLastGenerator = 'lastGenerator' if self.generatorCounter == 0 else 'generator'
                soundNotification = self.__GENERATORS_VOICEOVERS[isLastGenerator][BigWorld.player().team]
                sound_helpers.playNotification(soundNotification)
            return

    def set_bossDebuffFinishTime(self, prev):
        if self.__sessionProvider.isReplayPlaying:
            return
        if self.bossDebuffFinishTime != prev:
            remainingTime = self.__getRemainDebuffTime() if self.bossDebuffFinishTime else 0
            if self.bossDebuffFinishTime:
                self.__cd.delayCallback(self.__DEBUFF_TIMER_TICK_LENGTH_SECONDS, self.__tick)
            else:
                self.__previousRemainingTime = 0
            self.__notifyUIAboutDebuffTimer(remainingTime)

    def set_hyperionCharge(self, prev):
        if self.hyperionCharge != prev:
            ctrl = self.entity.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onPublicCounter(self.hyperionCharge, WT_COMPONENT_CONSTANTS.HYPERION_MAX_CHARGE, WT_COMPONENT_NAMES.HYPERION_COUNTER)
        return

    def _onAvatarReady(self):
        self.set_bossDebuffFinishTime(0)
        self.set_hyperionCharge(0)

    def __tick(self):
        remainingTime = self.__getRemainDebuffTime()
        if remainingTime == self.__previousRemainingTime:
            return None
        else:
            self.__notifyUIAboutDebuffTimer(remainingTime)
            self.__previousRemainingTime = remainingTime
            return self.__DEBUFF_TIMER_TICK_LENGTH_SECONDS

    def __notifyUIAboutDebuffTimer(self, remainTime):
        ctrl = self.entity.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onArenaTimer(WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER, max(0, remainTime))
        return

    def __getRemainDebuffTime(self):
        return max(0, self.bossDebuffFinishTime - BigWorld.serverTime())

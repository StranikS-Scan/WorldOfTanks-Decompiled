# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/battle_timer.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer
from gui.battle_control import avatar_getter
from gui.sounds.r4_sound_constants import R4_SOUND

class R4BattleTimer(BattleTimer):

    def __init__(self):
        super(R4BattleTimer, self).__init__()
        arenaType = self.sessionProvider.arenaVisitor.type
        self.__appearTime = arenaType.getBattleEndWarningAppearTime()

    def setTotalTime(self, totalTime):
        super(R4BattleTimer, self).setTotalTime(totalTime)
        if totalTime == self.__appearTime:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'playOnHeadVehicle'):
                soundNotifications.playOnHeadVehicle(R4_SOUND.R4_TIME_WARNING)

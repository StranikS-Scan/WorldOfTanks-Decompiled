# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: wt/scripts/client/OvertimeManagerComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
import BigWorld
BOSS_TEAM = 1

class OvertimeManagerComponent(DynamicScriptComponent):
    _WT23_OVERTIME_HUNTER_SOUND_NOTIFICATION = 'wt23_hunters_vo_overtime'
    _WT23_OVERTIME_BOSS_SOUND_NOTIFICATION = 'wt23_w_vo_overtime'

    def set_overtimeDuration(self, _=None):
        feedback = self.entity.sessionProvider.shared.feedback
        if feedback:
            feedback.onOvertime(self.overtimeDuration)
        if self.overtimeDuration > 0:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'play'):
                if getattr(BigWorld.player(), 'team', 0) == BOSS_TEAM:
                    soundNotifications.play(self._WT23_OVERTIME_BOSS_SOUND_NOTIFICATION)
                else:
                    soundNotifications.play(self._WT23_OVERTIME_HUNTER_SOUND_NOTIFICATION)

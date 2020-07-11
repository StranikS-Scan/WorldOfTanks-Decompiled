# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_4.py
import BigWorld
from bootcamp.scenery.AbstractMission import AbstractMission

class Mission4(AbstractMission):
    _combatMusicDelayTime = 3.0

    def __init__(self, assistant):
        self._combatMusicTriggered = False
        self._callbackID = None
        super(Mission4, self).__init__(assistant)
        return

    def start(self):
        super(Mission4, self).start()
        self.playSound2D('vo_bc_main_task')
        self.playSound2D('bc_main_tips_task_start')
        self.muteSounds(('crew_member_contusion', 'track_destroyed', 'fire_started', 'gunner_killed'))

    def onEnemyObserved(self, isObserved):
        if not self._combatMusicTriggered and self._callbackID is None:
            self._combatMusicTriggered = True
            self._callbackID = BigWorld.callback(self._combatMusicDelayTime, self._playCombatMusic)
        return

    def stop(self):
        self.muteSounds(())
        if self._callbackID:
            BigWorld.cancelCallback(self._callbackID)
            self._callbackID = None
        super(Mission4, self).stop()
        return

    def _playCombatMusic(self):
        super(Mission4, self)._playCombatMusic()
        self._callbackID = None
        return

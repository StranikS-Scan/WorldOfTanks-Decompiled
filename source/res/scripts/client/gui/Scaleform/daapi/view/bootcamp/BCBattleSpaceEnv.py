# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattleSpaceEnv.py
from gui.sounds.ambients import BattleSpaceEnv, NoMusic

class BCBattleSpaceEnv(BattleSpaceEnv):

    def stop(self):
        self._music = NoMusic()
        self._onChanged()
        super(BCBattleSpaceEnv, self).stop()

    def _setAfterBattleAmbient(self):
        pass

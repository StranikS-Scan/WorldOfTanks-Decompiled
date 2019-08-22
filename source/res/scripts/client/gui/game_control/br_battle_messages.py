# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/br_battle_messages.py
from helpers import dependency, int2roman
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from skeletons.gui.battle_session import IBattleSessionProvider

class ProgressionMessagesPlayer(IProgressionListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setLevel(self, level, *args):
        if level == 1:
            return
        else:
            ctrl = self._sessionProvider.shared.messages
            if ctrl is not None:
                ctrl.onShowPlayerMessageByKey('VEHICLE_LEVEL_UP', {'level': int2roman(level)})
            return

    def onMaxLvlAchieved(self):
        ctrl = self._sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowPlayerMessageByKey('VEHICLE_LEVEL_MAXED')
        return

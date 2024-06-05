# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/countdown.py
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.base_models import TextClientModel

class CountdownClientModel(TextClientModel):
    __slots__ = ('header', 'subheader', 'battleStartMessage')

    def __init__(self, header, subheader, battleStartMessage):
        super(CountdownClientModel, self).__init__()
        self.header = header
        self.subheader = subheader
        self.battleStartMessage = battleStartMessage

    def getHeader(self):
        return self._getText(self.header)

    def getSubheader(self):
        return self._getText(self.subheader)

    def getBattleStartMessage(self):
        return self._getText(self.battleStartMessage)

    def __repr__(self):
        return '<CountdownClientModel>: header=%s, subheader=%s, battleStartMessage=%s' % (self.header, self.subheader, self.battleStartMessage)

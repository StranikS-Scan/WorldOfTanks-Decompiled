# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/countdown.py


class CountdownClientModel(object):
    __slots__ = ('header', 'subheader', 'battleStartMessage')

    def __init__(self, header, subheader, battleStartMessage):
        super(CountdownClientModel, self).__init__()
        self.header = header
        self.subheader = subheader
        self.battleStartMessage = battleStartMessage

    def __repr__(self):
        return '<CountdownClientModel>: header=%s, subheader=%s, battleStartMessage=%s' % (self.header, self.subheader, self.battleStartMessage)

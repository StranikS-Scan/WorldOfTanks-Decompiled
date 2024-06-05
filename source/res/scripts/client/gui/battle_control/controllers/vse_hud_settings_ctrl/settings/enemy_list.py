# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/enemy_list.py
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.base_models import BaseClientModel

class EnemyListClientModel(BaseClientModel):
    __slots__ = ('showSpottedIcon', 'highlightElite')

    def __init__(self, showSpottedIcon, highlightElite):
        super(EnemyListClientModel, self).__init__()
        self.showSpottedIcon = showSpottedIcon
        self.highlightElite = highlightElite

    def __repr__(self):
        return '<EnemyListClientModel>: showSpottedIcon=%s, highlightElite=%s' % (self.showSpottedIcon, self.highlightElite)

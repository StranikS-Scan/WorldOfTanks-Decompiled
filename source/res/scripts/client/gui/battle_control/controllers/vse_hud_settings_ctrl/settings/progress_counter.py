# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/progress_counter.py
import typing
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.base_models import TextClientModel

class ProgressCounterClientModel(TextClientModel):
    __slots__ = ('id', 'header', 'icon')

    def __init__(self, id, header, icon):
        super(ProgressCounterClientModel, self).__init__()
        self.id = id
        self.header = header
        self.icon = icon

    def getHeader(self, params):
        return self._getPluralText(self.header, params)

    def __repr__(self):
        return '<ProgressCounterClientModel>: id=%s, header=%s, icon=%s' % (self.id, self.header, self.icon)

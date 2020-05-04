# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_about_model.py
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel

class ActionAboutModel(ActionMenuModel):
    __slots__ = ('onGotoExternalVideo',)

    def __init__(self, properties=5, commands=4):
        super(ActionAboutModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getString(4)

    def setEndDate(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(ActionAboutModel, self)._initialize()
        self._addStringProperty('endDate', '')
        self.onGotoExternalVideo = self._addCommand('onGotoExternalVideo')

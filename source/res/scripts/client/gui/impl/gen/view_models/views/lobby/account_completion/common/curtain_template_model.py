# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/curtain_template_model.py
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_dialog_model import BaseDialogModel

class CurtainTemplateModel(BaseDialogModel):
    __slots__ = ('onMoveSpace',)
    SERVER_UNAVAILABLE = 'SERVER_UNAVAILABLE'
    MESSAGE = 'MESSAGE'
    NOTHING = ''

    def __init__(self, properties=8, commands=3):
        super(CurtainTemplateModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getEmail(self):
        return self._getString(4)

    def setEmail(self, value):
        self._setString(4, value)

    def getIsShow(self):
        return self._getBool(5)

    def setIsShow(self, value):
        self._setBool(5, value)

    def getIsFade(self):
        return self._getBool(6)

    def setIsFade(self, value):
        self._setBool(6, value)

    def getIsWaiting(self):
        return self._getBool(7)

    def setIsWaiting(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(CurtainTemplateModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('email', '')
        self._addBoolProperty('isShow', False)
        self._addBoolProperty('isFade', False)
        self._addBoolProperty('isWaiting', False)
        self.onMoveSpace = self._addCommand('onMoveSpace')

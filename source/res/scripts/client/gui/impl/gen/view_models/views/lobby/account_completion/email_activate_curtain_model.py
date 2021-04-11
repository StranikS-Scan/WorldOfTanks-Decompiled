# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/email_activate_curtain_model.py
from gui.impl.gen.view_models.views.lobby.account_completion.common.curtain_template_model import CurtainTemplateModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_separate_model import FieldSeparateModel

class EmailActivateCurtainModel(CurtainTemplateModel):
    __slots__ = ('onResendClicked',)

    def __init__(self, properties=11, commands=4):
        super(EmailActivateCurtainModel, self).__init__(properties=properties, commands=commands)

    @property
    def field(self):
        return self._getViewModel(8)

    def getTimer(self):
        return self._getNumber(9)

    def setTimer(self, value):
        self._setNumber(9, value)

    def getIsShowAccept(self):
        return self._getBool(10)

    def setIsShowAccept(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(EmailActivateCurtainModel, self)._initialize()
        self._addViewModelProperty('field', FieldSeparateModel())
        self._addNumberProperty('timer', 0)
        self._addBoolProperty('isShowAccept', False)
        self.onResendClicked = self._addCommand('onResendClicked')

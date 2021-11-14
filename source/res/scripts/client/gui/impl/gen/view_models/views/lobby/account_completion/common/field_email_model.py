# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/field_email_model.py
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_field_model import BaseFieldModel

class FieldEmailModel(BaseFieldModel):
    __slots__ = ('onErrorTimer',)
    EMAIL_LEN_MAX = 50
    EMAIL_LEN_MIN = 4

    def __init__(self, properties=5, commands=3):
        super(FieldEmailModel, self).__init__(properties=properties, commands=commands)

    def getErrorTime(self):
        return self._getNumber(4)

    def setErrorTime(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(FieldEmailModel, self)._initialize()
        self._addNumberProperty('errorTime', 0)
        self.onErrorTimer = self._addCommand('onErrorTimer')

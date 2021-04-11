# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/email_confirmation_curtain_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.account_completion.common.curtain_template_model import CurtainTemplateModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_model import FieldModel

class EmailConfirmationCurtainModel(CurtainTemplateModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=3):
        super(EmailConfirmationCurtainModel, self).__init__(properties=properties, commands=commands)

    @property
    def field(self):
        return self._getViewModel(8)

    def getQuestID(self):
        return self._getString(9)

    def setQuestID(self, value):
        self._setString(9, value)

    def getBonuses(self):
        return self._getArray(10)

    def setBonuses(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(EmailConfirmationCurtainModel, self)._initialize()
        self._addViewModelProperty('field', FieldModel())
        self._addStringProperty('questID', '')
        self._addArrayProperty('bonuses', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/add_credentials_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_wgnp_overlay_view_model import BaseWgnpOverlayViewModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_email_model import FieldEmailModel

class AddCredentialsModel(BaseWgnpOverlayViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=4):
        super(AddCredentialsModel, self).__init__(properties=properties, commands=commands)

    @property
    def email(self):
        return self._getViewModel(9)

    @staticmethod
    def getEmailType():
        return FieldEmailModel

    def getQuestID(self):
        return self._getString(10)

    def setQuestID(self, value):
        self._setString(10, value)

    def getBonuses(self):
        return self._getArray(11)

    def setBonuses(self, value):
        self._setArray(11, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def getRewardsTitle(self):
        return self._getResource(12)

    def setRewardsTitle(self, value):
        self._setResource(12, value)

    def _initialize(self):
        super(AddCredentialsModel, self)._initialize()
        self._addViewModelProperty('email', FieldEmailModel())
        self._addStringProperty('questID', '')
        self._addArrayProperty('bonuses', Array())
        self._addResourceProperty('rewardsTitle', R.invalid())

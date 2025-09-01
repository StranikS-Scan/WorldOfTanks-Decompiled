# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/campaign_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel

class CampaignModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CampaignModel, self).__init__(properties=properties, commands=commands)

    def getOperations(self):
        return self._getArray(0)

    def setOperations(self, value):
        self._setArray(0, value)

    @staticmethod
    def getOperationsType():
        return SelectOperationModel

    def getCampaignName(self):
        return self._getString(1)

    def setCampaignName(self, value):
        self._setString(1, value)

    def getCompletedWithHonor(self):
        return self._getBool(2)

    def setCompletedWithHonor(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CampaignModel, self)._initialize()
        self._addArrayProperty('operations', Array())
        self._addStringProperty('campaignName', '')
        self._addBoolProperty('completedWithHonor', False)

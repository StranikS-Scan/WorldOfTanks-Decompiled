# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pm_announce/tooltips/personal_missions_old_campaign_tooltip_operations_model.py
from frameworks.wulf import ViewModel

class PersonalMissionsOldCampaignTooltipOperationsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PersonalMissionsOldCampaignTooltipOperationsModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCompleted(self):
        return self._getNumber(1)

    def setCompleted(self, value):
        self._setNumber(1, value)

    def getAll(self):
        return self._getNumber(2)

    def setAll(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PersonalMissionsOldCampaignTooltipOperationsModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('completed', 0)
        self._addNumberProperty('all', 0)

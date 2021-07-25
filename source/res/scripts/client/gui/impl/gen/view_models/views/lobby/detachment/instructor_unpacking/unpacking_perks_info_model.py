# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_unpacking/unpacking_perks_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_unpacking.unpacking_perk_model import UnpackingPerkModel

class UnpackingPerksInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(UnpackingPerksInfoModel, self).__init__(properties=properties, commands=commands)

    def getSelectedTab(self):
        return self._getString(0)

    def setSelectedTab(self, value):
        self._setString(0, value)

    def getProfessions(self):
        return self._getArray(1)

    def setProfessions(self, value):
        self._setArray(1, value)

    def getPerksList(self):
        return self._getArray(2)

    def setPerksList(self, value):
        self._setArray(2, value)

    def getSelectedPerk(self):
        return self._getNumber(3)

    def setSelectedPerk(self, value):
        self._setNumber(3, value)

    def getSteps(self):
        return self._getNumber(4)

    def setSteps(self, value):
        self._setNumber(4, value)

    def getCurrentStep(self):
        return self._getNumber(5)

    def setCurrentStep(self, value):
        self._setNumber(5, value)

    def getMainPoints(self):
        return self._getNumber(6)

    def setMainPoints(self, value):
        self._setNumber(6, value)

    def getOvercapPoints(self):
        return self._getNumber(7)

    def setOvercapPoints(self, value):
        self._setNumber(7, value)

    def getBreakPoints(self):
        return self._getNumber(8)

    def setBreakPoints(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(UnpackingPerksInfoModel, self)._initialize()
        self._addStringProperty('selectedTab', '')
        self._addArrayProperty('professions', Array())
        self._addArrayProperty('perksList', Array())
        self._addNumberProperty('selectedPerk', 0)
        self._addNumberProperty('steps', 0)
        self._addNumberProperty('currentStep', 0)
        self._addNumberProperty('mainPoints', 0)
        self._addNumberProperty('overcapPoints', 0)
        self._addNumberProperty('breakPoints', 0)

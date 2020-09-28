# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_vehicle_params_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtEventVehicleParamsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WtEventVehicleParamsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsSkill(self):
        return self._getBool(0)

    def setIsSkill(self, value):
        self._setBool(0, value)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getText(self):
        return self._getString(4)

    def setText(self, value):
        self._setString(4, value)

    def getSkillTitle(self):
        return self._getString(5)

    def setSkillTitle(self, value):
        self._setString(5, value)

    def getSkillDescription(self):
        return self._getString(6)

    def setSkillDescription(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(WtEventVehicleParamsTooltipViewModel, self)._initialize()
        self._addBoolProperty('isSkill', False)
        self._addStringProperty('id', '')
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('title', '')
        self._addStringProperty('text', '')
        self._addStringProperty('skillTitle', '')
        self._addStringProperty('skillDescription', '')

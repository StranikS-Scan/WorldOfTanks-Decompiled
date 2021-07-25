# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/instructor_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_model import CommanderModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.instructor_info_tooltip_model import InstructorInfoTooltipModel

class InstructorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(InstructorTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def information(self):
        return self._getViewModel(0)

    @property
    def commander(self):
        return self._getViewModel(1)

    @property
    def vehicle(self):
        return self._getViewModel(2)

    def getShownPage(self):
        return self._getString(3)

    def setShownPage(self, value):
        self._setString(3, value)

    def getDetachmentNation(self):
        return self._getString(4)

    def setDetachmentNation(self, value):
        self._setString(4, value)

    def getIsTokenNationsUnsuitable(self):
        return self._getBool(5)

    def setIsTokenNationsUnsuitable(self, value):
        self._setBool(5, value)

    def getIsWrongLeader(self):
        return self._getBool(6)

    def setIsWrongLeader(self, value):
        self._setBool(6, value)

    def getLeaderName(self):
        return self._getString(7)

    def setLeaderName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(InstructorTooltipModel, self)._initialize()
        self._addViewModelProperty('information', InstructorInfoTooltipModel())
        self._addViewModelProperty('commander', CommanderModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addStringProperty('shownPage', 'common')
        self._addStringProperty('detachmentNation', '')
        self._addBoolProperty('isTokenNationsUnsuitable', False)
        self._addBoolProperty('isWrongLeader', False)
        self._addStringProperty('leaderName', '')

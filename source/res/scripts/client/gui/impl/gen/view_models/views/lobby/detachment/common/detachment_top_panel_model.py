# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_top_panel_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_model import CommanderModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_info_animated_model import DetachmentInfoAnimatedModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel

class DetachmentTopPanelModel(CommanderModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(DetachmentTopPanelModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(6)

    @property
    def roseModel(self):
        return self._getViewModel(7)

    def getPointsAvailable(self):
        return self._getNumber(8)

    def setPointsAvailable(self, value):
        self._setNumber(8, value)

    def getVehicleType(self):
        return self._getString(9)

    def setVehicleType(self, value):
        self._setString(9, value)

    def getRankIcon(self):
        return self._getResource(10)

    def setRankIcon(self, value):
        self._setResource(10, value)

    def getInBarracks(self):
        return self._getBool(11)

    def setInBarracks(self, value):
        self._setBool(11, value)

    def getMasteryLevel(self):
        return self._getResource(12)

    def setMasteryLevel(self, value):
        self._setResource(12, value)

    def _initialize(self):
        super(DetachmentTopPanelModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentInfoAnimatedModel())
        self._addViewModelProperty('roseModel', RoseModel())
        self._addNumberProperty('pointsAvailable', 0)
        self._addStringProperty('vehicleType', '')
        self._addResourceProperty('rankIcon', R.invalid())
        self._addBoolProperty('inBarracks', False)
        self._addResourceProperty('masteryLevel', R.invalid())

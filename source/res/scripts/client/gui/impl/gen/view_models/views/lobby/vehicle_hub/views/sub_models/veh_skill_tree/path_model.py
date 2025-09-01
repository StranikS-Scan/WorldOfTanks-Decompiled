# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/path_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class LineType(Enum):
    LEFTTORIGHT = 'leftToRight'
    RIGHTTOLEFT = 'rightToLeft'
    TOPTOBOTTOM = 'topToBottom'
    BOTTOMTOTOP = 'bottomToTop'
    LEFTTOBOTTOM = 'leftToBottom'
    BOTTOMTOLEFT = 'bottomToLeft'
    LEFTTOTOP = 'leftToTop'
    TOPTOLEFT = 'topToLeft'
    TOPTORIGHT = 'topToRight'
    RIGHTTOTOP = 'rightToTop'
    RIGHTTOBOTTOM = 'rightToBottom'
    BOTTOMTORIGHT = 'bottomToRight'


class PathModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PathModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getLineType(self):
        return LineType(self._getString(1))

    def setLineType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(PathModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('lineType')

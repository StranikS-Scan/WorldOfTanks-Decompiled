# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/entry_point_cgf_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EntryPointCgfTooltipState(Enum):
    QUESTGIVER = 'questGiver'
    POSTOFFICE = 'postOffice'
    GOLDWAGON = 'goldWagon'
    ONPAUSE = 'onPause'


class EntryPointCgfTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EntryPointCgfTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCgfEntryPoint(self):
        return self._getString(0)

    def setCgfEntryPoint(self, value):
        self._setString(0, value)

    def getIsPaused(self):
        return self._getBool(1)

    def setIsPaused(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EntryPointCgfTooltipModel, self)._initialize()
        self._addStringProperty('cgfEntryPoint', '')
        self._addBoolProperty('isPaused', False)

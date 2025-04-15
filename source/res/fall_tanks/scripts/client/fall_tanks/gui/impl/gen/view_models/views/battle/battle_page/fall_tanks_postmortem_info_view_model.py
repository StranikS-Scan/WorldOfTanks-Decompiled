# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/gen/view_models/views/battle/battle_page/fall_tanks_postmortem_info_view_model.py
from frameworks.wulf import ViewModel

class FallTanksPostmortemInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FallTanksPostmortemInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFinished(self):
        return self._getBool(0)

    def setIsFinished(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(FallTanksPostmortemInfoViewModel, self)._initialize()
        self._addBoolProperty('isFinished', False)

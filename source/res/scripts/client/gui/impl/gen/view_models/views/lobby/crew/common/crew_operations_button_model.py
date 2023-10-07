# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_operations_button_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.button_model import ButtonModel

class CrewOperationsButtonModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CrewOperationsButtonModel, self).__init__(properties=properties, commands=commands)

    def getIsAutoReturnOn(self):
        return self._getBool(1)

    def setIsAutoReturnOn(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(CrewOperationsButtonModel, self)._initialize()
        self._addBoolProperty('isAutoReturnOn', False)

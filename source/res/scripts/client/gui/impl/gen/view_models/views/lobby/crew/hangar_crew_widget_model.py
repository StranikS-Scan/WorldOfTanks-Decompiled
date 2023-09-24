# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/hangar_crew_widget_model.py
from frameworks.wulf import ViewModel

class HangarCrewWidgetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(HangarCrewWidgetModel, self).__init__(properties=properties, commands=commands)

    def getSyncInitiator(self):
        return self._getNumber(0)

    def setSyncInitiator(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(HangarCrewWidgetModel, self)._initialize()
        self._addNumberProperty('syncInitiator', 0)

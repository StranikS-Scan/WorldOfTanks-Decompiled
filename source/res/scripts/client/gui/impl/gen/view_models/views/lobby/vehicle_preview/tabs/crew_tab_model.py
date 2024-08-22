# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/tabs/crew_tab_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.tabs.tankman_preview_model import TankmanPreviewModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.tabs.title_model import TitleModel

class CrewTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CrewTabModel, self).__init__(properties=properties, commands=commands)

    @property
    def headerModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getHeaderModelType():
        return TitleModel

    def getIsLockedCrew(self):
        return self._getBool(1)

    def setIsLockedCrew(self, value):
        self._setBool(1, value)

    def getHasDog(self):
        return self._getBool(2)

    def setHasDog(self, value):
        self._setBool(2, value)

    def getNation(self):
        return self._getString(3)

    def setNation(self, value):
        self._setString(3, value)

    def getTankmen(self):
        return self._getArray(4)

    def setTankmen(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTankmenType():
        return TankmanPreviewModel

    def _initialize(self):
        super(CrewTabModel, self)._initialize()
        self._addViewModelProperty('headerModel', TitleModel())
        self._addBoolProperty('isLockedCrew', False)
        self._addBoolProperty('hasDog', False)
        self._addStringProperty('nation', '')
        self._addArrayProperty('tankmen', Array())

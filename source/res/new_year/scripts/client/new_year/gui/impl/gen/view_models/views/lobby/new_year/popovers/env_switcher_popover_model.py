# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/popovers/env_switcher_popover_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.environment_switcher import EnvironmentSwitcher

class EnvSwitcherPopoverModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EnvSwitcherPopoverModel, self).__init__(properties=properties, commands=commands)

    @property
    def switcherComponent(self):
        return self._getViewModel(0)

    @staticmethod
    def getSwitcherComponentType():
        return EnvironmentSwitcher

    def getIsInHangar(self):
        return self._getBool(1)

    def setIsInHangar(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EnvSwitcherPopoverModel, self)._initialize()
        self._addViewModelProperty('switcherComponent', EnvironmentSwitcher())
        self._addBoolProperty('isInHangar', False)

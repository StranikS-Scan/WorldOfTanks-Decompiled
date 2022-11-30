# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_main_menu_tab_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel

class NyMainMenuTabModel(NewYearTabModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyMainMenuTabModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(6)

    def setIsEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyMainMenuTabModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)

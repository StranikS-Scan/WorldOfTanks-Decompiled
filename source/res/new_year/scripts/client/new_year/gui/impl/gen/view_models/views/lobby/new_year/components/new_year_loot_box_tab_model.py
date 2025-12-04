# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_loot_box_tab_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel

class NewYearLootBoxTabModel(NewYearTabModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NewYearLootBoxTabModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NewYearLootBoxTabModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)

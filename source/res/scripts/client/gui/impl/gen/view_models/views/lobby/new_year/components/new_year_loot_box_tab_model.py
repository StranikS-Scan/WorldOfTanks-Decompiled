# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_loot_box_tab_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel

class NewYearLootBoxTabModel(NewYearTabModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NewYearLootBoxTabModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(4)

    def setIsEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NewYearLootBoxTabModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)

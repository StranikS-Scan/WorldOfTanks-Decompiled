# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_bonus_header_model.py
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_bonus_info_model import NewYearBonusInfoModel

class NewYearBonusHeaderModel(NewYearBonusInfoModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearBonusHeaderModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearBonusHeaderModel, self)._initialize()
        self._addStringProperty('description', '')

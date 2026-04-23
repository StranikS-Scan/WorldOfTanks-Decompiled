# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_seasons_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_seasons_item_model import CustomizationSeasonsItemModel

class CustomizationSeasonsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CustomizationSeasonsModel, self).__init__(properties=properties, commands=commands)

    def getSeasonsList(self):
        return self._getArray(0)

    def setSeasonsList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSeasonsListType():
        return CustomizationSeasonsItemModel

    def _initialize(self):
        super(CustomizationSeasonsModel, self)._initialize()
        self._addArrayProperty('seasonsList', Array())

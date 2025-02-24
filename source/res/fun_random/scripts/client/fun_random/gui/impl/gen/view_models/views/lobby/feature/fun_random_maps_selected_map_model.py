# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_maps_selected_map_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_modifier import FunRandomMapsModifier

class FunRandomMapsSelectedMapModel(ViewModel):
    __slots__ = ()
    MINIMAP_SIZE_DEFAULT = 570
    MINIMAP_SIZE_SMALL = 332

    def __init__(self, properties=5, commands=0):
        super(FunRandomMapsSelectedMapModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getImage(self):
        return self._getResource(2)

    def setImage(self, value):
        self._setResource(2, value)

    def getModifiers(self):
        return self._getArray(3)

    def setModifiers(self, value):
        self._setArray(3, value)

    @staticmethod
    def getModifiersType():
        return FunRandomMapsModifier

    def getPoints(self):
        return self._getArray(4)

    def setPoints(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPointsType():
        return FunRandomMapsModifier

    def _initialize(self):
        super(FunRandomMapsSelectedMapModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('title', '')
        self._addResourceProperty('image', R.invalid())
        self._addArrayProperty('modifiers', Array())
        self._addArrayProperty('points', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/collection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.collection_item_model import CollectionItemModel
from gui.impl.gen.view_models.views.lobby.rts.progression_item_model import ProgressionItemModel

class CollectionViewModel(ViewModel):
    __slots__ = ('onProgressBarAnimation', 'onMissionClick')

    def __init__(self, properties=5, commands=2):
        super(CollectionViewModel, self).__init__(properties=properties, commands=commands)

    def getPrevious(self):
        return self._getNumber(0)

    def setPrevious(self, value):
        self._setNumber(0, value)

    def getCurrent(self):
        return self._getNumber(1)

    def setCurrent(self, value):
        self._setNumber(1, value)

    def getTotal(self):
        return self._getNumber(2)

    def setTotal(self, value):
        self._setNumber(2, value)

    def getCollection(self):
        return self._getArray(3)

    def setCollection(self, value):
        self._setArray(3, value)

    def getProgression(self):
        return self._getArray(4)

    def setProgression(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(CollectionViewModel, self)._initialize()
        self._addNumberProperty('previous', 0)
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addArrayProperty('collection', Array())
        self._addArrayProperty('progression', Array())
        self.onProgressBarAnimation = self._addCommand('onProgressBarAnimation')
        self.onMissionClick = self._addCommand('onMissionClick')

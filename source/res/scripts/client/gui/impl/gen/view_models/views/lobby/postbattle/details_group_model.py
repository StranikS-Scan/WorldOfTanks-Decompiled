# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/details_group_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.details_item_model import DetailsItemModel

class DetailsGroupModel(DetailsItemModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DetailsGroupModel, self).__init__(properties=properties, commands=commands)

    def getRecords(self):
        return self._getArray(2)

    def setRecords(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(DetailsGroupModel, self)._initialize()
        self._addArrayProperty('records', Array())

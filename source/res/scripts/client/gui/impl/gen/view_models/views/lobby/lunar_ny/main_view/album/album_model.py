# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/main_view/album/album_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel

class AlbumModel(ViewModel):
    __slots__ = ('onSlotClick', 'onRemoveCharm')

    def __init__(self, properties=3, commands=2):
        super(AlbumModel, self).__init__(properties=properties, commands=commands)

    def getCountNewCharms(self):
        return self._getNumber(0)

    def setCountNewCharms(self, value):
        self._setNumber(0, value)

    def getCountCharmsInStorage(self):
        return self._getNumber(1)

    def setCountCharmsInStorage(self, value):
        self._setNumber(1, value)

    def getCharmsInSlots(self):
        return self._getArray(2)

    def setCharmsInSlots(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(AlbumModel, self)._initialize()
        self._addNumberProperty('countNewCharms', 0)
        self._addNumberProperty('countCharmsInStorage', 0)
        self._addArrayProperty('charmsInSlots', Array())
        self.onSlotClick = self._addCommand('onSlotClick')
        self.onRemoveCharm = self._addCommand('onRemoveCharm')

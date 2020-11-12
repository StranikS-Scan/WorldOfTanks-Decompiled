# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/tooltips/china_loot_box_infotype_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.tooltips.infotype_slot_model import InfotypeSlotModel

class BoxType(Enum):
    COMMON = 'china_common'
    PREMIUM = 'china_premium'


class ChinaLootBoxInfotypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ChinaLootBoxInfotypeModel, self).__init__(properties=properties, commands=commands)

    def getBoxType(self):
        return BoxType(self._getString(0))

    def setBoxType(self, value):
        self._setString(0, value)

    def getSlots(self):
        return self._getArray(1)

    def setSlots(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(ChinaLootBoxInfotypeModel, self)._initialize()
        self._addStringProperty('boxType')
        self._addArrayProperty('slots', Array())

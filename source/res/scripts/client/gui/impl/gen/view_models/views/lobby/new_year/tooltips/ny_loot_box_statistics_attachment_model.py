# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_loot_box_statistics_attachment_model.py
from frameworks.wulf import ViewModel

class NyLootBoxStatisticsAttachmentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyLootBoxStatisticsAttachmentModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def getRarity(self):
        return self._getString(2)

    def setRarity(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NyLootBoxStatisticsAttachmentModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('amount', 0)
        self._addStringProperty('rarity', '')

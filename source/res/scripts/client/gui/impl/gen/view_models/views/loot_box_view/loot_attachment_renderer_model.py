# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_attachment_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootAttachmentRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(LootAttachmentRendererModel, self).__init__(properties=properties, commands=commands)

    def getGroupName(self):
        return self._getString(14)

    def setGroupName(self, value):
        self._setString(14, value)

    def getAttachName(self):
        return self._getString(15)

    def setAttachName(self, value):
        self._setString(15, value)

    def getRarity(self):
        return self._getString(16)

    def setRarity(self, value):
        self._setString(16, value)

    def _initialize(self):
        super(LootAttachmentRendererModel, self)._initialize()
        self._addStringProperty('groupName', '')
        self._addStringProperty('attachName', '')
        self._addStringProperty('rarity', '')

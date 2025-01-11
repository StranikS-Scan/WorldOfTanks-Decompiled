# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_attachment_special_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_attachment_renderer_model import LootAttachmentRendererModel

class LootAttachmentSpecialRendererModel(LootAttachmentRendererModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(LootAttachmentSpecialRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(17)

    @staticmethod
    def getCongratsViewModelType():
        return CongratsViewModel

    def _initialize(self):
        super(LootAttachmentSpecialRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', CongratsViewModel())

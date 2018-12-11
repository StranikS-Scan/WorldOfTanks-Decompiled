# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_video_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootVideoRendererModel(LootDefRendererModel):
    __slots__ = ()

    def getVideoSrc(self):
        return self._getString(9)

    def setVideoSrc(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(LootVideoRendererModel, self)._initialize()
        self._addStringProperty('videoSrc', '')

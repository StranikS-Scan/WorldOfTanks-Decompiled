# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_video_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootVideoRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(LootVideoRendererModel, self).__init__(properties=properties, commands=commands)

    def getVideoSrc(self):
        return self._getString(10)

    def setVideoSrc(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(LootVideoRendererModel, self)._initialize()
        self._addStringProperty('videoSrc', '')

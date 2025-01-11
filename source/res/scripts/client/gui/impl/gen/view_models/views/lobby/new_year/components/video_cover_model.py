# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/video_cover_model.py
from frameworks.wulf import ViewModel

class VideoCoverModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=0, commands=1):
        super(VideoCoverModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(VideoCoverModel, self)._initialize()
        self.onClick = self._addCommand('onClick')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/banner/banner_view_model.py
from frameworks.wulf import ViewModel

class BannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=0, commands=1):
        super(BannerViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(BannerViewModel, self)._initialize()
        self.onClick = self._addCommand('onClick')

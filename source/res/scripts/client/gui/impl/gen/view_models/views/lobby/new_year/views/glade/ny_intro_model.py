# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_intro_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.region_model import RegionModel
from gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class NyIntroModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(NyIntroModel, self).__init__(properties=properties, commands=commands)

    @property
    def videoCover(self):
        return self._getViewModel(0)

    @property
    def region(self):
        return self._getViewModel(1)

    def _initialize(self):
        super(NyIntroModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self.onClose = self._addCommand('onClose')

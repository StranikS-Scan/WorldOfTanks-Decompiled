# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/chapter_rewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel

class ChapterRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onSelectVehicle')

    def __init__(self, properties=1, commands=2):
        super(ChapterRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentChapter(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentChapterType():
        return ChapterModel

    def _initialize(self):
        super(ChapterRewardsViewModel, self)._initialize()
        self._addViewModelProperty('currentChapter', ChapterModel())
        self.onClose = self._addCommand('onClose')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')

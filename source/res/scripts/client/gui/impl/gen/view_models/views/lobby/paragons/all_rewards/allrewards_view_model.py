# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/all_rewards/allrewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel

class AllrewardsViewModel(ViewModel):
    __slots__ = ('onSelectVehicle',)

    def __init__(self, properties=1, commands=1):
        super(AllrewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentChapter(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentChapterType():
        return ChapterModel

    def _initialize(self):
        super(AllrewardsViewModel, self)._initialize()
        self._addViewModelProperty('currentChapter', ChapterModel())
        self.onSelectVehicle = self._addCommand('onSelectVehicle')

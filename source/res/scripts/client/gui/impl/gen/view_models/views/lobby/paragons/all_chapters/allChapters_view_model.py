# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/all_chapters/allChapters_view_model.py
from frameworks.wulf import ViewModel

class AllChaptersViewModel(ViewModel):
    __slots__ = ('onSelectChapter', 'onToChapterRewards')

    def __init__(self, properties=0, commands=2):
        super(AllChaptersViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(AllChaptersViewModel, self)._initialize()
        self.onSelectChapter = self._addCommand('onSelectChapter')
        self.onToChapterRewards = self._addCommand('onToChapterRewards')

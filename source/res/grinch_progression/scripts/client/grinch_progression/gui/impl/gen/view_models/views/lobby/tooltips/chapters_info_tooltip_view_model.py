# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/tooltips/chapters_info_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.tooltips.chapter_info_model import ChapterInfoModel

class ChaptersInfoTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ChaptersInfoTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getChapters(self):
        return self._getArray(0)

    def setChapters(self, value):
        self._setArray(0, value)

    @staticmethod
    def getChaptersType():
        return ChapterInfoModel

    def _initialize(self):
        super(ChaptersInfoTooltipViewModel, self)._initialize()
        self._addArrayProperty('chapters', Array())

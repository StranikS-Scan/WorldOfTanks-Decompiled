# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/tooltips/chapter_info_tooltip_view.py
from grinch.skeletons.battle_controller import IGrinchController
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from grinch_progression.gui.impl.gen.view_models.views.lobby.tooltips.chapter_info_model import ChapterInfoModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.tooltips.chapters_info_tooltip_view_model import ChaptersInfoTooltipViewModel
from helpers import dependency

class ChaptersTooltipView(ViewImpl):
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.grinch_progression.lobby.tooltips.ChaptersInfoTooltipView())
        settings.model = ChaptersInfoTooltipViewModel()
        super(ChaptersTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChaptersTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChaptersTooltipView, self)._onLoading(*args, **kwargs)
        chaptersModel = self.viewModel.getChapters()
        for season in self.__grinchCtrl.getAllSeasons():
            chapterModel = ChapterInfoModel()
            chapterModel.setStartDate(season.getStartDate())
            chapterModel.setEndDate(season.getEndDate())
            chaptersModel.addViewModel(chapterModel)

        chaptersModel.invalidate()

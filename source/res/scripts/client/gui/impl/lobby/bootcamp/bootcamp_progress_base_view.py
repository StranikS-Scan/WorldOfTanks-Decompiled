# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_progress_base_view.py
from constants import BootcampVersion
from gui.impl.pub import ViewImpl
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.bootcamp.rewards_tooltip import RewardsTooltip
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.bootcamp.bootcamp_lesson_model import BootcampLessonModel
from gui.shared.tooltips.bootcamp import BootcampStatuses
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from bootcamp.Bootcamp import g_bootcamp
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP

class BootcampProgressBaseView(ViewImpl):
    __slots__ = ('__tooltipData',)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, settings):
        super(BootcampProgressBaseView, self).__init__(settings)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(BootcampProgressBaseView, self).getViewModel()

    def _setupModel(self, model):
        self.__fillProgressBar(model)

    def _onLoading(self, *args, **kwargs):
        super(BootcampProgressBaseView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._setupModel(model)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId:
                tooltipData = self.__tooltipData[int(tooltipId)]
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
        super(BootcampProgressBaseView, self).createToolTip(event)
        return

    def createToolTipContent(self, event, contentID):
        return RewardsTooltip(self.bootcampController.needAwarding()) if contentID == R.views.lobby.bootcamp.RewardsTooltip() else super(BootcampProgressBaseView, self).createToolTipContent(event=event, contentID=contentID)

    def __getProgressBarItem(self, tooltipArgs):
        return {'tooltipArgs': tooltipArgs}

    def __getProgressBarItems(self):
        return [self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_1, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_1]), self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_2, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_2_SHORT])] if g_bootcamp.getVersion() == BootcampVersion.SHORT else [self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_1, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_1]),
         self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_2, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_2]),
         self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_3, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_3]),
         self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_4, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_4]),
         self.__getProgressBarItem([BOOTCAMP.TOOLTIP_PROGRESSION_LABEL_LESSON_5, BOOTCAMP.TOOLTIP_PROGRESSION_DESCRIPTION_LESSON_5])]

    def __fillProgressBar(self, viewModel):
        progressBarItems = self.__getProgressBarItems()
        currentLesson = g_bootcamp.getLessonNum()
        isNeedAwarding = self.bootcampController.needAwarding()
        viewModel.setCurrentLesson(currentLesson)
        viewModel.setTotalLessons(g_bootcamp.getContextIntParameter('lastLessonNum'))
        viewModel.setIsNeedAwarding(isNeedAwarding)
        lessons = Array()
        for index, lessonRaw in enumerate(progressBarItems):
            lessonModel = BootcampLessonModel()
            lessonNumber = index + 1
            lessonModel.setLessonNumber(lessonNumber)
            lessonModel.setCompleted(lessonNumber <= currentLesson)
            lessonModel.setCurrent(lessonNumber == currentLesson + 1)
            lessonModel.setTooltipId(lessonNumber)
            status = BootcampStatuses.IN_PROGRESS if lessonNumber == currentLesson else (BootcampStatuses.COMPLETED if lessonNumber < currentLesson else None)
            self.__tooltipData[lessonNumber] = createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BOOTCAMP_LESSON_PROGRESS, specialArgs=lessonRaw['tooltipArgs'] + [status])
            lessons.addViewModel(lessonModel)

        lessons.invalidate()
        viewModel.setLevels(lessons)
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/birthday_entry_point_view.py
from collections import namedtuple
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.hangar.entry_points.gf_header_widget import GFHeaderWidget, GFHeaderWidgetView
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_entry_point_view_model import BirthdayEntryPointViewModel
from helpers import dependency
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import fillProgression
from mt_birthday.gui.shared.event_dispatcher import showMainView
from mt_birthday.gui.impl.lobby.tooltips.economy_bonus_tooltip import EconomyBonusTooltip
from mt_birthday.gui.impl.lobby.tooltips.entry_point_tooltip import EntryPointTooltip
ProgressionAnimationData = namedtuple('_ProgressionAnimationData', 'currentPoints deltaPoints')

class BirthdayEntryPointView(GFHeaderWidgetView):
    __mtBirthday = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ('__tooltipData', '__prevProgressionPoints', '__queueAnimations', '__isAnimationStarted')

    def __init__(self, *args):
        super(BirthdayEntryPointView, self).__init__(R.views.mt_birthday.lobby.birthday.BirthdayEntryPointView(), BirthdayEntryPointViewModel())
        self.__prevProgressionPoints = None
        self.__tooltipData = {}
        self.__queueAnimations = []
        self.__isAnimationStarted = False
        return

    def _getEvents(self):
        events = super(BirthdayEntryPointView, self)._getEvents()
        events += ((self.viewModel.onClick, showMainView),
         (self.viewModel.onComponentDestroyed, self.__onComponentDestroyed),
         (self.viewModel.onAnimationEnded, self.__onAnimationEnded),
         (self.__mtBirthday.progression.onProgressionUpdated, self.__onProgressionUpdated),
         (self.__mtBirthday.onEventSettingsUpdated, self.__onEventSettingsUpdated))
        return events

    @property
    def viewModel(self):
        return super(BirthdayEntryPointView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BirthdayEntryPointView, self)._onLoading()
        self.__prevProgressionPoints = self.__mtBirthday.progression.getProgressionTokensCount()
        fillProgression(self.viewModel, self.__tooltipData)
        self.viewModel.setIsPaused(self.__mtBirthday.isPaused())
        self.viewModel.setEconomicBonus(self.__mtBirthday.getEconomyBonusValue())

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BirthdayEntryPointView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.EconomyBonusTooltip():
            return EconomyBonusTooltip()
        return EntryPointTooltip() if contentID == R.views.mt_birthday.lobby.tooltips.EntryPointTooltip() else super(BirthdayEntryPointView, self).createToolTipContent(event, contentID)

    def __startAnimation(self, progressionAnimationData):
        with self.viewModel.transaction() as tx:
            progression = tx.progression
            progression.setCurrentPoints(progressionAnimationData.currentPoints)
            if self.__mtBirthday.progression.isInfinityLevel():
                progression.setInfinityDeltaFrom(progressionAnimationData.deltaPoints)
            else:
                progression.setPointsDeltaFrom(progressionAnimationData.deltaPoints)

    def __onProgressionUpdated(self):
        _, infLevelConfig = self.__mtBirthday.progression.getInfinityLevel()
        infLevelMaxPoints = infLevelConfig['maxProgressionPoints']
        isLevelUp = False
        currentPoints = self.__mtBirthday.progression.getProgressionTokensCount()
        prevPoints = self.__prevProgressionPoints
        self.__prevProgressionPoints = currentPoints
        deltaPoints = currentPoints - prevPoints
        if deltaPoints > 0:
            currentLevel, currentLevelConfig = self.__mtBirthday.progression.getCurrentProgressionLevel()
            prevLevel, _ = self.__mtBirthday.progression.getLevelByPoints(min(prevPoints, infLevelMaxPoints))
            if currentLevel is not None and prevLevel is not None and currentLevel - prevLevel > 0:
                isLevelUp = True
            if not isLevelUp:
                progressionAnimationData = ProgressionAnimationData(currentPoints, prevPoints)
                self.__queueAnimations.append(progressionAnimationData)
            else:
                currentLevelMinProgressionPoints = currentLevelConfig['minProgressionPoints']
                progressionAnimationData = ProgressionAnimationData(currentLevelMinProgressionPoints, prevPoints)
                self.__queueAnimations.append(progressionAnimationData)
                progressionAnimationData = ProgressionAnimationData(currentPoints, currentLevelMinProgressionPoints)
                self.__queueAnimations.append(progressionAnimationData)
        elif deltaPoints < 0:
            _, levelConfig = self.__mtBirthday.progression.getLevelByPoints(min(currentPoints, infLevelMaxPoints - 1))
            minProgressPoints = levelConfig['minProgressionPoints']
            self.__queueAnimations.append(ProgressionAnimationData(minProgressPoints, prevPoints))
            self.__queueAnimations.append(ProgressionAnimationData(currentPoints, minProgressPoints - 1))
        if not self.__isAnimationStarted and self.__queueAnimations:
            self.__isAnimationStarted = True
            self.__startAnimation(self.__queueAnimations.pop(0))
        return

    def __onAnimationEnded(self):
        with self.viewModel.transaction() as tx:
            progression = tx.progression
            currPoints = progression.getCurrentPoints()
            if self.__mtBirthday.progression.isInfinityLevel():
                progression.setInfinityDeltaFrom(currPoints)
            else:
                progression.setPointsDeltaFrom(currPoints)
            if not self.__mtBirthday.progression.isInfinityLevel():
                level, _ = self.__mtBirthday.progression.getLevelByPoints(currPoints)
                if level > progression.getCurrentLevel():
                    progression.setCurrentLevel(level)
            else:
                infinityLevel = self.__mtBirthday.progression.getInfinityProgressionTokensCount()
                if infinityLevel > progression.getInfinityLevelCompleteCount():
                    progression.setInfinityLevelCompleteCount(self.__mtBirthday.progression.getInfinityProgressionTokensCount())
        if self.__queueAnimations:
            self.__startAnimation(self.__queueAnimations.pop(0))
        self.__isAnimationStarted = False

    def __onEventSettingsUpdated(self):
        self.viewModel.setIsPaused(self.__mtBirthday.isPaused())

    def __onComponentDestroyed(self):
        self.__prevProgressionPoints = self.__mtBirthday.progression.getProgressionTokensCount()
        self.__isAnimationStarted = False
        self.__queueAnimations.clear()


class BirthdayEntryPointWidget(GFHeaderWidget):
    __slots__ = ()

    def _makeInjectView(self):
        return BirthdayEntryPointView()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_event_progression_providers.py
import datetime
from adisp import process
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import time_utils, dependency, int2roman
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.game_control import IEventProgressionController
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.formatters import text_styles, icons
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from battle_selector_extra_item import SelectorExtraItem
_R_BATTLE_TYPES = R.strings.menu.headerButtons.battle.types
_R_BATTLE_MENU = R.strings.menu.headerButtons.battle.menu
_R_ICONS = R.images.gui.maps.icons

class EventProgressionDefaultDataProvider(SelectorExtraItem):
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __slots__ = ('_isDisabled', '_isNew')

    def __init__(self):
        super(EventProgressionDefaultDataProvider, self).__init__(label=backport.text(_R_BATTLE_TYPES.eventProgression.about(), year=datetime.datetime.now().year), data=PREBATTLE_ACTION_NAME.EPIC, order=0, selectorType=SELECTOR_BATTLE_TYPES.EVENT_PROGRESSION)
        self._isDisabled = False
        self._isNew = False

    def select(self):
        self.__eventProgression.openURL()

    def isAvailable(self):
        return True

    def isDefault(self):
        return True

    def getSmallIcon(self):
        pass

    def getLargerIcon(self):
        pass

    def getFormattedLabel(self):
        return text_styles.main(self._label)

    def getMainLabel(self):
        return text_styles.highTitle(backport.text(_R_BATTLE_TYPES.eventProgression()))

    def getInfoLabel(self):
        return '{} {}'.format(text_styles.highTitle(self.__eventProgression.actualRewardPoints), icons.makeImageTag(backport.image(_R_ICONS.epicBattles.rewardPoints.c_16x16()), vSpace=-1))

    def isVisible(self):
        return self.__eventProgression.isEnabled and not self.__bootcampController.isInBootcamp()

    def getRibbonSrc(self):
        ribbonResId = self.__eventProgression.selectorRibbonResId
        ribbonSrc = backport.image(ribbonResId) if ribbonResId else ''
        return ribbonSrc

    def _update(self, state):
        self._label = backport.text(self.__eventProgression.aboutEventProgressionResId)


class EventProgressionDataProvider(SelectorExtraItem):
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __bcc = dependency.descriptor(IBootcampController)
    __slots__ = ('__queueType',)

    def __init__(self):
        SelectorExtraItem.__init__(self, label=0, data=0, order=0, isVisible=False)
        self.__queueType = 0

    def isShowNewIndicator(self):
        return False

    def isRandomBattle(self):
        return True

    def isAvailable(self):
        return False if self.__bcc.isInBootcamp() else self.__eventProgression.isAvailable() and self.__eventProgression.getCurrentSeason()

    def isDefault(self):
        return False

    def updateState(self):
        self._label = backport.text(self.__eventProgression.selectorLabelTxtId)
        self._data = self.__eventProgression.selectorData
        self._selectorType = self.__eventProgression.selectorType
        self.__queueType = self.__eventProgression.selectorQueueType
        self._isVisible = False
        if self.isAvailable() or self.__eventProgression.isFrozen():
            self._isVisible = any((self.__eventProgression.getCurrentSeason(), self.__eventProgression.getNextSeason()))
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        self._isDisabled = not self.__eventProgression.modeIsEnabled()
        return

    def getFormattedLabel(self):
        battleTypeName = text_styles.middleTitle(self.getLabel())
        availabilityStr = self._getPerformanceAlarmStr() or self._getScheduleStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererExtraBGEvent()) if self.__eventProgression.isActive() else ''

    def getMainLabel(self):
        return text_styles.highTitle(backport.text(_R_BATTLE_TYPES.eventProgression()))

    def getInfoLabel(self):
        return '{} {}'.format(text_styles.highTitle(self.__eventProgression.actualRewardPoints), icons.makeImageTag(backport.image(_R_ICONS.epicBattles.rewardPoints.c_16x16()), vSpace=-2))

    def getRibbonSrc(self):
        ribbonResId = self.__eventProgression.selectorRibbonResId
        ribbonSrc = backport.image(ribbonResId) if ribbonResId else ''
        return ribbonSrc

    def _update(self, state):
        self.updateState()
        self._isSelected = state.isQueueSelected(self.__queueType)

    def _getScheduleStr(self):
        if self._isDisabled:
            return text_styles.error(backport.text(_R_BATTLE_TYPES.epic.extra.frozen()))
        else:
            currentSeason = self.__eventProgression.getCurrentSeason()
            if currentSeason:
                seasonResID = R.strings.epic_battle.season.num(currentSeason.getSeasonID())
                seasonName = backport.text(seasonResID.name()) if seasonResID else None
                if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                    cycleNumber = currentSeason.getCycleInfo().getEpicCycleNumber()
                    scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.currentCycle(), cycle=int2roman(cycleNumber), season=seasonName)
                else:
                    nextCycle = currentSeason.getNextCycleInfo(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle is None:
                        nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle:
                        nextCycleStartTime = backport.getDateTimeFormat(nextCycle.startDate)
                        scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=nextCycleStartTime)
                    else:
                        scheduleStr = None
            else:
                nextSeason = self.__eventProgression.getNextSeason()
                nextCycle = nextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                if nextCycle:
                    startTime = backport.getDateTimeFormat(nextCycle.startDate)
                    scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=startTime)
                else:
                    scheduleStr = None
            return text_styles.main(scheduleStr) if scheduleStr else None

    def _getPerformanceAlarmStr(self):
        currPerformanceGroup = self.__eventProgression.getPerformanceGroup()
        attentionText, iconPath = (None, None)
        if currPerformanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            attentionText = text_styles.error(backport.text(_R_BATTLE_MENU.attention.lowPerformance()))
            iconPath = backport.image(_R_ICONS.library.marker_blocked())
        elif currPerformanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            attentionText = text_styles.alert(backport.text(_R_BATTLE_MENU.attention.reducedPerformance()))
            iconPath = backport.image(_R_ICONS.library.alertIcon())
        return icons.makeImageTag(iconPath, vSpace=-3) + ' ' + attentionText if attentionText and iconPath else None

    @process
    def _doSelect(self, dispatcher):
        if self.__eventProgression.getCurrentSeason() is not None or self.__eventProgression.getNextSeason() is not None:
            isSuccess = yield dispatcher.doSelectAction(PrbAction(self._data))
            if isSuccess and self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)
            else:
                return
        self.__eventProgression.openURL()
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/epic_battles_widget.py
from collections import namedtuple
import SoundGroups
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import LABEL_STATE
from gui.Scaleform.daapi.view.lobby.missions.regular import missions_page
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import isEpicDailyQuestsRefreshAvailable
from gui.Scaleform.daapi.view.meta.EpicBattlesWidgetMeta import EpicBattlesWidgetMeta
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.periodic_battles.models import CalendarStatusVO
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, int2roman
from helpers import time_utils
from helpers.time_utils import ONE_DAY
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController, IQuestsController, IEventProgressionController
EpicBattlesWidgetVO = namedtuple('EpicBattlesWidgetVO', ('calendarStatus', 'showAlert', 'epicMetaLevelIconData', 'quests'))

def _getTimeTo(timeStamp, textId):
    timeLeft = time_utils.getTillTimeString(timeStamp, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY, removeLeadingZeros=True)
    return backport.text(textId, value=text_styles.stats(timeLeft))


def getTimeToStartStr(timeStamp):
    return _getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToStart())


def getTimeToLeftStr(timeStamp):
    return _getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToLeft())


def getCycleRomanNumberStr(cycleNumber):
    txtId = R.strings.tooltips.eventProgression.season()
    return backport.text(txtId, season=int2roman(cycleNumber))


def getLevelStr(level):
    txtId = R.strings.tooltips.eventProgression.level()
    return backport.text(txtId, level=level)


class EpicBattlesWidget(EpicBattlesWidgetMeta):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __questController = dependency.descriptor(IQuestsController)
    __eventProgressionController = dependency.descriptor(IEventProgressionController)

    def __init__(self):
        super(EpicBattlesWidget, self).__init__()
        self.__periodicNotifier = None
        self._currentVehicle = None
        return

    def onWidgetClick(self):
        self.__eventProgressionController.openURL()

    def onQuestBtnClick(self, questType, questID):
        if questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON:
            missions_page.setHideDoneFilter()
            showMissionsCategories()

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def onChangeServerClick(self):
        event_dispatcher.showEpicBattlesPrimeTimeWindow()

    def update(self):
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.startNotification()
        self.as_setDataS(self._buildVO()._asdict())
        return

    def _populate(self):
        super(EpicBattlesWidget, self)._populate()
        if self.__periodicNotifier is None:
            self.__periodicNotifier = PeriodicNotifier(self.__epicMetaGameCtrl.getTimer, self.update)
        self.__periodicNotifier.startNotification()
        self._currentVehicle = g_currentVehicle
        return

    def _dispose(self):
        if self.__periodicNotifier is not None:
            self.__periodicNotifier.stopNotification()
            self.__periodicNotifier.clear()
            self.__periodicNotifier = None
        super(EpicBattlesWidget, self)._dispose()
        self.__periodicNotifier = None
        self._currentVehicle = None
        return

    def _buildVO(self):
        showAlert = not self.__epicMetaGameCtrl.isInPrimeTime() and self.__epicMetaGameCtrl.isEnabled()
        season = self.__epicMetaGameCtrl.getCurrentSeason() or self.__epicMetaGameCtrl.getNextSeason()
        if self.__epicMetaGameCtrl.isActive():
            _, plLevel, _ = self.__epicMetaGameCtrl.getPlayerLevelInfo()
        else:
            plLevel = None
        cycleNumber = 1
        if season is not None:
            cycleNumber = self.__epicMetaGameCtrl.getCurrentOrNextActiveCycleNumber(season)
        return EpicBattlesWidgetVO(calendarStatus=self.__getStatusBlock()._asdict(), showAlert=showAlert, epicMetaLevelIconData=getEpicMetaIconVODict(cycleNumber, plLevel), quests=self.__getQuestsVO(self._currentVehicle.item, plLevel))

    def __getQuestsVO(self, vehicle, level):
        if not self.__epicMetaGameCtrl.isAvailable():
            return []
        quests = [ q for q in self.__questController.getQuestForVehicle(vehicle) if q.getID() in self.__eventProgressionController.questIDs ]
        totalCount = len(quests)
        completedQuests = len([ q for q in quests if q.isCompleted() ])
        libraryIcons = R.images.gui.maps.icons.library
        commonQuestsIcon = libraryIcons.outline.quests_available()
        if not totalCount:
            commonQuestsIcon = libraryIcons.outline.quests_disabled()
            label = ''
        elif level < self.__epicMetaGameCtrl.getMaxPlayerLevel():
            label = icons.makeImageTag(backport.image(libraryIcons.CancelIcon_1()))
        elif completedQuests != totalCount:
            label = backport.text(R.strings.menu.hangar_header.battle_quests_label.dyn(LABEL_STATE.ACTIVE)(), total=totalCount - completedQuests)
        else:
            currentCycleEndTime, _ = self.__epicMetaGameCtrl.getCurrentCycleInfo()
            cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp()
            if cycleTimeLeft < ONE_DAY or not isEpicDailyQuestsRefreshAvailable():
                label = icons.makeImageTag(backport.image(libraryIcons.ConfirmIcon_1()))
            else:
                label = icons.makeImageTag(backport.image(libraryIcons.time_icon()))
        quests = [self._headerQuestFormatterVo(totalCount > 0, backport.image(commonQuestsIcon), label, HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, flag=backport.image(libraryIcons.hangarFlag.flag_epic()), tooltip=TOOLTIPS_CONSTANTS.EPIC_QUESTS_PREVIEW, isTooltipSpecial=True)]
        return [self.__wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)]

    def __wrapQuestGroup(self, groupID, icon, quests):
        return {'groupID': groupID,
         'groupIcon': icon,
         'quests': quests}

    def _headerQuestFormatterVo(self, enable, icon, label, questType, flag=None, stateIcon=None, questID=None, isReward=False, tooltip='', isTooltipSpecial=False):
        return {'enable': enable,
         'flag': flag,
         'icon': icon,
         'stateIcon': stateIcon,
         'label': label,
         'questType': questType,
         'questID': str(questID),
         'isReward': isReward,
         'tooltip': tooltip,
         'isTooltipSpecial': isTooltipSpecial}

    def __getStatusBlock(self):
        status, timeLeft, _ = self.__epicMetaGameCtrl.getPrimeTimeStatus()
        showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
        hasAvailableServers = self.__epicMetaGameCtrl.hasAvailablePrimeTimeServers()
        return CalendarStatusVO(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.epic_battle.widgetAlertMessageBlock.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=self.__getAlertStatusText(timeLeft, hasAvailableServers), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=None)

    def __getAlertStatusText(self, timeLeft, hasAvailableServers):
        rAlertMsgBlock = R.strings.epic_battle.widgetAlertMessageBlock
        alertStr = ''
        if hasAvailableServers:
            alertStr = backport.text(rAlertMsgBlock.somePeripheriesHalt(), serverName=self.__connectionMgr.serverUserNameShort)
        else:
            currSeason = self.__epicMetaGameCtrl.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            primeTime = self.__epicMetaGameCtrl.getPrimeTimes().get(self.__connectionMgr.peripheryID)
            isCycleNow = currSeason and currSeason.hasActiveCycle(currTime) and primeTime and primeTime.getPeriodsBetween(currTime, currSeason.getCycleEndDate())
            if isCycleNow:
                if self.__connectionMgr.isStandalone():
                    key = rAlertMsgBlock.singleModeHalt
                else:
                    key = rAlertMsgBlock.allPeripheriesHalt
                timeLeftStr = time_utils.getTillTimeString(timeLeft, EPIC_BATTLE.STATUS_TIMELEFT, removeLeadingZeros=True)
                alertStr = backport.text(key(), time=timeLeftStr)
            else:
                nextSeason = currSeason or self.__epicMetaGameCtrl.getNextSeason()
                if nextSeason is not None:
                    nextCycle = nextSeason.getNextByTimeCycle(currTime)
                    if nextCycle is not None:
                        cycleNumber = nextCycle.getEpicCycleNumber()
                        timeLeftStr = time_utils.getTillTimeString(nextCycle.startDate - currTime, EPIC_BATTLE.STATUS_TIMELEFT, removeLeadingZeros=True)
                        alertStr = backport.text(rAlertMsgBlock.startIn(), cycle=int2roman(cycleNumber), time=timeLeftStr)
                if not alertStr:
                    prevSeason = currSeason or self.__epicMetaGameCtrl.getPreviousSeason()
                    if prevSeason is not None:
                        prevCycle = prevSeason.getLastActiveCycleInfo(currTime)
                        if prevCycle is not None:
                            cycleNumber = prevCycle.getEpicCycleNumber()
                            alertStr = backport.text(rAlertMsgBlock.noCycleMessage(), cycle=int2roman(cycleNumber))
        return text_styles.vehicleStatusCriticalText(alertStr)

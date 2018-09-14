# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleDirectionPopover.py
import operator
import sys
import BigWorld
from gui import SystemMessages
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import prbPeripheriesHandlerProperty, prbDispatcherProperty
from gui.shared.fortifications import fort_helpers, events_dispatcher as fort_events
from helpers import i18n, time_utils
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.FortBattleDirectionPopoverMeta import FortBattleDirectionPopoverMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

class FortBattleDirectionPopover(View, FortBattleDirectionPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):
    INVALIDATE_INTERVAL = 60

    def __init__(self, ctx = None):
        super(FortBattleDirectionPopover, self).__init__()
        self._direction = ctx.get('data')
        self.__updateCallbackID = None
        return

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def requestToJoin(self, battleID):
        currentBattleID = getBattleID()
        if currentBattleID == battleID:
            fort_events.showFortBattleRoomWindow()
        else:
            battle = self.fortCtrl.getFort().getBattle(battleID)
            if battle is not None:
                fort_helpers.tryToConnectFortBattle(battleID, battle.getPeripheryID())
            else:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_ERRORS_BATTLE_DOES_NOT_EXIST, type=SystemMessages.SM_TYPE.Error)
        return

    def onWindowClose(self):
        self.destroy()

    def onFortBattleChanged(self, cache, item, battleItem):
        self._prepareAndSetData()

    def _populate(self):
        super(FortBattleDirectionPopover, self)._populate()
        self.startFortListening()
        self._prepareAndSetData()

    def _dispose(self):
        self.__clearCallback()
        self.stopFortListening()
        super(FortBattleDirectionPopoverMeta, self)._dispose()

    def _prepareAndSetData(self):
        battles = []
        invalidateCbDelay = sys.maxint
        fort = self.fortCtrl.getFort()
        self.__clearCallback()
        for battleItem in self.__applyBattlesFilter(fort.getAttacksIn(timePeriod=time_utils.ONE_DAY)):
            battles.append((battleItem,
             i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERBATTLENAME_CLANBATTLEOFFENCE, clanName=self.__getFmtClanName(battleItem)),
             RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCEFUTURE,
             TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_OFFENSE))

        for battleItem in self.__applyBattlesFilter(fort.getDefencesIn(timePeriod=time_utils.ONE_DAY)):
            battles.append((battleItem,
             i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERBATTLENAME_CLANBATTLEDEFENCE, clanName=self.__getFmtClanName(battleItem)),
             RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTURE,
             TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_DEFENSE))

        result = []
        for battleItem, descr, icon, typeTip in sorted(battles, key=operator.itemgetter(0)):
            startTime, startTimeLeft = battleItem.getStartTime(), battleItem.getStartTimeLeft()
            fortBattle = fort.getBattle(battleItem.getBattleID())
            if fortBattle is not None:
                startTime, startTimeLeft = fortBattle.getRoundStartTime(), fortBattle.getRoundStartTimeLeft()
                if fortBattle.isBattleRound():
                    startTimeLeft = 0
            if startTimeLeft > time_utils.QUARTER_HOUR:
                invalidateCbDelay = min(invalidateCbDelay, startTimeLeft - time_utils.QUARTER_HOUR)
            elif startTimeLeft > 0:
                invalidateCbDelay = min(invalidateCbDelay, startTimeLeft)
            if startTimeLeft <= 0:
                infoTip = TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_ISINBATTLE
            else:
                infoTip = ''
            if battleItem.isHot() and startTimeLeft > 0:
                timerData = {'timeBeforeBattle': startTimeLeft,
                 'htmlFormatter': self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, '###')}
            else:
                timerData = None
            battleHoutFmt = i18n.makeString('#fortifications:fortBattleDirectionPopover/battleDurationFmt')
            battleHourLabel = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, battleHoutFmt % {'prevHour': BigWorld.wg_getShortTimeFormat(startTime),
             'nextHour': BigWorld.wg_getShortTimeFormat(startTime + time_utils.ONE_HOUR)})
            result.append({'description': descr,
             'canJoin': battleItem.isHot(),
             'battleInfo': self.__getBattleInfo(startTime, startTimeLeft),
             'battleHour': battleHourLabel,
             'battleTypeIcon': icon,
             'fortBattleID': battleItem.getBattleID(),
             'battleTypeTooltip': typeTip,
             'battleInfoTooltip': infoTip,
             'timer': timerData})

        title = i18n.makeString(FORTIFICATIONS.GENERAL_DIRECTION, value=i18n.makeString('#fortifications:General/directionName%d' % self._direction))
        nextBattles = ' %s' % i18n.makeString(FORTIFICATIONS.FORTBATTLEDIRECTIONPOPOVER_COMMINGBATTLES)
        nextBattlesLabel = self.app.utilsManager.textManager.concatStyles(((TextType.STANDARD_TEXT, nextBattles), (TextType.MAIN_TEXT, len(result))))
        self.as_setDataS({'title': title,
         'nextBattles': nextBattlesLabel,
         'battlesList': result})
        if invalidateCbDelay != sys.maxint:
            LOG_DEBUG('FortBattleDirectionPopover, load invalidation callback', invalidateCbDelay)
            self.__loadCallback(invalidateCbDelay)
        return

    def __applyBattlesFilter(self, battleItems):
        for battleItem in battleItems:
            if battleItem.getDirection() == self._direction:
                if not battleItem.isEnded() and battleItem.getStartTimeLeft() <= time_utils.ONE_DAY:
                    yield battleItem

    def __getBattleInfo(self, startTime, startTimeLeft):
        if startTimeLeft > time_utils.QUARTER_HOUR:
            if time_utils.isTimeNextDay(startTime):
                return self.app.utilsManager.textManager.getText(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TOMORROW), TextType.STANDARD_TEXT)
            if time_utils.isTimeThisDay(startTime):
                return self.app.utilsManager.textManager.getText(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TODAY), TextType.STANDARD_TEXT)
        else:
            if startTimeLeft > 0:
                return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE) + ' ')
            inBattleText = ' ' + i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_ISBATTLE)
            return self.app.utilsManager.textManager.concatStyles(((TextIcons.SWORDS,), (TextType.ERROR_TEXT, inBattleText)))
        return ''

    def __invalidateCallbackHandler(self):
        self._prepareAndSetData()

    def __getFmtClanName(self, battleItem):
        _, clanAbbrev, _ = battleItem.getOpponentClanInfo()
        return '[' + clanAbbrev + ']'

    def __loadCallback(self, delay):
        self.__clearCallback()
        self.__updateCallbackID = BigWorld.callback(delay, self.__invalidateCallbackHandler)

    def __clearCallback(self):
        if self.__updateCallbackID is not None:
            BigWorld.cancelCallback(self.__updateCallbackID)
            self.__updateCallbackID = None
        return

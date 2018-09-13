# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleDirectionPopover.py
import time
import operator
import sys
import BigWorld
from adisp import process
from constants import PREBATTLE_TYPE
from gui import DialogsInterface, SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import prbPeripheriesHandlerProperty
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.fortifications.context import CreateOrJoinFortBattleCtx
from helpers import i18n, time_utils
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
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

    def requestToJoin(self, battleID):
        currentBattleID = getBattleID()
        if currentBattleID == battleID:
            g_eventBus.handleEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)
        else:
            battle = self.fortCtrl.getFort().getBattle(battleID)
            peripheryID = battle.getPeripheryID()
            if g_lobbyContext.isAnotherPeriphery(peripheryID):
                if g_lobbyContext.isPeripheryAvailable(peripheryID):
                    self.__requestToReloginAndCreateOrJoinFortBattle(peripheryID, battleID)
                else:
                    SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
            else:
                self.__requestToCreateOrJoinFortBattle(battleID)

    def onWindowClose(self):
        self.destroy()

    def onUpdated(self):
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
        for battleItem in self.__applyBattlesFilter(self.fortCtrl.getFort().getAttacks()):
            battles.append((battleItem,
             i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERBATTLENAME_CLANBATTLEOFFENCE, clanName=self.__getFmtClanName(battleItem)),
             RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCEFUTURE,
             TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_OFFENSE))

        for battleItem in self.__applyBattlesFilter(self.fortCtrl.getFort().getDefences()):
            battles.append((battleItem,
             i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERBATTLENAME_CLANBATTLEDEFENCE, clanName=self.__getFmtClanName(battleItem)),
             RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTURE,
             TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_DEFENSE))

        result = []
        for battleItem, descr, icon, typeTip in sorted(battles, key=operator.itemgetter(0)):
            startTime, startTimeLeft = battleItem.getStartTime(), battleItem.getStartTimeLeft()
            if startTimeLeft > time_utils.QUARTER_HOUR:
                invalidateCbDelay = min(invalidateCbDelay, startTimeLeft - time_utils.QUARTER_HOUR)
            elif startTimeLeft > 0:
                invalidateCbDelay = min(invalidateCbDelay, startTimeLeft)
            if startTimeLeft <= 0:
                infoTip = TOOLTIPS.FORTIFICATION_FORTBATTLEDIRECTIONPOPOVER_ISINBATTLE
            else:
                infoTip = ''
            if (battleItem.isPlanned() or battleItem.isInProgress()) and startTimeLeft <= time_utils.QUARTER_HOUR:
                timerData = {'timeBeforeBattle': startTimeLeft,
                 'htmlFormatter': fort_text.getText(fort_text.ALERT_TEXT, '###')}
            else:
                timerData = None
            battleHour = time.struct_time(time.localtime(startTime)).tm_hour
            endOfBattleHour = time.struct_time(time.localtime(startTime + time_utils.ONE_HOUR)).tm_hour
            battleHoutFmt = i18n.makeString('#fortifications:fortBattleDirectionPopover/battleDurationFmt')
            battleHourLabel = fort_text.getText(fort_text.MAIN_TEXT, battleHoutFmt % {'prevHour': battleHour,
             'nextHour': endOfBattleHour})
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
        nextBattlesLabel = fort_text.concatStyles(((fort_text.STANDARD_TEXT, nextBattles), (fort_text.MAIN_TEXT, len(result))))
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

    @classmethod
    def __getBattleInfo(cls, startTime, startTimeLeft):
        if startTimeLeft > time_utils.QUARTER_HOUR:
            if time_utils.isTimeNextDay(startTime):
                return fort_text.getText(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TOMORROW), fort_text.STANDARD_TEXT)
            if time_utils.isTimeThisDay(startTime):
                return fort_text.getText(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TODAY), fort_text.STANDARD_TEXT)
        else:
            if startTimeLeft > 0:
                return fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE) + ' ')
            inBattleText = ' ' + i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_ISBATTLE)
            return fort_text.concatStyles(((fort_text.SWORDS,), (fort_text.ERROR_TEXT, inBattleText)))
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

    @process
    def __requestToCreateOrJoinFortBattle(self, battleID):
        yield self.fortProvider.sendRequest(CreateOrJoinFortBattleCtx(battleID, waitingID='fort/fortBattle/createOrJoin'))

    @process
    def __requestToReloginAndCreateOrJoinFortBattle(self, peripheryID, battleID):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.FORT_BATTLE, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, CreateOrJoinFortBattleCtx(battleID, waitingID='fort/fortBattle/createOrJoin'))

# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleDirectionPopover.py
import operator
import sys
import BigWorld
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_formatters import getDivisionIcon
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.prb_getters import getBattleID
from gui.prb_control.prb_helpers import prbPeripheriesHandlerProperty, prbDispatcherProperty
from gui.shared.fortifications import fort_helpers, events_dispatcher as fort_events
from gui.shared.fortifications.fort_seqs import BATTLE_ITEM_TYPE
from helpers import i18n, time_utils
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortBattleDirectionPopoverMeta import FortBattleDirectionPopoverMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons

class FortBattleDirectionPopover(FortBattleDirectionPopoverMeta, FortViewHelper):
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
        if currentBattleID == battleID and self.prbDispatcher.getUnitFunctional().hasEntity():
            fort_events.showFortBattleRoomWindow()
        else:
            battle = self.fortCtrl.getFort().getBattle(battleID)
            if battle is not None:
                fort_helpers.tryToConnectFortBattle(battleID, battle.getPeripheryID())
            else:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_ERRORS_BATTLE_DOES_NOT_EXIST, type=SystemMessages.SM_TYPE.Error)
        self.destroy()
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
                 'htmlFormatter': text_styles.alert('###')}
            else:
                timerData = None
            battleHourFmt = i18n.makeString('#fortifications:fortBattleDirectionPopover/battleDurationFmt')
            battleHourLabel = text_styles.main(battleHourFmt % {'prevHour': BigWorld.wg_getShortTimeFormat(startTime),
             'nextHour': BigWorld.wg_getShortTimeFormat(startTime + time_utils.ONE_HOUR)})
            divisionIcon = getDivisionIcon(battleItem.defenderFortLevel, battleItem.attackerFortLevel, determineAlert=battleItem.getType() == BATTLE_ITEM_TYPE.ATTACK)
            result.append({'description': descr,
             'canJoin': battleItem.isHot(),
             'battleInfo': self.__getBattleInfo(startTime, startTimeLeft),
             'battleHour': battleHourLabel,
             'battleTypeIcon': icon,
             'fortBattleID': battleItem.getBattleID(),
             'battleTypeTooltip': typeTip,
             'battleInfoTooltip': infoTip,
             'timer': timerData,
             'divisionIcon': divisionIcon})

        title = i18n.makeString(FORTIFICATIONS.GENERAL_DIRECTION, value=i18n.makeString('#fortifications:General/directionName%d' % self._direction))
        nextBattles = i18n.makeString(FORTIFICATIONS.FORTBATTLEDIRECTIONPOPOVER_COMMINGBATTLES)
        nextBattlesLabel = ''.join((text_styles.standard(nextBattles), text_styles.main(len(result))))
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
                return text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TOMORROW))
            if time_utils.isTimeThisDay(startTime):
                return text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_DATE_TODAY))
        else:
            if startTimeLeft > 0:
                return text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_BEFOREBATTLE) + ' ')
            inBattleText = ' ' + i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_RENDERCURRENTTIME_ISBATTLE)
            return text_styles.error(icons.swords() + inBattleText)
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

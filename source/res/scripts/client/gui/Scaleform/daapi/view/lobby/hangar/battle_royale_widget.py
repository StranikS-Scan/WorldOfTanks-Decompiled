# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/battle_royale_widget.py
from collections import namedtuple
from battle_royale.gui.impl.lobby.views.widget_view import WidgetView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from helpers import int2roman
from helpers import dependency
from gui.Scaleform.locale.BATTLE_ROYALE import BATTLE_ROYALE
from gui.Scaleform.daapi.view.meta.BattleRoyaleHangarWidgetMeta import BattleRoyaleHangarWidgetMeta
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from skeletons.connection_mgr import IConnectionManager
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.periodic_battles.models import PrimeTimeStatus, AlertData
from helpers import time_utils
from gui.shared import event_dispatcher
from battle_royale_progression.gui.shared import event_dispatcher as battle_royale_event_dispatcher
from gui.shared.formatters import text_styles
BattleRoyaleWidgetVO = namedtuple('EpicBattlesWidgetVO', ('calendarStatus', 'showAlert'))

class BattleRoyaleHangarWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = WidgetView()
        return self.__view


class BattleRoyaleHangarWidget(BattleRoyaleHangarWidgetMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __slots__ = ()

    def onClick(self):
        if self.__brProgression.isEnabled:
            battle_royale_event_dispatcher.showProgressionView()
        else:
            self.__battleRoyaleController.openURL()

    def onChangeServerClick(self):
        event_dispatcher.showBattleRoyalePrimeTimeWindow()

    def _populate(self):
        super(BattleRoyaleHangarWidget, self)._populate()
        self.__battleRoyaleController.onWidgetUpdate += self.__update
        self.__update()

    def __update(self):
        showAlert = not self.__battleRoyaleController.isInPrimeTime() and self.__battleRoyaleController.isEnabled()
        data = BattleRoyaleWidgetVO(calendarStatus=self.__getStatusBlock().asDict(), showAlert=showAlert)._asdict()
        self.as_setDataS(data)

    def _dispose(self):
        self.__battleRoyaleController.onWidgetUpdate -= self.__update
        super(BattleRoyaleHangarWidget, self)._dispose()

    def __getStatusBlock(self):
        status, timeLeft, _ = self.__battleRoyaleController.getPrimeTimeStatus()
        showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
        unsuitablePeriphery = status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        hasAvailableServers = self.__battleRoyaleController.hasAvailablePrimeTimeServers()
        return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.battle_royale.widgetAlertMessageBlock.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=self.__getAlertStatusText(timeLeft, unsuitablePeriphery, hasAvailableServers), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=None, isSimpleTooltip=False)

    def __getAlertStatusText(self, timeLeft, unsuitablePeriphery, hasAvailableServers):
        rAlertMsgBlock = R.strings.battle_royale.widgetAlertMessageBlock
        alertStr = ''
        if hasAvailableServers:
            if unsuitablePeriphery:
                alertStr = backport.text(R.strings.battle_royale.alertMessage.unsuitablePeriphery())
            else:
                alertStr = backport.text(rAlertMsgBlock.somePeripheriesHalt(), serverName=self.__connectionMgr.serverUserNameShort)
        else:
            currSeason = self.__battleRoyaleController.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            primeTime = self.__battleRoyaleController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
            isCycleNow = currSeason and currSeason.hasActiveCycle(currTime) and primeTime and primeTime.getPeriodsBetween(currTime, currSeason.getCycleEndDate())
            if isCycleNow:
                if self.__connectionMgr.isStandalone():
                    key = rAlertMsgBlock.singleModeHalt
                else:
                    key = rAlertMsgBlock.allPeripheriesHalt
                timeLeftStr = time_utils.getTillTimeString(timeLeft, BATTLE_ROYALE.STATUS_TIMELEFT, removeLeadingZeros=True)
                alertStr = backport.text(key(), time=timeLeftStr)
            else:
                nextSeason = currSeason or self.__battleRoyaleController.getNextSeason()
                if nextSeason is not None:
                    nextCycle = nextSeason.getNextByTimeCycle(currTime)
                    if nextCycle is not None:
                        cycleNumber = nextCycle.getEpicCycleNumber()
                        timeLeftStr = time_utils.getTillTimeString(nextCycle.startDate - currTime, BATTLE_ROYALE.STATUS_TIMELEFT, removeLeadingZeros=True)
                        alertStr = backport.text(rAlertMsgBlock.startIn.single() if nextSeason.isSingleCycleSeason() else rAlertMsgBlock.startIn.multi(), cycle=int2roman(cycleNumber), time=timeLeftStr)
                if not alertStr:
                    prevSeason = currSeason or self.__battleRoyaleController.getPreviousSeason()
                    if prevSeason is not None:
                        prevCycle = prevSeason.getLastActiveCycleInfo(currTime)
                        if prevCycle is not None:
                            cycleNumber = prevCycle.getEpicCycleNumber()
                            alertStr = backport.text(rAlertMsgBlock.noCycleMessage.single() if prevSeason.isSingleCycleSeason() else rAlertMsgBlock.noCycleMessage.multi(), cycle=int2roman(cycleNumber))
        return text_styles.vehicleStatusCriticalText(alertStr)

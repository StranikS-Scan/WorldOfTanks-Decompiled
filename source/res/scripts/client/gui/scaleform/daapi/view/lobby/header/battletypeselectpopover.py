# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
import BigWorld
from helpers import i18n
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.ARENAS import ARENAS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications import isStartingScriptDone
from gui.shared.utils.functions import makeTooltip
from gui.server_events import g_eventsCache
from predefined_hosts import g_preDefinedHosts

class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta):

    def __init__(self, _ = None):
        super(BattleTypeSelectPopover, self).__init__()

    def selectFight(self, actionName):
        battle_selector_items.getItems().select(actionName)

    def getTooltipData(self, itemData):
        if itemData is None:
            return ''
        elif itemData == PREBATTLE_ACTION_NAME.RANDOM_QUEUE:
            return TOOLTIPS.BATTLETYPES_STANDART
        elif itemData == PREBATTLE_ACTION_NAME.UNIT:
            return TOOLTIPS.BATTLETYPES_UNIT
        elif itemData == PREBATTLE_ACTION_NAME.COMPANY:
            return self.__getCompanyAvailabilityData()
        else:
            if itemData == PREBATTLE_ACTION_NAME.FORT:
                if not g_clanCache.isInClan:
                    return '#tooltips:fortification/disabled/no_clan'
                elif not isStartingScriptDone():
                    return '#tooltips:fortification/disabled/no_fort'
                else:
                    return TOOLTIPS.BATTLETYPES_FORTIFICATION
            else:
                if itemData == PREBATTLE_ACTION_NAME.TRAINING:
                    return TOOLTIPS.BATTLETYPES_TRAINING
                if itemData == PREBATTLE_ACTION_NAME.SPEC_BATTLE:
                    return TOOLTIPS.BATTLETYPES_SPEC
                if itemData == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL:
                    return TOOLTIPS.BATTLETYPES_BATTLETUTORIAL
                if itemData == PREBATTLE_ACTION_NAME.FALLOUT:
                    return TOOLTIPS.BATTLETYPES_FALLOUT
                if itemData == PREBATTLE_ACTION_NAME.SANDBOX:
                    return makeTooltip(TOOLTIPS.BATTLETYPES_BATTLETEACHING_HEADER, i18n.makeString(TOOLTIPS.BATTLETYPES_BATTLETEACHING_BODY, map1=i18n.makeString(ARENAS.C_100_THEPIT_NAME), map2=i18n.makeString(ARENAS.C_10_HILLS_NAME), battles=BATTLES_TO_SELECT_RANDOM_MIN_LIMIT))
            return ''

    def demoClick(self):
        demonstratorWindow = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.DEMONSTRATOR_WINDOW})
        if demonstratorWindow is not None:
            demonstratorWindow.onWindowClose()
        else:
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.DEMONSTRATOR_WINDOW), EVENT_BUS_SCOPE.LOBBY)
        return

    def update(self):
        if not self.isDisposed():
            self.as_updateS(*battle_selector_items.getItems().getVOs())

    def _populate(self):
        super(BattleTypeSelectPopover, self)._populate()
        self.update()

    def _dispose(self):
        super(BattleTypeSelectPopover, self)._dispose()

    def __getCompanyAvailabilityData(self):
        tooltipData = TOOLTIPS.BATTLETYPES_COMPANY
        battle = g_eventsCache.getCompanyBattles()
        header = i18n.makeString(tooltipData + '/header')
        body = i18n.makeString(tooltipData + '/body')
        serversList = []
        if battle.isValid() and battle.isDestroyingTimeCorrect():
            for peripheryID in battle.peripheryIDs:
                host = g_preDefinedHosts.periphery(peripheryID)
                if host is not None:
                    serversList.append(host.name)

            beginDate = ''
            endDate = ''
            serversString = ''
            if battle.startTime is not None:
                beginDate = i18n.makeString(TOOLTIPS.BATTLETYPES_AVAILABLETIME_SINCE, beginDate=BigWorld.wg_getShortDateFormat(battle.startTime))
            if battle.finishTime is not None:
                endDate = i18n.makeString(TOOLTIPS.BATTLETYPES_AVAILABLETIME_UNTIL, endDate=BigWorld.wg_getShortDateFormat(battle.finishTime))
            if serversList:
                serversString = i18n.makeString(TOOLTIPS.BATTLETYPES_AVAILABLETIME_SERVERS, servers=', '.join(serversList))
            if beginDate or endDate or serversString:
                restrictInfo = i18n.makeString(TOOLTIPS.BATTLETYPES_AVAILABLETIME, since=beginDate, until=endDate, servers=serversString)
                body = '%s\n\n%s' % (body, restrictInfo)
        return makeTooltip(header, body)

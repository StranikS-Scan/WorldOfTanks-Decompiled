# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
import BigWorld
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.ARENAS import ARENAS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.events import LoadViewEvent
from gui.shared.fortifications import isStartingScriptDone
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency, time_utils
from predefined_hosts import g_preDefinedHosts
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, _=None):
        super(BattleTypeSelectPopover, self).__init__()

    def selectFight(self, actionName):
        battle_selector_items.getItems().select(actionName)

    def getTooltipData(self, itemData, itemIsDisabled):
        if itemData is None:
            return
        else:
            tooltip = ''
            isSpecial = False
            if itemData == PREBATTLE_ACTION_NAME.RANDOM:
                tooltip = TOOLTIPS.BATTLETYPES_STANDART
            elif itemData == PREBATTLE_ACTION_NAME.RANKED:
                tooltip, isSpecial = self.__getRankedAvailabilityData()
            elif itemData == PREBATTLE_ACTION_NAME.E_SPORT:
                tooltip = TOOLTIPS.BATTLETYPES_UNIT
            elif itemData == PREBATTLE_ACTION_NAME.COMPANIES_LIST:
                tooltip = self.__getCompanyAvailabilityData()
            elif itemData == PREBATTLE_ACTION_NAME.FORT:
                if not self.lobbyContext.getServerSettings().isFortsEnabled():
                    tooltip = TOOLTIPS.BATTLETYPES_FORTIFICATION_DISABLED
                elif not g_clanCache.isInClan:
                    tooltip = '#tooltips:fortification/disabled/no_clan'
                elif not isStartingScriptDone():
                    tooltip = '#tooltips:fortification/disabled/no_fort'
                else:
                    tooltip = TOOLTIPS.BATTLETYPES_FORTIFICATION
            elif itemData == PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST:
                if not itemIsDisabled:
                    tooltip = TOOLTIPS.BATTLETYPES_STRONGHOLDS
                else:
                    tooltip = TOOLTIPS.HEADER_BUTTONS_FORTS_TURNEDOFF
            elif itemData == PREBATTLE_ACTION_NAME.TRAININGS_LIST:
                tooltip = TOOLTIPS.BATTLETYPES_TRAINING
            elif itemData == PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST:
                tooltip = TOOLTIPS.BATTLETYPES_SPEC
            elif itemData == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL:
                tooltip = TOOLTIPS.BATTLETYPES_BATTLETUTORIAL
            elif itemData == PREBATTLE_ACTION_NAME.FALLOUT:
                tooltip = TOOLTIPS.BATTLETYPES_FALLOUT
            elif itemData == PREBATTLE_ACTION_NAME.SANDBOX:
                tooltip = makeTooltip(TOOLTIPS.BATTLETYPES_BATTLETEACHING_HEADER, i18n.makeString(TOOLTIPS.BATTLETYPES_BATTLETEACHING_BODY, map1=i18n.makeString(ARENAS.C_100_THEPIT_NAME), map2=i18n.makeString(ARENAS.C_10_HILLS_NAME), battles=BATTLES_TO_SELECT_RANDOM_MIN_LIMIT))
            result = {'isSpecial': isSpecial,
             'tooltip': tooltip}
            return result

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
        battle = self.eventsCache.getCompanyBattles()
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

    def __getRankedAvailabilityData(self):
        if self.rankedController.isAvailable():
            return (TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO, True)
        else:
            tooltipData = TOOLTIPS.BATTLETYPES_RANKED
            header = i18n.makeString(tooltipData + '/header')
            bodyKey = tooltipData + '/body'
            body = i18n.makeString(bodyKey)
            nextSeason = self.rankedController.getNextSeason()
            if self.rankedController.isFrozen():
                additionalInfo = i18n.makeString(bodyKey + '/frozen')
            elif nextSeason is not None:
                additionalInfo = i18n.makeString(bodyKey + '/coming', date=BigWorld.wg_getShortDateFormat(time_utils.makeLocalServerTime(nextSeason.getStartDate())))
            else:
                additionalInfo = i18n.makeString(bodyKey + '/disabled')
            res = makeTooltip(header, '%s\n\n%s' % (body, additionalInfo))
            return (res, False)

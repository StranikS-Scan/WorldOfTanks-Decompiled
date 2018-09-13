# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
from collections import namedtuple
import types
import BigWorld
import constants
import ArenaType
import fortified_regions
from gui.prb_control import getBattleID
from predefined_hosts import g_preDefinedHosts
from constants import PREBATTLE_TYPE
from debug_utils import LOG_WARNING
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from CurrentVehicle import g_currentVehicle
from UnitBase import SORTIE_DIVISION
from gui import g_htmlTemplates, makeHtmlString, game_control
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters, fort_text
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeBuildingIndicatorsVO
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import findFirst, CONST_CONTAINER
from gui.shared.ClanCache import g_clanCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE
from gui.shared import g_eventsCache, g_itemsCache

class IgrTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(IgrTooltipData, self).__init__(context, TOOLTIP_TYPE.IGR)

    def getDisplayableData(self, *args):
        qLabels, qProgress = [], []
        if game_control.g_instance.igr.getRoomType() == constants.IGR_TYPE.PREMIUM:
            quests = g_eventsCache.getQuests()
            for q in quests.itervalues():
                if q.accountReqs.hasIGRCondition():
                    metaList = q.getBonuses('meta')
                    if len(metaList):
                        qLabels.append(metaList[0].format())
                    winCond = None
                    if q.postBattleCond.getConditions().getName() == 'and':
                        winCond = q.postBattleCond.getConditions().find('win')
                    isWin = winCond.getValue() if winCond is not None else False
                    battlesCond = q.bonusCond.getConditions().find('battles')
                    if battlesCond is not None:
                        curBattles, totalBattles = (0, 0)
                        progress = battlesCond.getProgressPerGroup()
                        if None in progress:
                            curBattles, totalBattles, _, _ = progress[None]
                        qProgress.append([curBattles, totalBattles, i18n.makeString('#quests:igr/tooltip/winsLabel') if isWin else i18n.makeString('#quests:igr/tooltip/battlesLabel')])

        template = g_htmlTemplates['html_templates:lobby/tooltips']['igr_quest']
        descriptionTemplate = 'igr_description' if len(qLabels) == 0 else 'igr_description_with_quests'
        igrPercent = (game_control.g_instance.igr.getXPFactor() - 1) * 100
        igrType = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == constants.IGR_TYPE.PREMIUM else 'basic')
        return {'title': i18n.makeString(TOOLTIPS.IGR_TITLE, igrIcon=icon),
         'description': makeHtmlString('html_templates:lobby/tooltips', descriptionTemplate, {'igrValue': '{0}%'.format(BigWorld.wg_getIntegralFormat(igrPercent))}),
         'quests': map(lambda i: i.format(**template.ctx), qLabels),
         'progressHeader': makeHtmlString('html_templates:lobby/tooltips', 'igr_progress_header', {}),
         'progress': qProgress}


class EfficiencyTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.EFFICIENCY)

    def getDisplayableData(self, _, value):
        return value


class SortieDivisionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SortieDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self):
        divisionsData = []
        divisions = makeDivisionData(I18N_FORTIFICATIONS.sortie_division_name)
        for division in divisions:
            divisionsData.append({'divisName': division['label'],
             'divisLevels': self.__getLevelsStr(division['level']),
             'divisBonus': self.__getBonusStr(division['profit']),
             'divisPlayers': self.__getPlayerLimitsStr(*self.__getPlayerLimits(division['level']))})

        return {'divisions': divisionsData}

    def __getPlayerLimits(self, divisionType):
        divisionIndex = SORTIE_DIVISION._ORDER.index(divisionType)
        division = SupportedRosterSettings.list(PREBATTLE_TYPE.SORTIE)[divisionIndex]
        return (division.getMinSlots(), division.getMaxSlots())

    def __getPlayerLimitsStr(self, minCount, maxCount):
        return fort_text.getText(fort_text.MAIN_TEXT, str(minCount) + ' - ' + str(maxCount))

    def __getLevelsStr(self, maxlvl):
        minLevel = 1
        minLevelStr = fort_formatters.getTextLevel(minLevel)
        maxLevelStr = fort_formatters.getTextLevel(maxlvl)
        return fort_text.getText(fort_text.MAIN_TEXT, minLevelStr + ' - ' + maxLevelStr)

    def __getBonusStr(self, bonus):
        text = (fort_text.PURPLE_TEXT, BigWorld.wg_getIntegralFormat(bonus) + ' ')
        icon = (fort_text.NUT_ICON,)
        return fort_text.concatStyles((text, icon))


class MapTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(MapTooltipData, self).__init__(context, TOOLTIP_TYPE.MAP)

    def getDisplayableData(self, arenaID):
        arenaType = ArenaType.g_cache[int(arenaID)]
        return {'mapName': i18n.makeString('#arenas:%s/name' % arenaType.geometryName),
         'gameplayName': i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName),
         'imageURL': '../maps/icons/map/%s.png' % arenaType.geometryName,
         'description': i18n.makeString('#arenas:%s/description' % arenaType.geometryName)}


class HistoricalAmmoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(HistoricalAmmoTooltipData, self).__init__(context, TOOLTIP_TYPE.HISTORICAL_AMMO)

    def getDisplayableData(self, battleID, vehicleID):
        battle = g_eventsCache.getHistoricalBattles().get(battleID)
        shellsItems = battle.getShellsLayout(int(vehicleID))
        priceString = battle.getShellsLayoutFormatedPrice(int(vehicleID), self.app.colorManager, True, True)
        data = {'price': priceString,
         'shells': []}
        shells = data['shells']
        for shell, count in shellsItems:
            shells.append({'id': str(shell.intCD),
             'type': shell.type,
             'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
             'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
             'count': count})

        return data


class HistoricalModulesTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(HistoricalModulesTooltipData, self).__init__(context, TOOLTIP_TYPE.HISTORICAL_MODULES)

    def getDisplayableData(self, battleID):
        templatePath = 'html_templates:lobby/historicalBattles/tooltips'
        template = 'moduleLabel'
        vehicle = g_currentVehicle.item
        battle = g_eventsCache.getHistoricalBattles().get(battleID)
        modules = battle.getModules(vehicle)
        data = {}
        if modules is not None:
            modulesData = []
            for item in modules.itervalues():
                modulesData.append({'type': item.itemTypeName,
                 'label': makeHtmlString(templatePath, template, {'type': item.userType,
                           'name': item.userName})})

            data = {'tankName': vehicle.userName,
             'modules': modulesData}
        return data


class SettingsControlTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SettingsControlTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, controlID):
        warningKey = '%s/warning' % controlID
        warning = i18n.makeString('#settings:%s' % warningKey)
        if warningKey == warning:
            warning = ''
        return {'name': i18n.makeString('#settings:%s' % controlID),
         'descr': i18n.makeString('#settings:%s/description' % controlID),
         'recommended': '',
         'status': {'level': 'warning',
                    'text': warning}}


class SettingsButtonTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SettingsButtonTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self):
        from ConnectionManager import connectionManager
        serverName = ''
        if connectionManager.peripheryID == 0:
            serverName = connectionManager.serverUserName
        else:
            hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
            for key, name, csisStatus, peripheryID in hostsList:
                if connectionManager.peripheryID == peripheryID:
                    serverName = name
                    break

        stats = None
        if constants.IS_SHOW_SERVER_STATS:
            stats = dict(game_control.g_instance.serverStats.getStats())
        return {'name': i18n.makeString(TOOLTIPS.HEADER_MENU_HEADER),
         'description': i18n.makeString(TOOLTIPS.HEADER_MENU_DESCRIPTION),
         'serverHeader': i18n.makeString(TOOLTIPS.HEADER_MENU_SERVER),
         'serverName': serverName,
         'playersOnServer': i18n.makeString(TOOLTIPS.HEADER_MENU_PLAYERSONSERVER),
         'servers': stats}


class ClanInfoTooltipData(ToolTipBaseData, FortViewHelper):

    def __init__(self, context):
        super(ClanInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, clanDBID):
        fortCtrl = g_clanCache.fortProvider.getController()
        isFortFrozen = False
        if clanDBID is None:
            fort = fortCtrl.getFort()
            fortDossier = fort.getFortDossier()
            battlesStats = fortDossier.getBattlesStats()
            isFortFrozen = self._isFortFrozen()
            clanName, clanMotto, clanTag = g_clanCache.clanName, '', g_clanCache.clanTag
            clanLvl = fort.level if fort is not None else 0
            homePeripheryID = fort.peripheryID
            playersAtClan, buildingsNum = len(g_clanCache.clanMembers), len(fort.getBuildingsCompleted())
            combatCount, winsEff, profitEff = battlesStats.getCombatCount(), battlesStats.getWinsEfficiency(), battlesStats.getProfitFactor()
            creationTime = fortDossier.getGlobalStats().getCreationTime()
            defence, vacation, offDay = fort.getDefencePeriod(), fort.getVacationDate(), fort.getOffDay()
        elif type(clanDBID) in (types.IntType, types.LongType, types.FloatType):
            clanInfo = fortCtrl.getPublicInfoCache().getItem(clanDBID)
            if clanInfo is None:
                LOG_WARNING('Requested clan info is empty', clanDBID)
                return
            clanName, clanMotto = clanInfo.getClanName(), ''
            clanTag, clanLvl = '[%s]' % clanInfo.getClanAbbrev(), clanInfo.getLevel()
            homePeripheryID = clanInfo.getHomePeripheryID()
            playersAtClan, buildingsNum = (None, None)
            combatCount, winsEff, profitEff = clanInfo.getBattleCount(), None, clanInfo.getProfitFactor()
            creationTime = None
            defence, offDay = clanInfo.getDefencePeriod(), clanInfo.getOffDay()
            vacation = clanInfo.getVacationPeriod()
        else:
            LOG_WARNING('Invalid clanDBID identifier', clanDBID, type(clanDBID))
            return
        topStats = []
        host = g_preDefinedHosts.periphery(homePeripheryID)
        if host is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_HOMEPEREPHIRY), host.name))
        if playersAtClan is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PLAYERSATCLAN), playersAtClan))
        if buildingsNum is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_BUILDINGSATFORTIFICATION), buildingsNum))
        if combatCount is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_FIGHTSFORFORTIFICATION), combatCount))
        topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_WINPERCENTAGE), '--' if winsEff is None else BigWorld.wg_getNiceNumberFormat(winsEff)))
        if profitEff is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PROFITPERCENTAGE), BigWorld.wg_getNiceNumberFormat(profitEff)))
        if creationTime is not None:
            fortCreationData = fort_text.getText(fort_text.NEUTRAL_TEXT, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPCLANINFO_FORTCREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(creationTime)))
        else:
            fortCreationData = None

        def _makeLabels(stats, itemIdx):
            return '\n'.join((str(a[itemIdx]) for a in stats))

        infoTexts, protectionHeader = [], ''
        if defence[0]:
            if isFortFrozen:
                protectionHeader = fort_text.getText(fort_text.ERROR_TEXT, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIMESTOPPED))
            else:
                protectionHeader = fort_text.getText(fort_text.HIGH_TITLE, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIME))
            statsValueColor = fort_text.DISABLE_TEXT if isFortFrozen else fort_text.STATS_TEXT
            defencePeriodString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortTimeFormat(defence[0]), finishTime=BigWorld.wg_getShortTimeFormat(defence[1]))
            defencePeriodString = fort_text.getText(statsValueColor, defencePeriodString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSEHOUR, period=defencePeriodString))
            if offDay > -1:
                dayOffString = i18n.makeString('#menu:dateTime/weekDays/full/%d' % offDay)
            else:
                dayOffString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NODAYOFF)
            dayOffString = fort_text.getText(statsValueColor, dayOffString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DAYOFF, dayOff=dayOffString))
            if vacation[0] and vacation[1]:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortDateFormat(vacation[0]), finishTime=BigWorld.wg_getShortDateFormat(vacation[1]))
            else:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NOVACATION)
            vacationString = fort_text.getText(statsValueColor, vacationString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_VACATION, period=vacationString))
        return {'headerText': fort_text.getText(fort_text.HIGH_TITLE, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_HEADER, clanTag=clanTag, clanLevel=fort_formatters.getTextLevel(clanLvl))),
         'fullClanName': fort_text.getText(fort_text.NEUTRAL_TEXT, clanName),
         'sloganText': fort_text.getText(fort_text.STANDARD_TEXT, clanMotto),
         'infoDescriptionTopText': fort_text.getText(fort_text.MAIN_TEXT, _makeLabels(topStats, 0)),
         'infoTopText': fort_text.getText('statsText', _makeLabels(topStats, 1)),
         'infoDescriptionBottomText': '',
         'infoBottomText': '',
         'protectionHeaderText': protectionHeader,
         'infoText': makeHtmlString('html_templates:lobby/fortifications/tooltips/defense_description', 'main', {'text': '\n'.join(infoTexts)}),
         'fortCreationDate': fortCreationData}


_battleStatus = namedtuple('_battleStatus', ('level', 'msg', 'color', 'prefix'))

class ToolTipFortBuildingData(ToolTipBaseData, FortViewHelper):

    class BATTLE_STATUSES(CONST_CONTAINER):
        NO_BATTLE = _battleStatus('warning', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_WASNOTBATTLE, fort_text.PURPLE_TEXT, '')
        LOST = _battleStatus('critical', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_DEFEAT, fort_text.ERROR_TEXT, '-')
        WON = _battleStatus('info', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_VICTORY, fort_text.SUCCESS_TEXT, '+')

    def __init__(self, context):
        super(ToolTipFortBuildingData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, buildingUID, isMine):
        ms = i18n.makeString
        fort = self.fortCtrl.getFort()
        battleID = getBattleID()
        battle = fort.getBattle(battleID)
        buildingTypeID = self.UI_BUILDINGS_BIND.index(buildingUID)
        if battle.isDefence():
            isAttack = not isMine
        else:
            isAttack = isMine
        if isAttack:
            buildingsList = battle.getAttackerBuildList()
            buildingsFullList = battle.getAttackerFullBuildList()
        else:
            buildingsList = battle.getDefenderBuildList()
            buildingsFullList = battle.getDefenderFullBuildList()
        buildingFullData = findFirst(lambda x: x[0] == buildingTypeID, buildingsFullList)
        _, status, buildingLevel, hpVal, defResVal = buildingFullData
        isReadyForBattle = status == constants.FORT_BUILDING_STATUS.READY_FOR_BATTLE
        buildingData = None
        resCount, arenaTypeID = (None, None)
        if isReadyForBattle:
            buildingData = findFirst(lambda x: x[0] == buildingTypeID, buildingsList)
            _, resCount, arenaTypeID = buildingData
        _, status, buildingLevel, hpVal, defResVal = buildingFullData
        progress = self._getProgress(buildingTypeID, buildingLevel)
        buildingLevelData = fortified_regions.g_cache.buildings[buildingTypeID].levels[buildingLevel]
        hpTotalVal = buildingLevelData.hp
        maxDefResVal = buildingLevelData.storage
        buildingName = fort_text.getText(fort_text.HIGH_TITLE, ms(FORT.buildings_buildingname(buildingUID)))
        currentMapTxt = None
        buildingLevelTxt = fort_text.getText(fort_text.MAIN_TEXT, ms(FORT.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=str(fort_formatters.getTextLevel(buildingLevel))))
        descrActionTxt = None
        statusTxt = None
        statusLevel = None
        indicatorsModel = None
        infoMessage = None
        if status == constants.FORT_BUILDING_STATUS.LOW_LEVEL:
            minBuildingLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
            minLevel = fort_formatters.getTextLevel(1)
            maxLevel = fort_formatters.getTextLevel(minBuildingLevel - 1)
            infoMessage = ms(FORT.TOOLTIPBUILDINGINFO_LOWLEVELMESSAGE, minLevel=minLevel, maxLevel=maxLevel)
        else:
            indicatorsModel = makeBuildingIndicatorsVO(buildingLevel, progress, hpVal, hpTotalVal, defResVal, maxDefResVal)
            if isReadyForBattle:
                lootedBuildings = battle.getLootedBuildList()
                battleStatus = self.BATTLE_STATUSES.NO_BATTLE
                if (buildingData, isAttack) in lootedBuildings:
                    battleStatus = self.BATTLE_STATUSES.LOST
                    if battle.isDefence() and isAttack or not battle.isDefence() and not isAttack:
                        battleStatus = self.BATTLE_STATUSES.WON
                arenaType = ArenaType.g_cache.get(arenaTypeID)
                prefix = fort_text.getText(fort_text.STANDARD_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_MEP_MAPPREFIX))
                mapName = fort_text.getText(fort_text.NEUTRAL_TEXT, arenaType.name)
                currentMapTxt = prefix + mapName
                statusLevel = battleStatus.level
                statusTxt = ms(battleStatus.msg)
                defResStatusTxt = fort_text.concatStyles(((battleStatus.color, '%s %s' % (battleStatus.prefix, BigWorld.wg_getIntegralFormat(resCount))), (fort_text.NUT_ICON,)))
                descrActionTxt = fort_text.getText(fort_text.MAIN_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_DESCRACTION))
                descrActionTxt = descrActionTxt % {'value': defResStatusTxt}
            else:
                minResCount = hpTotalVal * 0.2
                minResStatusTxt = fort_text.concatStyles(((fort_text.NEUTRAL_TEXT, BigWorld.wg_getIntegralFormat(minResCount)), (fort_text.NUT_ICON,)))
                infoMessage = fort_text.getText(fort_text.MAIN_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_DESTROYEDMESSAGE))
                infoMessage = infoMessage % {'value': minResStatusTxt}
        result = {'buildingUID': buildingUID,
         'buildingName': buildingName,
         'currentMap': currentMapTxt,
         'buildingLevel': buildingLevelTxt,
         'descrAction': descrActionTxt,
         'statusMsg': statusTxt,
         'statusLevel': statusLevel,
         'indicatorModel': indicatorsModel,
         'isAvailable': isReadyForBattle,
         'infoMessage': infoMessage}
        return result


class ActionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, type, key, newPrice, oldPrice, isBuying, forCredits = False):
        actionNames = None
        body = ''
        descr = ''
        newCredits, newGold = newPrice
        oldCredits, oldGold = oldPrice
        newPriceValue = 0
        newPriceCurrency = None
        oldPriceValue = 0
        oldPriceCurrency = None
        if type == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            actions = g_eventsCache.getEconomicsAction(key)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
                if key == 'freeXPToTManXPRate':
                    newPriceCurrency = oldPriceCurrency = 'freeXp'
        elif type == ACTION_TOOLTIPS_TYPE.ITEM:
            item = g_itemsCache.items.getItemByCD(int(key))
            useGold = item.isPremium and not forCredits and isBuying
            newPriceValue = newGold if useGold else newCredits
            newPriceCurrency = 'gold' if useGold else 'credits'
            oldPriceValue = oldGold if useGold else oldCredits
            oldPriceCurrency = 'gold' if useGold else 'credits'
            actions = g_eventsCache.getItemAction(item, True, forCredits)
            if item.itemTypeID in (GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT) and item.isPremium and not useGold:
                actions += g_eventsCache.getEconomicsAction('exchangeRateForShellsAndEqs')
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isPremium and not isBuying:
                actions += g_eventsCache.getEconomicsAction('exchangeRate')
            if actions:
                actionNames = map(lambda x: x[1], actions)
            if not isBuying:
                sellingActions = g_eventsCache.getItemAction(item, False, forCredits)
                if sellingActions:
                    actionNames = map(lambda x: x[1], sellingActions)

                    def filter(item):
                        (forGold, _), _ = item
                        return forGold

                    sellForGoldAction = findFirst(filter, sellingActions)
                    if sellForGoldAction:
                        newPriceValue = newGold
                        newPriceCurrency = 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.CAMOUFLAGE:
            intCD, type = cPickle.loads(key)
            actions = g_eventsCache.getCamouflageAction(intCD) + g_eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.EMBLEMS:
            group, type = cPickle.loads(key)
            actions = g_eventsCache.getEmblemsAction(group) + g_eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.AMMO:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = []
            for shell in item.gun.defaultAmmo:
                actions += g_eventsCache.getItemAction(shell, isBuying, True)

            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits
                oldPriceValue = oldCredits
                newPriceCurrency = oldPriceCurrency = 'credits'
        actionNames = set(actionNames)
        if actionNames:
            formatedNewPrice = makeHtmlString('html_templates:lobby/quests/actions', newPriceCurrency, {'value': BigWorld.wg_getGoldFormat(newPriceValue)})
            formatedOldPrice = makeHtmlString('html_templates:lobby/quests/actions', oldPriceCurrency, {'value': BigWorld.wg_getGoldFormat(oldPriceValue)})
            body = i18n.makeString('#tooltips:actionPrice/body', oldPrice=formatedOldPrice, newPrice=formatedNewPrice)

            def mapName(item):
                action = g_eventsCache.getActions().get(item)
                return i18n.makeString('#tooltips:actionPrice/actionName', actionName=action.getUserName())

            actionUserNames = ', '.join(map(mapName, actionNames))
            if len(actionNames) > 1:
                descr = i18n.makeString('#tooltips:actionPrice/forActions', actions=actionUserNames)
            else:
                descr = i18n.makeString('#tooltips:actionPrice/forAction', action=actionUserNames)
        return {'name': i18n.makeString('#tooltips:actionPrice/header'),
         'descr': '%s\n%s' % (body, descr)}

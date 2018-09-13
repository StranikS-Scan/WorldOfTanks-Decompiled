# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
import BigWorld
from constants import PREBATTLE_TYPE
import ArenaType
from CurrentVehicle import g_currentVehicle
from UnitBase import SORTIE_DIVISION
import constants
import gui
from gui import game_control, makeHtmlString
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters, fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_text import getText, HIGH_TITLE, NEUTRAL_TEXT, STANDARD_TEXT, MAIN_TEXT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import findFirst
from gui.shared.ClanCache import g_clanCache
from helpers import i18n
from helpers.i18n import makeString
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE
from gui.shared import g_eventsCache, g_itemsCache
from gui.shared.fortifications.fort_helpers import fortProviderProperty, fortCtrlProperty

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
                        qProgress.append([curBattles, totalBattles, makeString('#quests:igr/tooltip/winsLabel') if isWin else makeString('#quests:igr/tooltip/battlesLabel')])

        template = gui.g_htmlTemplates['html_templates:lobby/tooltips']['igr_quest']
        descriptionTemplate = 'igr_description' if len(qLabels) == 0 else 'igr_description_with_quests'
        igrPercent = (game_control.g_instance.igr.getXPFactor() - 1) * 100
        igrType = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == constants.IGR_TYPE.PREMIUM else 'basic')
        return {'title': i18n.makeString(TOOLTIPS.IGR_TITLE, igrIcon=icon),
         'description': gui.makeHtmlString('html_templates:lobby/tooltips', descriptionTemplate, {'igrValue': '{0}%'.format(BigWorld.wg_getIntegralFormat(igrPercent))}),
         'quests': map(lambda i: i.format(**template.ctx), qLabels),
         'progressHeader': gui.makeHtmlString('html_templates:lobby/tooltips', 'igr_progress_header', {}),
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
        text = (fort_text.MAIN_TEXT, str(minCount) + ' - ' + str(maxCount))
        icon = (fort_text.HUMANS,)
        return fort_text.concatStyles((text, icon))

    def __getLevelsStr(self, maxlvl):
        minLevel = 1
        minLevelStr = fort_formatters.getTextLevel(minLevel)
        maxLevelStr = fort_formatters.getTextLevel(maxlvl)
        return getText(fort_text.MAIN_TEXT, minLevelStr + ' - ' + maxLevelStr)

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


class ClanInfoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ClanInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, *args, **kwargs):
        fort = self.fortCtrl.getFort()
        fortLevel = fort_formatters.getTextLevel(fort.level)
        headerText = i18n.makeString(TOOLTIPS.TOOLTIPCLANINFO_FORTIFICATION_HEADER, clanTag=str(g_clanCache.clanTag), fortLevel=str(fortLevel))
        headerText = getText(HIGH_TITLE, headerText)
        fullClanName = getText(NEUTRAL_TEXT, str(g_clanCache.clanFullName))
        creationTime = fort.getFortDossier().getGlobalStats().getCreationTime()
        creationDate = i18n.makeString(TOOLTIPS.TOOLTIPCLANINFO_FORTIFICATION_FORTCREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(creationTime))
        creationDate = getText(MAIN_TEXT, creationDate)
        data = {'headerText': headerText,
         'fullClanName': fullClanName,
         'infoText': getText(STANDARD_TEXT, i18n.makeString(TOOLTIPS.TOOLTIPCLANINFO_FORTIFICATION_DESCRIPTION)),
         'fortCreationDate': creationDate}
        return data

    @fortProviderProperty
    def fortProvider(self):
        return None

    @fortCtrlProperty
    def fortCtrl(self):
        return None


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

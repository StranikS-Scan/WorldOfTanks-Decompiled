# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
import types
import math
import ResMgr
from operator import methodcaller, itemgetter
import BigWorld
import constants
import ArenaType
import fortified_regions
from shared_utils import findFirst, CONST_CONTAINER
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters as clans_fmts
from gui.clans.clan_controller import g_clanCtrl
from gui.clans.items import formatField
from gui.clubs import formatters as club_fmts
from gui.clubs.ClubsController import g_clubsCtrl
from gui.clubs.settings import getLadderChevron256x256, getPointsToNextDivision
from gui.prb_control.prb_getters import getBattleID
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.time_formatters import getTimeLeftStr
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.view_helpers import UsersInfoHelper
from gui.LobbyContext import g_lobbyContext
from gui.shared.tooltips import efficiency
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter, makeClanFullName, makeClubFullName, makeContactStatusDescription
from predefined_hosts import g_preDefinedHosts
from constants import PREBATTLE_TYPE, WG_GAMES
from debug_utils import LOG_WARNING
from helpers import i18n, time_utils, html, int2roman
from helpers.i18n import makeString as ms, makeString
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from CurrentVehicle import g_currentVehicle
from UnitBase import SORTIE_DIVISION
from gui import g_htmlTemplates, makeHtmlString, game_control
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeBuildingIndicatorsVO
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE, ToolTipMethodField, ToolTipParameterField, ToolTipData, ToolTipAttrField
from gui.shared import g_itemsCache
from gui.server_events import g_eventsCache
from gui.Scaleform.daapi.view.lobby.customization import CAMOUFLAGES_KIND_TEXTS, CAMOUFLAGES_NATIONS_TEXTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesSortieListView import formatGuiTimeLimitStr
from items import vehicles
from messenger.storage import storage_getter
from messenger.m_constants import USER_TAG

class FortOrderParamField(ToolTipParameterField):

    def _getValue(self):
        return [self._tooltip.item.getParams()]


class IgrTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(IgrTooltipData, self).__init__(context, TOOLTIP_TYPE.IGR)

    def getDisplayableData(self, *args):
        qLabels, qProgress = [], []
        premVehQuests = []
        if game_control.g_instance.igr.getRoomType() in (constants.IGR_TYPE.PREMIUM, constants.IGR_TYPE.BASE):
            quests = g_eventsCache.getQuests()
            for q in quests.itervalues():
                if game_control.g_instance.igr.getRoomType() == constants.IGR_TYPE.PREMIUM:
                    template = g_htmlTemplates['html_templates:lobby/tooltips']['igr_quest']
                    if q.accountReqs.hasIGRCondition() and not q.hasPremIGRVehBonus():
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
                if q.hasPremIGRVehBonus():
                    metaList = q.getBonuses('meta')
                    leftTime = time_utils.getTimeDeltaFromNow(q.getFinishTime())
                    if len(metaList) and leftTime > 0:
                        header = makeHtmlString('html_templates:lobby/tooltips', 'prem_igr_veh_quest_header', ctx={'qLabel': metaList[0].format()})
                        text = i18n.makeString('#tooltips:vehicleIgr/specialAbility')
                        localization = '#tooltips:vehicleIgr/%s'
                        actionLeft = getTimeLeftStr(localization, leftTime, timeStyle=text_styles.stats)
                        text += '\n' + actionLeft
                        premVehQuests.append({'header': header,
                         'descr': text})

        descriptionTemplate = 'igr_description' if len(qLabels) == 0 else 'igr_description_with_quests'
        igrPercent = (game_control.g_instance.igr.getXPFactor() - 1) * 100
        igrType = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == constants.IGR_TYPE.PREMIUM else 'basic')
        return {'title': i18n.makeString(TOOLTIPS.IGR_TITLE, igrIcon=icon),
         'description': makeHtmlString('html_templates:lobby/tooltips', descriptionTemplate, {'igrValue': '{0}%'.format(BigWorld.wg_getIntegralFormat(igrPercent))}),
         'quests': map(lambda i: i.format(**template.ctx), qLabels),
         'progressHeader': makeHtmlString('html_templates:lobby/tooltips', 'igr_progress_header', {}),
         'progress': qProgress,
         'premVehQuests': premVehQuests}


_DEFAULT_MARGINS = {'top': 13,
 'left': 18,
 'bottom': 21,
 'right': 18}
_DEFAULT_MARGIN_AFTER_BLOCK = 10
_DEFAULT_MARGIN_AFTER_SEPARATOR = 17

class BlocksTooltipData(ToolTipBaseData):

    def __init__(self, context, toolTipType):
        super(BlocksTooltipData, self).__init__(context, toolTipType)
        self.__contentMargin = _DEFAULT_MARGINS.copy()
        self.__marginAfterBlock = _DEFAULT_MARGIN_AFTER_BLOCK
        self.__marginAfterSeparator = _DEFAULT_MARGIN_AFTER_SEPARATOR
        self.__width = 0

    def _getContentMargin(self):
        return self.__contentMargin

    def _setContentMargin(self, top = None, left = None, bottom = None, right = None):
        if top is not None:
            self.__contentMargin['top'] = top
        if left is not None:
            self.__contentMargin['left'] = left
        if bottom is not None:
            self.__contentMargin['bottom'] = bottom
        if right is not None:
            self.__contentMargin['right'] = right
        return

    def _setMargins(self, afterBlock = _DEFAULT_MARGIN_AFTER_BLOCK, afterSeparator = _DEFAULT_MARGIN_AFTER_SEPARATOR):
        self.__marginAfterBlock = afterBlock
        self.__marginAfterSeparator = afterSeparator

    def _setWidth(self, width):
        self.__width = width

    def _getWidth(self):
        return self.__width

    def _packBlocks(self, *args, **kwargs):
        return []

    def getDisplayableData(self, *args, **kwargs):
        return {'blocksData': self._packBlocks(*args, **kwargs),
         'marginAfterBlock': self.__marginAfterBlock,
         'marginAfterSeparator': self.__marginAfterSeparator,
         'contentMargin': self._getContentMargin(),
         'width': self._getWidth()}


class EfficiencyTooltipData(BlocksTooltipData):
    _packers = {BATTLE_EFFICIENCY_TYPES.ARMOR: efficiency.ArmorItemPacker,
     BATTLE_EFFICIENCY_TYPES.DAMAGE: efficiency.DamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: efficiency.KillItemPacker,
     BATTLE_EFFICIENCY_TYPES.DETECTION: efficiency.DetectionItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: efficiency.AssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.CRITS: efficiency.CritsItemPacker,
     BATTLE_EFFICIENCY_TYPES.CAPTURE: efficiency.CaptureItemPacker,
     BATTLE_EFFICIENCY_TYPES.DEFENCE: efficiency.DefenceItemPacker}

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.EFFICIENCY)

    def _packBlocks(self, data):
        if data is not None and data.type in self._packers:
            return self._packers[data.type]().pack(data.toDict())
        else:
            return []
            return


_ENV_TOOLTIPS_PATH = '#environment_tooltips:%s'
_ENV_IMAGES_PATH = '../maps/icons/environmentTooltips/%s.png'
_ENV_IMAGES_PATH_FOR_CHECK = 'gui/maps/icons/environmentTooltips/%s.png'

class EnvironmentTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EnvironmentTooltipData, self).__init__(context, None)
        return

    def getDisplayableData(self, tooltipId):
        title = _ENV_TOOLTIPS_PATH % ('%s/title' % tooltipId)
        desc = _ENV_TOOLTIPS_PATH % ('%s/desc' % tooltipId)
        icon = None
        if ResMgr.isFile(_ENV_IMAGES_PATH_FOR_CHECK % tooltipId):
            icon = _ENV_IMAGES_PATH % tooltipId
        return {'title': title,
         'text': desc,
         'icon': icon}


class ContactTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ContactTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTACT)
        self.__converter = ContactConverter()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def getDisplayableData(self, dbID, defaultName):
        userEntity = self.usersStorage.getUser(dbID)
        if userEntity is None:
            return {'userProps': {'userName': defaultName}}
        else:
            commonGuiData = self.__converter.makeVO(userEntity, False)
            tags = userEntity.getTags()
            resourceID = commonGuiData['resource']
            if resourceID == WG_GAMES.TANKS:
                statusDescription = makeContactStatusDescription(userEntity.isOnline(), tags, userEntity.getClientInfo())
            else:
                statusDescription = makeString('#tooltips:Contact/resource/%s' % resourceID)
            commonGuiData['statusDescription'] = statusDescription
            units = []
            currentUnit = ''
            region = g_lobbyContext.getRegionCode(userEntity.getID())
            if region is not None:
                currentUnit += self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_HOMEREALM, region)
            clanAbbrev = userEntity.getClanAbbrev()
            if clanAbbrev:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_CLAN, '[{0}]'.format(clanAbbrev))
            if currentUnit != '':
                units.append(currentUnit)
            currentUnit = ''
            if USER_TAG.IGNORED in tags:
                currentUnit += self.__makeIconUnitStr('contactIgnored.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_IGNORED)
            elif USER_TAG.SUB_TO not in tags and (userEntity.isFriend() or USER_TAG.SUB_PENDING_IN in tags):
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeIconUnitStr('contactConfirmNeeded.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_PENDINGFRIENDSHIP)
            if USER_TAG.BAN_CHAT in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeIconUnitStr('contactMsgsOff.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_CHATBAN)
            if USER_TAG.REFERRER in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeReferralStr(TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_RECRUITER)
            elif USER_TAG.REFERRAL in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeReferralStr(TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_RECRUIT)
            if currentUnit != '':
                units.append(currentUnit)
            groupsStr = ''
            userGroups = userEntity.getGroups()
            if len(userGroups) > 0:
                groupsStr += ', '.join(map(lambda group: html.escape(group), userGroups))
            if clanAbbrev and USER_TAG.CLAN_MEMBER in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeClanFullName(clanAbbrev)
            if USER_TAG.CLUB_MEMBER in tags:
                clubName = self.playerCtx.getMyClubName()
                if clubName:
                    groupsStr += self.__addComma(groupsStr)
                    groupsStr += makeClubFullName(clubName)
            if USER_TAG.IGNORED in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_IGNORED)
            if USER_TAG.SUB_PENDING_IN in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_FRIENDSHIPREQUEST)
            if groupsStr != '':
                units.append(self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_GROUPS, groupsStr + '.'))
            if len(units) > 0:
                commonGuiData['units'] = units
            return commonGuiData

    def __makeUnitStr(self, descr, val):
        return makeHtmlString('html_templates:contacts/contact', 'tooltipUnitTxt', {'descr': makeString(descr),
         'value': val})

    def __makeIconUnitStr(self, icon, descr):
        return self.__converter.makeIconTag(iconPath=icon) + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': makeString(descr)})

    def __makeReferralStr(self, descr):
        return self.__converter.makeIconTag(key='referrTag') + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': makeString(descr)})

    def __addBR(self, currentUnit):
        if currentUnit != '':
            return '<br/>'
        return ''

    def __addComma(self, currStr):
        if currStr != '':
            return ', '
        return ''


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
        return text_styles.main(str(minCount) + ' - ' + str(maxCount))

    def __getLevelsStr(self, maxlvl):
        minLevel = 1
        minLevelStr = fort_formatters.getTextLevel(minLevel)
        maxLevelStr = fort_formatters.getTextLevel(maxlvl)
        return text_styles.main(minLevelStr + ' - ' + maxLevelStr)

    def __getBonusStr(self, bonus):
        return ''.join((text_styles.defRes(BigWorld.wg_getIntegralFormat(bonus) + ' '), icons.nut()))


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
        return {'price': '0',
         'shells': []}


class HistoricalModulesTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(HistoricalModulesTooltipData, self).__init__(context, TOOLTIP_TYPE.HISTORICAL_MODULES)

    def getDisplayableData(self, battleID):
        vehicle = g_currentVehicle.item
        return {'tankName': vehicle.userName,
         'modules': []}


class SettingsControlTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SettingsControlTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, controlID):
        result = {}
        key = '#settings:%s/name' % controlID
        if i18n.doesTextExist(key):
            result['header'] = i18n.makeString(key)
        else:
            result['header'] = i18n.makeString('#settings:%s' % controlID)
        result['body'] = i18n.makeString('#settings:%s/description' % controlID)
        key = '#settings:%s/warning' % controlID
        if i18n.doesTextExist(key):
            result['attention'] = i18n.makeString(key)
        return result


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

        serversStats = None
        if constants.IS_SHOW_SERVER_STATS:
            serversStats, _ = game_control.g_instance.serverStats.getFormattedStats()
        return {'name': i18n.makeString(TOOLTIPS.HEADER_MENU_HEADER),
         'description': i18n.makeString(TOOLTIPS.HEADER_MENU_DESCRIPTION),
         'serverHeader': i18n.makeString(TOOLTIPS.HEADER_MENU_SERVER),
         'serverName': serverName,
         'playersOnServer': i18n.makeString(TOOLTIPS.HEADER_MENU_PLAYERSONSERVER),
         'serversStats': serversStats}


class CustomizationItemTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CustomizationItemTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def _processVehiclesList(self, vehIntCDs):
        vehStrList = []
        for intCD in vehIntCDs:
            vehicle = vehicles.getVehicleType(int(intCD))
            if vehicle and VEHICLE_TAGS.SECRET not in vehicle.tags:
                vehStrList.append(vehicle.shortUserString)

        return vehStrList

    def getDisplayableData(self, type, id, nationId, timeLeft, isPermanent = None, value = None, isUsed = False, boundVehicle = None, boundToCurrentVehicle = False):
        ms = i18n.makeString
        item = self._context.buildItem(nationId, id, type)
        headerText = ''
        typeText = ''
        descriptionText = ''
        allow = None
        deny = None
        usageStr = None
        allowStr = None
        denyStr = None
        footerStr = ''
        footerList = []
        if timeLeft >= 0:
            timeLeftText = self.__getTimeLeftText(timeLeft, isUsed)
            timeLeftText = text_styles.main(timeLeftText)
        else:
            timeLeftText = ''
        if isPermanent and value > 1:
            footerList.append(ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_STORED, quantity=value))
        if type == CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE:
            headerText = item['description'] + '/label'
            allow = item['allow']
            deny = item['deny']
            typeText = ms(VEHICLE_CUSTOMIZATION.CAMOUFLAGE) + ' ' + ms(CAMOUFLAGES_KIND_TEXTS[item['kind']])
            descriptionText = text_styles.standard(ms(item['description'] + '/description'))
        elif type == CUSTOMIZATION_ITEM_TYPE.EMBLEM:
            groupName, _, _, _, emblemName, _, _, _, allow, deny = item
            groups, _, _ = vehicles.g_cache.playerEmblems()
            _, group, _, _, _, _ = groups.get(groupName)
            headerText = emblemName
            typeText = ms(VEHICLE_CUSTOMIZATION.EMBLEM) + ' ' + ms(group)
            descriptionText = ''
        elif type == CUSTOMIZATION_ITEM_TYPE.INSCRIPTION:
            groupName, _, _, _, inscriptionName, _, _, _, allow, deny = item
            groups = vehicles.g_cache.customization(nationId).get('inscriptionGroups', {})
            _, group, _, _, _ = groups.get(groupName)
            headerText = inscriptionName
            typeText = ms(VEHICLE_CUSTOMIZATION.INSCRIPTION) + ' ' + ms(group)
            descriptionText = ''
        allow = self._processVehiclesList(allow)
        deny = self._processVehiclesList(deny)
        if boundVehicle is None and allow and len(allow) > 0:
            allowStr = ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_EXACTVEHICLE, vehicle=', '.join(allow))
        if boundVehicle is None and deny and len(deny) > 0:
            denyStr = ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_DENYVEHICLE, vehicle=', '.join(deny))
        if boundToCurrentVehicle:
            usageStr = text_styles.stats(ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_CURRENTVEHICLE))
        elif boundVehicle:
            vehicle = vehicles.getVehicleType(int(boundVehicle))
            usageStr = text_styles.stats(ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_EXACTVEHICLE, vehicle=vehicle.shortUserString))
        elif type != CUSTOMIZATION_ITEM_TYPE.EMBLEM and not allowStr:
            usageStr = text_styles.stats(ms(CAMOUFLAGES_NATIONS_TEXTS[nationId]))
        if usageStr:
            footerList.append(usageStr)
        if allowStr:
            footerList.append(allowStr)
        if denyStr:
            footerList.append(denyStr)
        if len(footerList):
            footerStr = text_styles.stats('\n'.join(footerList))
        return {'header': text_styles.highTitle(ms(headerText)),
         'kind': text_styles.main(typeText),
         'description': descriptionText,
         'timeLeft': timeLeftText,
         'vehicleType': footerStr}

    def __getTimeLeftText(self, timeLeft, isUsed):
        ms = i18n.makeString
        result = ''
        if timeLeft > 0:
            secondsInDay = 86400
            secondsInHour = 3600
            secondsInMinute = 60
            if timeLeft > secondsInDay:
                timeLeft = int(math.ceil(timeLeft / secondsInDay))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_DAYS)
            elif timeLeft > secondsInHour:
                timeLeft = int(math.ceil(timeLeft / secondsInHour))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_HOURS)
            else:
                timeLeft = int(math.ceil(timeLeft / secondsInMinute))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_MINUTES)
            result = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_USED if isUsed else VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL, time=timeLeft, dimension=dimension)
        elif not timeLeft:
            result = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_INFINITY)
        return result


class ClanCommonInfoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ClanCommonInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.CLAN_PROFILE)
        self.__usersInfoHelper = UsersInfoHelper()

    def getDisplayableData(self, clanDBID):
        data = g_clanCtrl.getClanCommonData(clanDBID)
        if data is None:
            return {}
        else:
            rating = formatField(getter=data.getRating, formatter=BigWorld.wg_getIntegralFormat)
            count = formatField(getter=data.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat)
            wins = formatField(getter=data.getWinsRatio, formatter=lambda value: BigWorld.wg_getNiceNumberFormat(value) + '%')
            exp = formatField(getter=data.getAvgExp, formatter=BigWorld.wg_getIntegralFormat)
            statValues = text_styles.stats('\n'.join((rating,
             count,
             wins,
             exp)))
            abbrev = formatField(getter=data.getAbbrev)
            name = formatField(getter=data.getName)
            motto = formatField(getter=data.getMotto)
            userName = '{} {}'.format(self.__usersInfoHelper.getUserName(data.getLeaderDbID()), clans_fmts.getClanAbbrevString(abbrev))
            isActive = text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_NO))
            if data.isActive():
                isActive = text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_YES))
            return {'clanName': i18n.makeString(TOOLTIPS.CLANCOMMONINFO_CLANNAME, clanAbbrev=abbrev, clanName=name),
             'slogan': text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_SLOGAN, slogan=text_styles.standard(motto))),
             'statValues': statValues,
             'statDescriptions': text_styles.concatStylesToMultiLine(text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_STATRATING)), text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_STATBATTLESCOUNT)), text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_STATWINSPERCENT)), text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_STATAVGEXP))),
             'bottomInfoText': text_styles.concatStylesToMultiLine(text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_COMMANDER, commanderName=text_styles.stats(userName))), text_styles.main(i18n.makeString(TOOLTIPS.CLANCOMMONINFO_ACTIVITY, activity=text_styles.standard(isActive)))),
             'isClanActive': data.isActive()}


class ClanInfoTooltipData(ToolTipBaseData, FortViewHelper):

    def __init__(self, context):
        super(ClanInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, clanDBID):
        fortCtrl = g_clanCache.fortProvider.getController()
        isFortFrozen = False
        if clanDBID is None or clanDBID == g_clanCache.clanDBID:
            fort = fortCtrl.getFort()
            fortDossier = fort.getFortDossier()
            battlesStats = fortDossier.getBattlesStats()
            isFortFrozen = self._isFortFrozen()
            clanName, clanMotto, clanTag = g_clanCache.clanName, g_clanCache.clanMotto, g_clanCache.clanTag
            clanLvl = fort.level if fort is not None else 0
            homePeripheryID = fort.peripheryID
            playersAtClan, buildingsNum = len(g_clanCache.clanMembers), len(fort.getBuildingsCompleted())
            wEfficiencyVal = ProfileUtils.getFormattedWinsEfficiency(battlesStats)
            combatCount, winsEff, profitEff = battlesStats.getBattlesCount(), ProfileUtils.UNAVAILABLE_SYMBOL if wEfficiencyVal == str(ProfileUtils.UNAVAILABLE_VALUE) else wEfficiencyVal, battlesStats.getProfitFactor()
            creationTime = fortDossier.getGlobalStats().getCreationTime()
            defence, vacation, offDay = fort.getDefencePeriod(), fort.getVacationDate(), fort.getLocalOffDay()
        elif type(clanDBID) in (types.IntType, types.LongType, types.FloatType):
            clanInfo = fortCtrl.getPublicInfoCache().getItem(clanDBID)
            if clanInfo is None:
                LOG_WARNING('Requested clan info is empty', clanDBID)
                return
            clanName, clanMotto = clanInfo.getClanName(), clanInfo.getClanMotto()
            clanMotto = html.escape(clanMotto)
            clanTag, clanLvl = '[%s]' % clanInfo.getClanAbbrev(), clanInfo.getLevel()
            homePeripheryID = clanInfo.getHomePeripheryID()
            playersAtClan, buildingsNum = (None, None)
            combatCount, profitEff = clanInfo.getBattleCount(), clanInfo.getProfitFactor()
            creationTime = None
            timestamp = clanInfo.getAvailability()
            defHour, defMin = clanInfo.getDefHourFor(timestamp)
            defenceStart = time_utils.getTimeForLocal(timestamp, defHour, defMin)
            defenceFinish = defenceStart + time_utils.ONE_HOUR
            defence = (defenceStart, defenceFinish)
            offDay = clanInfo.getLocalOffDayFor(timestamp)
            vacation = clanInfo.getVacationPeriod()
            winsEff = None
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
        if winsEff is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_WINPERCENTAGE), winsEff))
        if profitEff is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PROFITPERCENTAGE), BigWorld.wg_getNiceNumberFormat(profitEff) if profitEff > 0 else ProfileUtils.UNAVAILABLE_SYMBOL))
        if creationTime is not None:
            fortCreationData = text_styles.neutral(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPCLANINFO_FORTCREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(creationTime)))
        else:
            fortCreationData = None

        def _makeLabels(stats, itemIdx):
            return '\n'.join((str(a[itemIdx]) for a in stats))

        infoTexts, protectionHeader = [], ''
        if defence[0]:
            if isFortFrozen:
                protectionHeader = text_styles.error(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIMESTOPPED))
            else:
                protectionHeader = text_styles.highTitle(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIME))
            if isFortFrozen:
                formatter = text_styles.disabled
            else:
                formatter = text_styles.stats
            defencePeriodString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortTimeFormat(defence[0]), finishTime=BigWorld.wg_getShortTimeFormat(defence[1]))
            defencePeriodString = formatter(defencePeriodString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSEHOUR, period=defencePeriodString))
            if offDay > -1:
                dayOffString = i18n.makeString('#menu:dateTime/weekDays/full/%d' % (offDay + 1))
            else:
                dayOffString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NODAYOFF)
            dayOffString = formatter(dayOffString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DAYOFF, dayOff=dayOffString))
            if vacation[0] and vacation[1]:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortDateFormat(vacation[0]), finishTime=BigWorld.wg_getShortDateFormat(vacation[1]))
            else:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NOVACATION)
            vacationString = formatter(vacationString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_VACATION, period=vacationString))
        return {'headerText': text_styles.highTitle(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_HEADER, clanTag=clanTag, clanLevel=fort_formatters.getTextLevel(clanLvl))),
         'fullClanName': text_styles.neutral(clanName),
         'sloganText': text_styles.standard(clanMotto),
         'infoDescriptionTopText': text_styles.main(_makeLabels(topStats, 0)),
         'infoTopText': text_styles.stats(_makeLabels(topStats, 1)),
         'infoDescriptionBottomText': '',
         'infoBottomText': '',
         'protectionHeaderText': protectionHeader,
         'infoText': makeHtmlString('html_templates:lobby/fortifications/tooltips/defense_description', 'main', {'text': '\n'.join(infoTexts)}),
         'fortCreationDate': fortCreationData}


class ToolTipRefSysDescription(ToolTipBaseData):
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')

    def __init__(self, context):
        super(ToolTipRefSysDescription, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self):
        return {'titleTF': self.__makeTitle(),
         'actionTF': self.__makeMainText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_ACTIONTF),
         'conditionsTF': self.__makeConditions(),
         'awardsTitleTF': self.__makeStandardText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_AWARDSTITLETF),
         'blocksVOs': self.__makeBlocks(),
         'bottomTF': self.__makeMainText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_BOTTOM_BOTTOMTF)}

    def __makeTitle(self):
        return text_styles.highTitle(ms(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_TITLETF))

    def __makeMainText(self, value):
        return text_styles.main(ms(value))

    def __makeConditions(self):
        return text_styles.standard(ms(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=game_control.g_instance.refSystem.getPosByXPinTeam()))

    def __makeStandardText(self, value):
        return text_styles.standard(ms(value))

    def __makeBlocks(self):
        result = []
        for xp, quests in game_control.g_instance.refSystem.getQuests():
            xpCost = BigWorld.wg_getIntegralFormat(xp)
            awardDescrPars = []
            for quest in quests:
                for bonusName in self.BONUSES_PRIORITY:
                    bonuses = quest.getBonuses(bonusName)
                    if bonuses:
                        awardDescrPars.append(', '.join(map(methodcaller('getDescription'), bonuses)))

            awardDescr = ', '.join(awardDescrPars)
            result.append({'leftTF': text_styles.credits(xpCost),
             'rightTF': awardDescr,
             'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON})

        return result


class ToolTipRefSysAwards(ToolTipBaseData):
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')

    def __init__(self, context):
        super(ToolTipRefSysAwards, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self, data):
        xp, questIDs = cPickle.loads(data)

        def filterFunc(q):
            return q.getID() in questIDs

        quests = g_eventsCache.getHiddenQuests(filterFunc)
        icon = ''
        awardDescrPars = []
        isCompleted = True
        for quest in quests.itervalues():
            for bonusName in self.BONUSES_PRIORITY:
                bonuses = quest.getBonuses(bonusName)
                if bonuses:
                    awardDescrPars.append(', '.join(map(methodcaller('getDescription'), bonuses)))
                    if not icon:
                        icon = bonuses[0].getTooltipIcon()

            if isCompleted and not quest.isCompleted():
                isCompleted = False

        awardDescr = ', '.join(awardDescrPars)
        return {'iconSource': icon,
         'infoTitle': self.__makeTitle(awardDescr),
         'infoBody': self.__makeBody(xp, isCompleted),
         'conditions': self.__makeConditions(),
         'awardStatus': self.__makeStatus(isCompleted)}

    def __makeTitle(self, value):
        award = text_styles.highTitle(value)
        return self.__makeTitleGeneralText(award)

    def __makeTitleGeneralText(self, award):
        return text_styles.highTitle(i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_TITLE_GENERAL, awardMsg=award))

    def __makeBody(self, expCount, isCompleted):
        howManyExp = expCount - game_control.g_instance.refSystem.getReferralsXPPool()
        notEnoughMsg = ''
        if not isCompleted and howManyExp > 0:
            notEnough = text_styles.error(i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS_NOTENOUGH))
            notEnoughMsg = i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS_NOTENOUGHMSG, notEnough=notEnough, howMany=self.__formatExpCount(howManyExp))
        resultFormatter = text_styles.main(i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS, expCount=self.__formatExpCount(expCount), notEnoughMsg=notEnoughMsg))
        return resultFormatter

    def __formatExpCount(self, value):
        value = text_styles.credits(BigWorld.wg_getIntegralFormat(value))
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, 16, 16, -3, 0)
        return value + icon

    def __makeConditions(self):
        return text_styles.standard(i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=game_control.g_instance.refSystem.getPosByXPinTeam()))

    def __makeStatus(self, isReceived):
        loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_NOTACCESS
        if isReceived:
            loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_ACCESS
        return text_styles.main(i18n.makeString(loc))


class ToolTipRefSysXPMultiplier(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipRefSysXPMultiplier, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self):
        refSystem = game_control.g_instance.refSystem
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, 16, 16, -3, 0)
        expNum = text_styles.credits(ms(BigWorld.wg_getNiceNumberFormat(refSystem.getMaxReferralXPPool())))
        titleText = text_styles.highTitle(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_TITLE))
        descriptionText = text_styles.main(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_DESCRIPTION))
        conditionsText = text_styles.standard(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS))
        bottomText = text_styles.main(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_BOTTOM, expNum=expNum + '<nobr>' + icon))
        xpBlocks = []
        for i, (period, bonus) in enumerate(refSystem.getRefPeriods()):
            xpBonus = 'x%s' % BigWorld.wg_getNiceNumberFormat(bonus)
            condition = self.__formatPeriod(period)
            xpBlocks.append({'xpIconSource': RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON,
             'multiplierText': text_styles.credits(xpBonus),
             'descriptionText': text_styles.main(condition)})

        return {'titleText': titleText,
         'descriptionText': descriptionText,
         'conditionsText': conditionsText,
         'bottomText': bottomText,
         'xpBlocksVOs': xpBlocks}

    def __formatPeriod(self, period):
        if period <= 24:
            return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_HOURS, hoursNum=period)
        if period <= 8760:
            return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_DAYS, daysNum=period / 24)
        return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_OTHER)


class _BattleStatus(object):
    __slots__ = ('level', 'msg', 'style', 'prefix')

    def __init__(self, level, msg, style, prefix):
        super(_BattleStatus, self).__init__()
        self.level = level
        self.msg = msg
        self.style = style
        self.prefix = prefix

    def getMsgText(self):
        return ms(self.msg)

    def getResText(self, count):
        return ''.join((self.style('%s %s' % (self.prefix, BigWorld.wg_getIntegralFormat(count))), icons.nut()))


class ToolTipFortBuildingData(ToolTipBaseData, FortViewHelper):

    class BATTLE_STATUSES(CONST_CONTAINER):
        NO_BATTLE = _BattleStatus('warning', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_WASNOTBATTLE, text_styles.defRes, '')
        LOST = _BattleStatus('critical', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_DEFEAT, text_styles.error, '-')
        WON = _BattleStatus('info', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_VICTORY, text_styles.success, '+')

    def __init__(self, context):
        super(ToolTipFortBuildingData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, buildingUID, isMine):
        ms = i18n.makeString
        fort = self.fortCtrl.getFort()
        battleID = getBattleID()
        battle = fort.getBattle(battleID)
        buildingTypeID = self.getBuildingIDbyUID(buildingUID)
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
        normLevel = max(buildingLevel, 1)
        buildingLevelData = fortified_regions.g_cache.buildings[buildingTypeID].levels[normLevel]
        hpTotalVal = buildingLevelData.hp
        maxDefResVal = buildingLevelData.storage
        buildingName = text_styles.highTitle(ms(FORT.buildings_buildingname(buildingUID)))
        currentMapTxt = None
        buildingLevelTxt = text_styles.main(ms(FORT.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=str(fort_formatters.getTextLevel(buildingLevel))))
        descrActionTxt = ''
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
                prefix = text_styles.standard(ms(FORT.TOOLTIPBUILDINGINFO_MEP_MAPPREFIX))
                mapName = text_styles.neutral(arenaType.name)
                currentMapTxt = prefix + mapName
                statusLevel = battleStatus.level
                statusTxt = battleStatus.getMsgText()
                defResStatusTxt = battleStatus.getResText(resCount)
                descrActionTxt = text_styles.main(ms(FORT.TOOLTIPBUILDINGINFO_DESCRACTION))
                descrActionTxt = descrActionTxt % {'value': defResStatusTxt}
            else:
                minResCount = hpTotalVal * 0.2
                minResStatusTxt = ''.join((text_styles.neutral(BigWorld.wg_getIntegralFormat(minResCount)), icons.nut()))
                infoMessage = text_styles.main(ms(FORT.TOOLTIPBUILDINGINFO_DESTROYEDMESSAGE))
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
         'infoMessage': infoMessage,
         'buildingIcon': FortViewHelper.getPopoverIconSource(buildingUID, buildingLevel, True)}
        return result


class ActionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, type, key, newPrice, oldPrice, isBuying, forCredits = False, rentPackage = None):
        actionNames = None
        body = ''
        descr = ''
        newCredits, newGold = newPrice
        oldCredits, oldGold = oldPrice
        newPriceValue = 0
        newPriceCurrency = None
        oldPriceValue = 0
        oldPriceCurrency = None
        hasRentCompensation = False
        rentCompensation = None
        if type == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            actions = g_eventsCache.getEconomicsAction(key)
            newPriceValue = newCredits if forCredits else newGold
            oldPriceValue = oldCredits if forCredits else oldGold
            newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
            if actions:
                actionNames = map(lambda x: x[1], actions)
                if key == 'freeXPToTManXPRate':
                    newPriceCurrency = oldPriceCurrency = 'freeXp'
        if type == ACTION_TOOLTIPS_TYPE.RENT:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = g_eventsCache.getRentAction(item, rentPackage)
            if actions:
                actionNames = map(itemgetter(1), actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
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
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                if item.isRented and not item.rentalIsOver and item.rentCompensation[1] > 0:
                    hasRentCompensation = True
                    rentCompensation = item.rentCompensation[1]
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
        if actionNames:
            actionNames = set(actionNames)
        if newPriceCurrency and oldPriceCurrency and newPriceValue is not None and oldPriceValue:
            formatedNewPrice = makeHtmlString('html_templates:lobby/quests/actions', newPriceCurrency, {'value': BigWorld.wg_getGoldFormat(newPriceValue)})
            formatedOldPrice = makeHtmlString('html_templates:lobby/quests/actions', oldPriceCurrency, {'value': BigWorld.wg_getGoldFormat(oldPriceValue)})
            body = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
        if actionNames:

            def mapName(item):
                action = g_eventsCache.getActions().get(item)
                return i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAME, actionName=action.getUserName())

            actionUserNames = ', '.join(map(mapName, actionNames))
            if len(actionNames) > 1:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTIONS, actions=actionUserNames)
            else:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, action=actionUserNames)
        if hasRentCompensation:
            formattedRentCompensation = makeHtmlString('html_templates:lobby/quests/actions', 'gold', {'value': BigWorld.wg_getGoldFormat(rentCompensation)})
            descr += '\n' + i18n.makeString(TOOLTIPS.ACTIONPRICE_RENTCOMPENSATION, rentCompensation=formattedRentCompensation)
        return {'header': i18n.makeString(TOOLTIPS.ACTIONPRICE_HEADER),
         'body': body + '\n' + descr if descr else body}


class ToolTipFortWrongTime(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipFortWrongTime, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, wrongState, timePeriods):

        def formatReceivedData(target):
            return text_styles.error(target)

        if wrongState == 'wrongTime':
            return {'header': i18n.makeString(TOOLTIPS.FORTWRONGTIME_HEADER),
             'body': i18n.makeString(TOOLTIPS.FORTWRONGTIME_BODY, local=BigWorld.wg_getShortTimeFormat(time_utils.getCurrentTimestamp()), server=BigWorld.wg_getShortTimeFormat(time_utils.getCurrentLocalServerTimestamp()))}
        elif (wrongState == 'lockTime' or wrongState == 'ownDefenceTime') and timePeriods is not None and len(timePeriods) >= 1:
            timeStart, timeFinish = timePeriods[0]
            return {'header': i18n.makeString(TOOLTIPS.FORTWRONGTIME_LOCKTIME_HEADER),
             'body': i18n.makeString(TOOLTIPS.FORTWRONGTIME_LOCKTIME_BODY, timeStart=formatReceivedData(timeStart), timeFinish=formatReceivedData(timeFinish))}
        else:
            raise AttributeError('%s: Unexpected state: %s' % (self, wrongState))
            return


class MapSmallTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(MapSmallTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, data):
        return {'mapName': data.mapName,
         'description': data.description,
         'imageURL': data.imageURL}


class QuestVehiclesBonusTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(QuestVehiclesBonusTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def getDisplayableData(self, questID):
        quest = self._context.buildItem(questID)
        bonuses = quest.getBonuses('vehicles')
        vehiclesList = []
        oneColumnLen = 20
        maxItemsLen = 60
        maxColumnLen = maxItemsLen / 2
        for b in bonuses:
            if b.isShowInGUI():
                flist = b.formattedList()
                if flist:
                    vehiclesList.extend(flist)

        vehiclesListLen = len(vehiclesList)
        if vehiclesListLen <= oneColumnLen:
            columns = ['<br>'.join(vehiclesList)]
        elif vehiclesListLen <= maxItemsLen:
            col1Len = int(math.ceil(vehiclesListLen / float(2)))
            col2Len = vehiclesListLen - col1Len
            col1Str = '<br>'.join(vehiclesList[:col1Len])
            col2Str = '<br>'.join(vehiclesList[col1Len:vehiclesListLen])
            columns = [col1Str, col2Str]
        else:
            col1Str = '<br>'.join(vehiclesList[:maxColumnLen])
            col2 = vehiclesList[maxColumnLen:maxItemsLen - 1]
            vehiclesLeft = vehiclesListLen - maxItemsLen - 1
            moreVehsStr = makeString(TOOLTIPS.QUESTS_VEHICLESBONUS_VEHICLESLEFT, count=vehiclesLeft)
            col2.append(text_styles.warning(moreVehsStr))
            col2Str = '<br>'.join(col2)
            columns = [col1Str, col2Str]
        return {'name': makeString(TOOLTIPS.QUESTS_VEHICLESBONUS_TITLE),
         'columns': columns}


class FortConsumableOrderTooltipData(ToolTipData):

    def __init__(self, context):
        super(FortConsumableOrderTooltipData, self).__init__(context, TOOLTIP_TYPE.EQUIPMENT)
        self.fields = (ToolTipAttrField(self, 'name', 'userName'), ToolTipMethodField(self, 'type', 'getUserType'), FortOrderParamField(self, 'params'))


class LadderTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(LadderTooltipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)

    def getDisplayableData(self, clubDbID):
        club = g_clubsCtrl.getClub(clubDbID)
        if club is None:
            return
        else:
            seasonState = g_clubsCtrl.getSeasonState()
            ladderInfo = club.getLadderInfo()
            if ladderInfo.isInLadder():
                icon = getLadderChevron256x256(ladderInfo.getDivision())
                league = club_fmts.getLeagueString(ladderInfo.getLeague())
                division = club_fmts.getDivisionString(ladderInfo.getDivision())
                ladderPlace = text_styles.promoSubTitle(i18n.makeString(TOOLTIPS.LADDER_PLACE, num=ladderInfo.position))
                state = text_styles.middleTitle(i18n.makeString(TOOLTIPS.LADDER_STATE, league=text_styles.highTitle(league), division=text_styles.highTitle(division)))
                if seasonState.isActive():
                    points = text_styles.main(i18n.makeString(TOOLTIPS.LADDER_POINTS, num=text_styles.stats(str(ladderInfo.getRatingPoints()))))
                else:
                    points = None
                if not ladderInfo.isTop():
                    valueStr = str(getPointsToNextDivision(ladderInfo.getRatingPoints()))
                    ladderStatus = text_styles.main(i18n.makeString(TOOLTIPS.LADDER_LEVELUP, num=text_styles.stats(valueStr)))
                else:
                    ladderStatus = None
            else:
                state, points = (None, None)
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LADDER_256_NO_LADDER
                ladderPlace = text_styles.middleTitle(TOOLTIPS.LADDER_INACTIVE_HEADER)
                ladderStatus = text_styles.main(TOOLTIPS.LADDER_INACTIVE_DESCR)
            if not seasonState.isActive():
                seasonStateString = '\n'.join([text_styles.middleTitle(club_fmts.getSeasonStateUserString(seasonState)), text_styles.main('#tooltips:ladder/season/%s' % seasonState.getStateString())])
            else:
                seasonStateString = None
            return {'state': state,
             'points': points,
             'status': ladderStatus,
             'season': seasonStateString,
             'icon': icon,
             'name': text_styles.highTitle(TOOLTIPS.LADDER_HEADER),
             'place': ladderPlace}


class FortDivisionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(FortDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, divisionID, showWarning):
        if divisionID == FORT_BATTLE_DIVISIONS.ABSOLUTE.divisionID:
            division = FORT_BATTLE_DIVISIONS.ABSOLUTE
            divisionType = 'absolute'
            warning = i18n.makeString('#tooltips:fortDivision/warning/lowBacklog')
        else:
            division = FORT_BATTLE_DIVISIONS.CHAMPION
            divisionType = 'champion'
            warning = i18n.makeString('#tooltips:fortDivision/warning/forbiddenEquipment')
        result = {'name': i18n.makeString('#tooltips:fortDivision/%s/header' % divisionType),
         'descr': i18n.makeString('#tooltips:fortDivision/%s/description' % divisionType),
         'params': [[i18n.makeString('#tooltips:fortDivision/params/vehicleLevel'), int2roman(1) + ' - ' + int2roman(division.maxVehicleLevel)], [i18n.makeString('#tooltips:fortDivision/params/vehiclesCount'), division.maxCombatants]]}
        if showWarning:
            result['warning'] = warning
        return result


class FortSortieTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(FortSortieTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, data):
        _ms = i18n.makeString
        division = text_styles.main(_ms(data.divisionName))
        inBattleIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_SWORDSICON, 16, 16, -3, 0)
        descriptionText = text_styles.main(_ms(data.descriptionForTT)) if data.descriptionForTT != '' else ''
        return {'titleText': text_styles.highTitle(_ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_TITLE, name=data.creatorName)),
         'divisionText': text_styles.standard(_ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_DIVISION, division=division)),
         'descriptionText': descriptionText,
         'hintText': text_styles.standard(_ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_HINT)),
         'inBattleText': text_styles.error(_ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_INBATTLE) + ' ' + inBattleIcon) if data.isInBattle else '',
         'isInBattle': data.isInBattle}


class LadderRegulations(ToolTipBaseData):

    def __init__(self, context):
        super(LadderRegulations, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)

    def getTextForPeriphery(self, serverID, serverName, availabilityCtrl, isHeader = False):
        _ms = i18n.makeString
        forbiddenPeriods = availabilityCtrl.getForbiddenPeriods(serverID)
        if not availabilityCtrl.isServerAvailable(serverID):
            text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_BAN, server=text_styles.stats(serverName))
            if isHeader:
                text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_HEADER_BAN, server=text_styles.alert(serverName))
        elif forbiddenPeriods:
            if isHeader:
                text = text_styles.main(_ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_HEADER_LIMITATION, server=text_styles.alert(serverName), time=text_styles.alert(self.getForbiddenHoursText(forbiddenPeriods))))
            else:
                text = text_styles.main(_ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_LIMITATION, server=text_styles.stats(serverName), time=self.getForbiddenHoursText(forbiddenPeriods)))
        else:
            text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_FREE, server=text_styles.stats(serverName))
            if isHeader:
                text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_HEADER_FREE, server=text_styles.alert(serverName))
        return text_styles.main(text)

    def getForbiddenHoursText(self, forbiddenPeriods):
        forbiddenHours = []
        for forbiddenPeriod in forbiddenPeriods:
            guiTimeLimit = formatGuiTimeLimitStr(*forbiddenPeriod)
            forbiddenHours.append(i18n.makeString(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_DATE, startTime=guiTimeLimit['startTime'], endTime=guiTimeLimit['endTime']))

        return ', '.join(forbiddenHours)

    def getDisplayableData(self):
        from ConnectionManager import connectionManager
        availabilityCtrl = g_clubsCtrl.getAvailabilityCtrl()
        allRules = []
        currServerName = ''
        currPeripheryID = connectionManager.peripheryID
        for url, name, status, peripheryID in g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming()):
            allRules.append(self.getTextForPeriphery(peripheryID, name, availabilityCtrl))
            if peripheryID == currPeripheryID:
                currServerName = name

        return {'name': text_styles.highTitle(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_NAME),
         'thisRules': self.getTextForPeriphery(currPeripheryID, currServerName, availabilityCtrl, True),
         'rulesName': text_styles.middleTitle(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_NAME),
         'allRules': '\n'.join(allRules),
         'info': text_styles.main(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_INFO)}

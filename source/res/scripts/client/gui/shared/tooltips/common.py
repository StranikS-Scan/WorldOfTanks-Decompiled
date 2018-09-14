# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
from collections import namedtuple
import types
import math
from operator import methodcaller, itemgetter
import ResMgr
import BigWorld
import constants
import ArenaType
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.goodies.goodies_cache import g_goodiesCache
from helpers import dependency
from shared_utils import findFirst, first
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters as clans_fmts
from gui.clans.items import formatField
from gui.clubs import formatters as club_fmts
from gui.clubs.settings import getLadderChevron256x256, getPointsToNextDivision
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.time_formatters import getTimeLeftStr
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.view_helpers import UsersInfoHelper
from gui.LobbyContext import g_lobbyContext
from gui.shared.tooltips import efficiency
from gui.shared.money import Money, Currency
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter, makeClanFullName, makeClubFullName, makeContactStatusDescription
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY, PING_STATUSES, PingData
from ConnectionManager import connectionManager
from constants import PREBATTLE_TYPE, WG_GAMES, VISIBILITY
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from helpers import i18n, time_utils, html, int2roman
from helpers.i18n import makeString as ms, makeString
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from UnitBase import SORTIE_DIVISION
from gui import g_htmlTemplates, makeHtmlString
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE, ToolTipParameterField
from gui.shared import g_itemsCache
from gui.Scaleform.daapi.view.lobby.customization import CAMOUFLAGES_KIND_TEXTS, CAMOUFLAGES_NATIONS_TEXTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesSortieListView import formatGuiTimeLimitStr
from items import vehicles
from messenger.storage import storage_getter
from messenger.m_constants import USER_TAG
from gui.shared.tooltips import formatters
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.clans import IClanController
from skeletons.gui.clubs import IClubsController
from skeletons.gui.game_control import IRefSystemController, IIGRController, IServerStatsController
from skeletons.gui.server_events import IEventsCache
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.Scaleform.locale.CHRISTMAS import CHRISTMAS
_UNAVAILABLE_DATA_PLACEHOLDER = '--'

class FortOrderParamField(ToolTipParameterField):

    def _getValue(self):
        return [self._tooltip.item.getParams()]


class IgrTooltipData(ToolTipBaseData):
    igrCtrl = dependency.descriptor(IIGRController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(IgrTooltipData, self).__init__(context, TOOLTIP_TYPE.IGR)

    def getDisplayableData(self, *args):
        qLabels, qProgress = [], []
        premVehQuests = []
        if self.igrCtrl.getRoomType() in (constants.IGR_TYPE.PREMIUM, constants.IGR_TYPE.BASE):
            quests = self.eventsCache.getQuests()
            for q in quests.itervalues():
                if self.igrCtrl.getRoomType() == constants.IGR_TYPE.PREMIUM:
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
        igrPercent = (self.igrCtrl.getXPFactor() - 1) * 100
        igrType = self.igrCtrl.getRoomType()
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

    def _setContentMargin(self, top=None, left=None, bottom=None, right=None):
        if top is not None:
            self.__contentMargin['top'] = top
        if left is not None:
            self.__contentMargin['left'] = left
        if bottom is not None:
            self.__contentMargin['bottom'] = bottom
        if right is not None:
            self.__contentMargin['right'] = right
        return

    def _setMargins(self, afterBlock=_DEFAULT_MARGIN_AFTER_BLOCK, afterSeparator=_DEFAULT_MARGIN_AFTER_SEPARATOR):
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
        self._setWidth(290)

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
            commonGuiData = self.__converter.makeVO(userEntity, useBigIcons=True)
            tags = userEntity.getTags()
            resourceID = self.__converter.getGuiResourceID(userEntity)
            if resourceID == WG_GAMES.TANKS:
                statusDescription = makeContactStatusDescription(userEntity.isOnline(), tags, userEntity.getClientInfo())
            else:
                statusDescription = makeString('#tooltips:Contact/resource/%s' % resourceID)
            commonGuiData['statusDescription'] = statusDescription
            if defaultName and USER_TAG.INVALID_NAME in tags:
                commonGuiData['userProps']['userName'] = defaultName
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
            if {USER_TAG.IGNORED, USER_TAG.IGNORED_TMP} & tags:
                currentUnit += self.__makeIconUnitStr('contactIgnored.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_IGNORED)
            elif USER_TAG.SUB_TO not in tags and (USER_TAG.SUB_PENDING_IN in tags or userEntity.isFriend() and USER_TAG.SUB_FROM not in tags):
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
            if USER_TAG.IGNORED in tags or USER_TAG.IGNORED_TMP in tags:
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
        return '<br/>' if currentUnit != '' else ''

    def __addComma(self, currStr):
        return ', ' if currStr != '' else ''


class SortieDivisionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SortieDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self):
        divisionsData = []
        divisions = makeDivisionData()
        for division in divisions:
            minLvl, maxLvl = division['vehLvls']
            if maxLvl == minLvl:
                divisLevels = fort_formatters.getTextLevel(maxLvl)
            else:
                divisLevels = fort_formatters.getTextLevel(minLvl) + ' - ' + fort_formatters.getTextLevel(maxLvl)
            divisionsData.append({'divisName': division['label'],
             'divisLevels': text_styles.main(divisLevels),
             'divisBonus': self.__getBonusStr(division['profit']),
             'divisPlayers': self.__getPlayerLimitsStr(*self.__getPlayerLimits(division['level']))})

        return {'divisions': divisionsData}

    def __getPlayerLimits(self, divisionType):
        divisionIndex = SORTIE_DIVISION._ORDER.index(divisionType)
        division = SupportedRosterSettings.list(PREBATTLE_TYPE.SORTIE)[divisionIndex]
        return (division.getMinSlots(), division.getMaxSlots())

    def __getPlayerLimitsStr(self, minCount, maxCount):
        return text_styles.main(str(minCount) + ' - ' + str(maxCount))

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


class SettingsButtonTooltipData(BlocksTooltipData):
    serverStats = dependency.descriptor(IServerStatsController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, context):
        super(SettingsButtonTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self.item = None
        self._setContentMargin(top=15, left=19, bottom=5, right=10)
        self._setMargins(afterBlock=15, afterSeparator=15)
        self._setWidth(295)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(SettingsButtonTooltipData, self)._packBlocks(*args, **kwargs)
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.HEADER_MENU_HEADER)), formatters.packTextBlockData(text_styles.standard(TOOLTIPS.HEADER_MENU_DESCRIPTION))]))
        serverBlocks = list()
        serverBlocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HEADER_MENU_SERVER), padding=formatters.packPadding(0, 0, 4)))
        simpleHostList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        isColorBlind = self.settingsCore.getSetting('isColorBlind')

        def __getPingData(url):
            pingData = g_preDefinedHosts.getHostPingData(url)
            if pingData.status == PING_STATUSES.REQUESTED:
                return PingData(pingData.value, PING_STATUSES.UNDEFINED)
            else:
                return pingData

        if connectionManager.peripheryID == 0:
            serverBlocks.append(self.__packServerBlock(self.__wrapServerName(connectionManager.serverUserName), __getPingData(connectionManager.url), HOST_AVAILABILITY.IGNORED, True, isColorBlind))
        if len(simpleHostList):
            currServUrl = connectionManager.url
            for key, name, csisStatus, peripheryID in simpleHostList:
                serverBlocks.append(self.__packServerBlock(name, __getPingData(key), csisStatus, currServUrl == key, isColorBlind))

        items.append(formatters.packBuildUpBlockData(serverBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        serversStats = None
        if constants.IS_SHOW_SERVER_STATS:
            serversStats, _ = self.serverStats.getFormattedStats()
        if not constants.IS_CHINA:
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HEADER_MENU_PLAYERSONSERVER)), formatters.packImageTextBlockData('', serversStats, RES_ICONS.MAPS_ICONS_LIBRARY_CREW_ONLINE, imgPadding=formatters.packPadding(-4, -10), padding=formatters.packPadding(5))]))
        return items

    @classmethod
    def __packServerBlock(cls, name, pingData, csisStatus, isSelected=False, isColorBlind=False):
        """
        Provides necessary block data from passed parameters
        :param name: str, the name of host
        :param pingData: predefined_hosts.PingData
        :param csisStatus: predefined_hosts.HOST_AVAILABILITY
        :param isSelected: bool
        :param isColorBlind: bool
        :return:
        """
        separator = '  '
        pingValue, pingStatus = pingData
        if csisStatus != HOST_AVAILABILITY.NOT_AVAILABLE and pingStatus != PING_STATUSES.UNDEFINED:
            if pingStatus == PING_STATUSES.LOW:
                formattedPing = text_styles.success(pingValue)
            else:
                formattedPing = text_styles.main(pingValue) if isSelected else text_styles.standard(pingValue)
        else:
            pingValue = _UNAVAILABLE_DATA_PLACEHOLDER
            pingStatus = PING_STATUSES.UNDEFINED
            formattedPing = text_styles.standard(pingValue)
        colorBlindName = ''
        if isColorBlind and pingStatus == PING_STATUSES.HIGH:
            colorBlindName = '_color_blind'
        pingStatusIcon = cls.__formatPingStatusIcon(RES_ICONS.maps_icons_pingstatus_stairs_indicator(str(pingStatus) + colorBlindName + '.png'))
        return formatters.packTextParameterBlockData(cls.__formatServerName(name, isSelected), text_styles.concatStylesToSingleLine(formattedPing, separator, pingStatusIcon), valueWidth=55, gap=2, padding=formatters.packPadding(left=40))

    @classmethod
    def __formatServerName(cls, name, isSelected=False):
        if isSelected:
            result = text_styles.main(name + ' ' + ms(TOOLTIPS.HEADER_MENU_SERVER_CURRENT))
        else:
            result = text_styles.standard(name)
        return result

    @classmethod
    def __formatPingStatusIcon(cls, icon):
        return icons.makeImageTag(icon, 16, 16, -4)

    @staticmethod
    def __wrapServerName(name):
        return makeHtmlString('html_templates:lobby/serverStats', 'serverName', {'name': name}) if constants.IS_CHINA else name


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

    def getDisplayableData(self, type, id, nationId, timeLeft, isPermanent=None, value=None, isUsed=False, boundVehicle=None, boundToCurrentVehicle=False):
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
    clanCtrl = dependency.descriptor(IClanController)

    def __init__(self, context):
        super(ClanCommonInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.CLAN_PROFILE)
        self.__usersInfoHelper = UsersInfoHelper()

    def getDisplayableData(self, clanDBID):
        data = self.clanCtrl.getClanCommonData(clanDBID)
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
    refSystem = dependency.descriptor(IRefSystemController)

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
        return text_styles.standard(ms(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=self.refSystem.getPosByXPinTeam()))

    def __makeStandardText(self, value):
        return text_styles.standard(ms(value))

    def __makeBlocks(self):
        result = []
        for xp, quests in self.refSystem.getQuests():
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
    eventsCache = dependency.descriptor(IEventsCache)
    refSystem = dependency.descriptor(IRefSystemController)

    def __init__(self, context):
        super(ToolTipRefSysAwards, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self, data):
        xp, questIDs = cPickle.loads(data)

        def filterFunc(q):
            return q.getID() in questIDs

        quests = self.eventsCache.getHiddenQuests(filterFunc)
        icon = ''
        awardDescrPars = []
        isCompleted = True
        for bonusName in self.BONUSES_PRIORITY:
            for quest in quests.itervalues():
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
        howManyExp = expCount - self.refSystem.getReferralsXPPool()
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
        return text_styles.standard(i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=self.refSystem.getPosByXPinTeam()))

    def __makeStatus(self, isReceived):
        loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_NOTACCESS
        if isReceived:
            loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_ACCESS
        return text_styles.main(i18n.makeString(loc))


class ToolTipRefSysXPMultiplier(ToolTipBaseData):
    refSystem = dependency.descriptor(IRefSystemController)

    def __init__(self, context):
        super(ToolTipRefSysXPMultiplier, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self):
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, 16, 16, -3, 0)
        expNum = text_styles.credits(ms(BigWorld.wg_getNiceNumberFormat(self.refSystem.getMaxReferralXPPool())))
        titleText = text_styles.highTitle(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_TITLE))
        descriptionText = text_styles.main(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_DESCRIPTION))
        conditionsText = text_styles.standard(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS))
        bottomText = text_styles.main(ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_BOTTOM, expNum=expNum + '<nobr>' + icon))
        xpBlocks = []
        for i, (period, bonus) in enumerate(self.refSystem.getRefPeriods()):
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
        return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_DAYS, daysNum=period / 24) if period <= 8760 else ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_OTHER)


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


class ActionTooltipData(ToolTipBaseData):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, type, key, newPrice, oldPrice, isBuying, forCredits=False, rentPackage=None):
        actionNames = None
        body = ''
        descr = ''
        newPrice = Money(*newPrice)
        oldPrice = Money(*oldPrice)
        newPriceValue = 0
        newPriceCurrency = None
        oldPriceValue = 0
        oldPriceCurrency = None
        hasRentCompensation = False
        hasPersonalDiscount = False
        rentCompensation = None
        if type == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            actions = self.eventsCache.getEconomicsAction(key)
            newPriceValue = newPrice.credits if forCredits else newPrice.gold
            oldPriceValue = oldPrice.credits if forCredits else oldPrice.gold
            newPriceCurrency = oldPriceCurrency = Currency.CREDITS if forCredits else Currency.GOLD
            if actions:
                actionNames = map(lambda x: x[1], actions)
                if key == 'freeXPToTManXPRate':
                    newPriceCurrency = oldPriceCurrency = 'freeXp'
        elif type == ACTION_TOOLTIPS_TYPE.RENT:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = self.eventsCache.getRentAction(item, rentPackage)
            if actions:
                actionNames = map(itemgetter(1), actions)
                newPriceValue = newPrice.credits if forCredits else newPrice.gold
                oldPriceValue = oldPrice.credits if forCredits else oldPrice.gold
                newPriceCurrency = oldPriceCurrency = Currency.CREDITS if forCredits else Currency.GOLD
        elif type == ACTION_TOOLTIPS_TYPE.ITEM:
            item = g_itemsCache.items.getItemByCD(int(key))
            useGold = item.isPremium and not forCredits and isBuying
            newPriceValue = newPrice.gold if useGold else newPrice.credits
            oldPriceValue = oldPrice.gold if useGold else oldPrice.credits
            newPriceCurrency = oldPriceCurrency = Currency.GOLD if useGold else Currency.CREDITS
            actions = self.eventsCache.getItemAction(item, True, forCredits)
            if item.itemTypeID in (GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT) and item.isPremium and not useGold:
                actions += self.eventsCache.getEconomicsAction('exchangeRateForShellsAndEqs')
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isPremium and not isBuying:
                actions += self.eventsCache.getEconomicsAction('exchangeRate')
            if actions:
                actionNames = map(lambda x: x[1], actions)
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                shop = g_itemsCache.items.shop
                shopPrice = shop.getItemPrice(item.intCD)
                personalPrice = shop.getPersonalVehicleDiscountPrice(item.intCD)
                if personalPrice is not None and personalPrice.get(newPriceCurrency) <= shopPrice.get(newPriceCurrency):
                    actionNames = None
                    hasPersonalDiscount = True
            if not isBuying:
                sellingActions = self.eventsCache.getItemAction(item, False, forCredits)
                if sellingActions:
                    actionNames = map(lambda x: x[1], sellingActions)

                    def filter(item):
                        (forGold, _), _ = item
                        return forGold

                    sellForGoldAction = findFirst(filter, sellingActions)
                    if sellForGoldAction:
                        newPriceValue = newPrice.gold
                        newPriceCurrency = Currency.GOLD
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                if item.isRented and not item.rentalIsOver and item.rentCompensation.gold > 0:
                    hasRentCompensation = True
                    rentCompensation = item.rentCompensation.gold
        elif type == ACTION_TOOLTIPS_TYPE.CAMOUFLAGE:
            intCD, type = cPickle.loads(key)
            actions = self.eventsCache.getCamouflageAction(intCD) + self.eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newPrice.credits if forCredits else newPrice.gold
                oldPriceValue = oldPrice.credits if forCredits else oldPrice.gold
                newPriceCurrency = oldPriceCurrency = Currency.CREDITS if forCredits else Currency.GOLD
        elif type == ACTION_TOOLTIPS_TYPE.EMBLEMS:
            group, type = cPickle.loads(key)
            actions = self.eventsCache.getEmblemsAction(group) + self.eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newPrice.credits if forCredits else newPrice.gold
                oldPriceValue = oldPrice.credits if forCredits else oldPrice.gold
                newPriceCurrency = oldPriceCurrency = Currency.CREDITS if forCredits else Currency.GOLD
        elif type == ACTION_TOOLTIPS_TYPE.AMMO:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = []
            for shell in item.gun.defaultAmmo:
                actions += self.eventsCache.getItemAction(shell, isBuying, True)

            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newPrice.credits
                oldPriceValue = newPrice.credits
                newPriceCurrency = oldPriceCurrency = Currency.CREDITS
        elif type == ACTION_TOOLTIPS_TYPE.BOOSTER:
            booster = g_goodiesCache.getBooster(int(key))
            actions = self.eventsCache.getBoosterAction(booster, isBuying, forCredits)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newPrice.credits if forCredits else newPrice.gold
                oldPriceValue = oldPrice.credits if forCredits else oldPrice.gold
                newPriceCurrency = oldPriceCurrency = Currency.CREDITS if forCredits else Currency.GOLD
        if actionNames:
            actionNames = set(actionNames)
        if newPriceCurrency and oldPriceCurrency and newPriceValue is not None and oldPriceValue:
            formatedNewPrice = makeHtmlString('html_templates:lobby/quests/actions', newPriceCurrency, {'value': BigWorld.wg_getGoldFormat(newPriceValue)})
            formatedOldPrice = makeHtmlString('html_templates:lobby/quests/actions', oldPriceCurrency, {'value': BigWorld.wg_getGoldFormat(oldPriceValue)})
            body = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
        if actionNames:

            def mapName(item):
                action = self.eventsCache.getActions().get(item)
                return i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAME, actionName=action.getUserName())

            actionUserNames = ', '.join(map(mapName, actionNames))
            if len(actionNames) > 1:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTIONS, actions=actionUserNames)
            else:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, action=actionUserNames)
        if hasPersonalDiscount:
            descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORPERSONALDISCOUNT)
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


class LadderTooltipData(ToolTipBaseData):
    clubsCtrl = dependency.descriptor(IClubsController)

    def __init__(self, context):
        super(LadderTooltipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)

    def getDisplayableData(self, clubDbID):
        club = self.clubsCtrl.getClub(clubDbID)
        if club is None:
            return
        else:
            seasonState = self.clubsCtrl.getSeasonState()
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


class SettingsMinimapCircles(BlocksTooltipData):

    def __init__(self, context):
        super(SettingsMinimapCircles, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setContentMargin(top=15, left=19, bottom=6, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(364)

    def _packBlocks(self, *args):
        tooltipBlocks = super(SettingsMinimapCircles, self)._packBlocks()
        headerBlock = formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_TITLE))
        lineBreak = '<br/>'
        imgBlock = formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_SETTINGS_MINIMAPCIRCLESTOOLTIP, imgPadding={'top': -5,
         'left': 74})
        tooltipBlocks.append(formatters.packBuildUpBlockData([headerBlock, imgBlock], padding={'bottom': -20}))
        textBlocks = []
        templateName = 'html_templates:lobby/tooltips/settings_minimap_circles'
        viewRangeTitle = text_styles.bonusAppliedText(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_VIEWRANGE_TITLE)
        viewRangeBody = text_styles.main(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_VIEWRANGE_BODY)
        textBlocks.extend(self.getTextBlocksForCircleDescr(viewRangeTitle, viewRangeBody))
        maxViewRangeHtml = makeHtmlString(templateName, 'max_view_range_title') + lineBreak
        maxViewRangeTitle = maxViewRangeHtml % i18n.makeString(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_MAXVIEWRANGE_TITLE)
        maxViewRangeBody = text_styles.main(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_MAXVIEWRANGE_AS3_BODY) % VISIBILITY.MAX_RADIUS
        textBlocks.extend(self.getTextBlocksForCircleDescr(maxViewRangeTitle, maxViewRangeBody))
        drawRangeHtml = makeHtmlString(templateName, 'draw_range_title') + lineBreak
        drawRangeTitle = drawRangeHtml % i18n.makeString(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_DRAWRANGE_TITLE)
        drawRangeBody = text_styles.main(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_DRAWRANGE_BODY)
        textBlocks.extend(self.getTextBlocksForCircleDescr(drawRangeTitle, drawRangeBody))
        tooltipBlocks.append(formatters.packBuildUpBlockData(textBlocks, padding={'top': -1}))
        return tooltipBlocks

    def getTextBlocksForCircleDescr(self, title, body):
        blocks = []
        blocks.append(formatters.packTextBlockData(title, padding={'bottom': 3}))
        blocks.append(formatters.packTextBlockData(body, padding={'bottom': 9}))
        return blocks


class SquadRestrictionsInfo(BlocksTooltipData):

    def __init__(self, context):
        super(SquadRestrictionsInfo, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setContentMargin(top=15, left=19, bottom=6, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(364)

    def _packBlocks(self, *args):
        tooltipBlocks = super(SquadRestrictionsInfo, self)._packBlocks()
        tooltipBlocks.append(formatters.packTitleDescBlock(text_styles.highTitle(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_HEADER)))
        tooltipBlocks.append(formatters.packImageTextBlockData(text_styles.stats(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_TITLE0), text_styles.standard(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_BODY0), RES_ICONS.MAPS_ICONS_LIBRARY_DONE, imgPadding=formatters.packPadding(left=-21, right=10), padding=formatters.packPadding(-22, 20)))
        tooltipBlocks.append(formatters.packImageTextBlockData(text_styles.stats(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_TITLE1), text_styles.standard(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_BODY1), RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLEDBIG, imgPadding=formatters.packPadding(left=-21, right=12), padding=formatters.packPadding(-22, 20, 1)))
        tooltipBlocks.append(formatters.packImageTextBlockData(text_styles.stats(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_TITLE2), text_styles.standard(TOOLTIPS.SQUADWINDOW_INFOICON_TECHRESTRICTIONS_BODY2), RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32, imgPadding=formatters.packPadding(left=-21, right=10), padding=formatters.packPadding(-22, 20, 11)))
        return tooltipBlocks


class LadderRegulations(ToolTipBaseData):
    clubsCtrl = dependency.descriptor(IClubsController)

    def __init__(self, context):
        super(LadderRegulations, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)

    def getTextForPeriphery(self, serverID, serverName, availabilityCtrl, isHeader=False):
        _ms = i18n.makeString
        forbiddenPeriods = availabilityCtrl.getForbiddenPeriods(serverID)
        if not availabilityCtrl.isServerAvailable(serverID):
            if isHeader:
                text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_HEADER_BAN, server=text_styles.alert(serverName))
            else:
                text = _ms(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_BAN, server=text_styles.stats(serverName))
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
        availabilityCtrl = self.clubsCtrl.getAvailabilityCtrl()
        allRules = []
        currServerName = connectionManager.serverUserName
        currPeripheryID = connectionManager.peripheryID
        for url, name, status, peripheryID in g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming()):
            allRules.append(self.getTextForPeriphery(peripheryID, name, availabilityCtrl))

        data = {'name': text_styles.highTitle(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_NAME),
         'thisRules': self.getTextForPeriphery(currPeripheryID, currServerName, availabilityCtrl, True),
         'info': text_styles.main(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_INFO)}
        if not connectionManager.isStandalone():
            data.update({'rulesName': text_styles.middleTitle(CYBERSPORT.LADDERREGULATIONS_TOOLTIP_SCHEDULE_NAME),
             'allRules': '\n'.join(allRules),
             'hasRules': len(allRules) != 0})
        return data


_CurrencySetting = namedtuple('_CurrencySetting', 'text, icon, textStyle, frame')

class CURRENCY_SETTINGS(object):
    BUY_CREDITS_PRICE = 'buyCreditsPrice'
    RESTORE_PRICE = 'restorePrice'
    BUY_GOLD_PRICE = 'buyGoldPrice'
    RENT_CREDITS_PRICE = 'rentCreditsPrice'
    RENT_GOLD_PRICE = 'rentGoldPrice'
    SELL_PRICE = 'sellPrice'
    UNLOCK_PRICE = 'unlockPrice'

    @classmethod
    def getRentSetting(cls, currency):
        return cls.RENT_CREDITS_PRICE if currency == Currency.CREDITS else cls.RENT_GOLD_PRICE

    @classmethod
    def getBuySetting(cls, currency):
        return cls.BUY_CREDITS_PRICE if currency == Currency.CREDITS else cls.BUY_GOLD_PRICE


_OPERATIONS_SETTINGS = {CURRENCY_SETTINGS.BUY_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.RESTORE_PRICE: _CurrencySetting('#tooltips:vehicle/restore_price', icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.BUY_GOLD_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.RENT_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_MINRENTALSPRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.RENT_GOLD_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_MINRENTALSPRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.SELL_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_SELL_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.UNLOCK_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_UNLOCK_PRICE, icons.xp(), text_styles.expText, ICON_TEXT_FRAMES.XP)}

def _getCurrencySetting(key):
    if key in _OPERATIONS_SETTINGS:
        return _OPERATIONS_SETTINGS[key]
    else:
        LOG_ERROR('Unsupported currency type "' + key + '"!')
        return None
        return None


def makePriceBlock(price, currencySetting, neededValue=None, oldPrice=None, percent=0, valueWidth=-1, leftPadding=61):
    _int = BigWorld.wg_getIntegralFormat
    needFormatted = ''
    oldPriceText = ''
    hasAction = percent != 0
    settings = _getCurrencySetting(currencySetting)
    if settings is None:
        return
    else:
        valueFormatted = settings.textStyle(_int(price))
        icon = settings.icon
        if neededValue is not None:
            needFormatted = settings.textStyle(_int(neededValue))
        if hasAction:
            oldPriceText = text_styles.concatStylesToSingleLine(icon, settings.textStyle(_int(oldPrice)))
        neededText = ''
        if neededValue is not None:
            neededText = text_styles.concatStylesToSingleLine(text_styles.main('('), text_styles.error(TOOLTIPS.VEHICLE_GRAPH_BODY_NOTENOUGH), ' ', needFormatted, ' ', icon, text_styles.main(')'))
        text = text_styles.concatStylesWithSpace(text_styles.main(settings.text), neededText)
        if hasAction:
            actionText = text_styles.main(makeString(TOOLTIPS.VEHICLE_ACTION_PRC, actionPrc=text_styles.stats(str(percent) + '%'), oldPrice=oldPriceText))
            text = text_styles.concatStylesToMultiLine(text, actionText)
            newPrice = Money(gold=price) if settings.frame == ICON_TEXT_FRAMES.GOLD else Money(credits=price)
            oldPrice = Money(gold=oldPrice) if settings.frame == ICON_TEXT_FRAMES.GOLD else Money(credits=oldPrice)
            return formatters.packSaleTextParameterBlockData(name=text, saleData={'newPrice': newPrice,
             'oldPrice': oldPrice,
             'valuePadding': -8}, actionStyle='alignTop', padding=formatters.packPadding(left=leftPadding), currency=newPrice.getCurrency())
        return formatters.packTextParameterWithIconBlockData(name=text, value=valueFormatted, icon=settings.frame, valueWidth=valueWidth, padding=formatters.packPadding(left=-5))
        return


class SettingsBaseKey(BlocksTooltipData):
    TEMPLATE_NAME = 'html_templates:lobby/tooltips/settings_key_commands'

    def __init__(self, context):
        super(SettingsBaseKey, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setWidth(350)
        self._enemyBlockImage = ''
        self._enemyBlockTitle = ''
        self._allyBlockImage = ''
        self._allyBlockTitle = ''

    def _getEnemyDescription(self):
        enemyDescriptionHtml = makeHtmlString(SettingsBaseKey.TEMPLATE_NAME, 'enemy_description')
        return text_styles.main(ms(TOOLTIPS.SETTINGS_KEY_ENEMY_BODY, enemy=enemyDescriptionHtml % i18n.makeString(TOOLTIPS.SETTINGS_KEY_TARGET_ENEMY)))

    def _packBlocks(self, *args):
        tooltipBlocks = super(SettingsBaseKey, self)._packBlocks()
        headerBlock = formatters.packTitleDescBlock(text_styles.highTitle(TOOLTIPS.SETTINGS_KEYFOLLOWME_TITLE))
        allyDescriptionHtml = makeHtmlString(SettingsBaseKey.TEMPLATE_NAME, 'ally_description')
        allyDescription = text_styles.main(ms(TOOLTIPS.SETTINGS_KEY_ALLY_BODY, ally=allyDescriptionHtml % i18n.makeString(TOOLTIPS.SETTINGS_KEY_TARGET_ALLY)))
        enemyBlock = formatters.packImageTextBlockData(title=text_styles.middleTitle(self._enemyBlockTitle), desc=self._getEnemyDescription(), img=self._enemyBlockImage, imgPadding={'left': -4,
         'right': 4}, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding={'top': -8})
        allyBlock = formatters.packImageTextBlockData(title=text_styles.middleTitle(self._allyBlockTitle), desc=allyDescription, img=self._allyBlockImage, imgPadding={'left': -4,
         'right': 4}, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding={'top': -8})
        tooltipBlocks.append(headerBlock)
        tooltipBlocks.append(enemyBlock)
        tooltipBlocks.append(allyBlock)
        return tooltipBlocks


class SettingsKeyFollowMe(SettingsBaseKey):

    def __init__(self, context):
        super(SettingsKeyFollowMe, self).__init__(context)
        self._enemyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_SUPPORTTOOLTIP
        self._enemyBlockTitle = TOOLTIPS.SETTINGS_SUPPORT_SUBTITLE
        self._allyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_FOLLOWMETOOLTIP
        self._allyBlockTitle = TOOLTIPS.SETTINGS_FOLLOWME_SUBTITLE


class SettingsKeyTurnBack(SettingsBaseKey):

    def __init__(self, context):
        super(SettingsKeyTurnBack, self).__init__(context)
        self._enemyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_DEFENDBASETOOLTIP
        self._enemyBlockTitle = TOOLTIPS.SETTINGS_DEFENDBASE_SUBTITLE
        self._allyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_TURNBACKTOOLTIP
        self._allyBlockTitle = TOOLTIPS.SETTINGS_TURNBACK_SUBTITLE

    def _getEnemyDescription(self):
        return text_styles.main(TOOLTIPS.SETTINGS_DEFENDBASE_ENEMY_BODY)


class SettingsKeyNeedHelp(SettingsBaseKey):

    def __init__(self, context):
        super(SettingsKeyNeedHelp, self).__init__(context)
        self._enemyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_NEEDHELPTOOLTIP
        self._enemyBlockTitle = TOOLTIPS.SETTINGS_NEEDHELP_SUBTITLE
        self._allyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_NEEDHELPTOOLTIP
        self._allyBlockTitle = TOOLTIPS.SETTINGS_HELPME_SUBTITLE

    def _getEnemyDescription(self):
        return text_styles.main(TOOLTIPS.SETTINGS_NEEDHELP_ENEMY_BODY)


class SettingsKeyReload(SettingsBaseKey):

    def __init__(self, context):
        super(SettingsKeyReload, self).__init__(context)
        self._enemyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_RESETTOOLTIP
        self._enemyBlockTitle = TOOLTIPS.SETTINGS_RELOAD_SUBTITLE
        self._allyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_STOPICONTOOLTIP
        self._allyBlockTitle = TOOLTIPS.SETTINGS_STOP_SUBTITLE

    def _getEnemyDescription(self):
        return text_styles.main(TOOLTIPS.SETTINGS_RELOAD_ENEMY_BODY)


class SettingKeySwitchMode(BlocksTooltipData):

    def __init__(self, context):
        super(SettingKeySwitchMode, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(SettingKeySwitchMode, self)._packBlocks(*args, **kwargs)
        tooltipBlocks.append(formatters.packTitleDescBlock(text_styles.highTitle(TOOLTIPS.SETTINGS_KEYMOVEMENT_TITLE), text_styles.main(TOOLTIPS.SETTINGS_SWITCHMODE_BODY)))
        return tooltipBlocks


class XMasTreeTooltipData(BlocksTooltipData):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(XMasTreeTooltipData, self).__init__(context, TOOLTIP_TYPE.CHRISTMAS)
        self._setContentMargin(top=16, bottom=17)
        self._setWidth(364)

    def _packBlocks(self, forceShowLevelInfo=False):
        items = super(XMasTreeTooltipData, self)._packBlocks(forceShowLevelInfo)
        ratingInfo = g_christmasCtrl.getTempStorage().getTreeLevelInfo()
        lvl = int2roman(ratingInfo['level'])
        hasToysOnTree = ratingInfo['rating'] > 0
        titleBlock = formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.XMAS_XMASTREE_TITLE))
        if not forceShowLevelInfo and not hasToysOnTree:
            descBlock = formatters.packTextBlockData(text_styles.main(TOOLTIPS.XMAS_XMASTREE_DESCRIPTION_NOTOYS))
        else:
            rating = ratingInfo['rating']
            maxRating = ratingInfo['maxRating'] + 1
            descBlock = formatters.packBlockDataItem(BLOCKS_TOOLTIP_TYPES.TOOLTIP_XMAS_EVENT_PROGRESS_BLOCK_LINKAGE, {'levelText': text_styles.main(ms(TOOLTIPS.XMAS_XMASTREE_DESCRIPTION, lvl=text_styles.stats(lvl))),
             'progressText': text_styles.main(ms(TOOLTIPS.XMAS_XMASTREE_PROGRESS, current=text_styles.stats(rating), total=maxRating)),
             'progress': rating / float(maxRating)})
        items.append(formatters.packBuildUpBlockData([titleBlock, descBlock], gap=-2, padding={'bottom': 4}))
        if forceShowLevelInfo or hasToysOnTree:
            intLvl = ratingInfo['level']
            qPattern = 'christmas_%s' % (intLvl + 1)
            quest = first(self.eventsCache.getHiddenQuests(filterFunc=lambda q: q.getID().startswith(qPattern)).values())
            simpleBonusesList = []
            if quest is not None:
                bonuses = quest.getBonuses()
                for b in bonuses:
                    if b is not None:
                        if b.isShowInGUI():
                            simpleBonusesList.extend(b.formattedList())

            nextLvlAward = ', '.join(simpleBonusesList)
            title = TOOLTIPS.XMAS_XMASTREE_AWARD
            if intLvl == 10:
                title = '#tooltips:xmas/award/allReceived'
            elif quest is not None and quest.isCompleted():
                nextLvlAward = text_styles.main('#tooltips:xmas/award/alreadyReceived')
            items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=text_styles.middleTitle(title), desc=text_styles.main(nextLvlAward), gap=-1)], gap=4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding={'top': -2,
             'bottom': 6}))
            items.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.XMAS_XMASTREE_NOTE), padding={'top': -1}))
        return items


class XMasInstructionTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(XMasInstructionTooltipData, self).__init__(context, TOOLTIP_TYPE.CHRISTMAS)
        self._setContentMargin(top=14, left=20, bottom=19)
        self._setWidth(362)

    def _packBlocks(self, *args, **kwargs):
        items = super(XMasInstructionTooltipData, self)._packBlocks(*args, **kwargs)
        title = text_styles.highTitle(TOOLTIPS.XMAS_INSTRUCTION_TITLE)
        description = text_styles.main(TOOLTIPS.XMAS_INSTRUCTION_DESCRIPTION)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=title, gap=-2, padding={'bottom': 4}), formatters.packImageBlockData(img=RES_ICONS.MAPS_ICONS_CHRISTMAS_INSTRUCTIONIMG)]))
        items.append(formatters.packTextBlockData(text=description))
        return items


class XMasSlotTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(XMasSlotTooltipData, self).__init__(context, TOOLTIP_TYPE.CHRISTMAS)
        self._setContentMargin(top=13, left=18, bottom=16)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        items = super(XMasSlotTooltipData, self)._packBlocks(*args, **kwargs)
        itemID = args[0]
        item = g_christmasCtrl.getChristmasItemByID(itemID)
        toyType = ms(CHRISTMAS.TOYTYPE + '/%s' % item.guiType)
        toyName = ms(CHRISTMAS.TOYNAME + '/%s' % item.id)
        title = text_styles.highTitle(ms(TOOLTIPS.XMAS_SLOT_TITLE, type=toyType, name=toyName))
        description = text_styles.main(ms(TOOLTIPS.XMAS_SLOT_DESCRIPTION, lvl=text_styles.stats(int2roman(item.rank))))
        value = text_styles.bonusLocalText(str(item.ratingValue))
        items.append(formatters.packTitleDescBlock(title=title, desc=description, gap=-2, padding={'bottom': 4}))
        items.append(formatters.packBuildUpBlockData([formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.XMAS_SLOT_POINTS), value=value, valueWidth=63, gap=7, vertCentred=True)], gap=4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding={'top': -2,
         'bottom': 2}))
        descriptionKey = '/'.join((CHRISTMAS.TOPTOYDESCRIPTION, str(itemID)))
        if i18n.doesTextExist(descriptionKey):
            items.append(formatters.packTextBlockData(text=text_styles.standard(ms(descriptionKey)), padding={'top': -1}))
        return items

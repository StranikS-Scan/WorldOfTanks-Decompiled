# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
from collections import namedtuple
import types
import math
from operator import methodcaller
import ResMgr
import BigWorld
import constants
import ArenaType
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.formatters.servers import formatPingStatus, wrapServerName
from helpers import dependency
from shared_utils import findFirst
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters as clans_fmts
from gui.clans.items import formatField
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.text_styles import concatStylesToMultiLine
from gui.shared.formatters.time_formatters import getTimeLeftStr
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.view_helpers import UsersInfoHelper
from gui.shared.tooltips import efficiency
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter, makeClanFullName, makeContactStatusDescription
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY, PING_STATUSES, PingData
from constants import PREBATTLE_TYPE, WG_GAMES, VISIBILITY
from debug_utils import LOG_WARNING, LOG_ERROR
from helpers import i18n, time_utils, html, int2roman
from helpers.i18n import makeString as ms, makeString
from gui import g_htmlTemplates, makeHtmlString
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getReserveNameVO, getDirection
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.prb_control.items.stronghold_items import SUPPORT_TYPE, REQUISITION_TYPE, HEAVYTRUCKS_TYPE
from gui.server_events.formatters import TOKEN_SIZES
from gui.server_events.events_helpers import missionsSortFunc
from gui.shared.gui_items import GUI_ITEM_TYPE, ACTION_ENTITY_ITEM
from gui.shared.ClanCache import g_clanCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE, ToolTipParameterField
from gui.Scaleform.daapi.view.lobby.customization import CAMOUFLAGES_KIND_TEXTS, CAMOUFLAGES_NATIONS_TEXTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from items import vehicles
from messenger.storage import storage_getter
from messenger.m_constants import USER_TAG
from gui.shared.tooltips import formatters
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.clans import IClanController
from skeletons.gui.game_control import IRefSystemController, IIGRController, IServerStatsController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_UNAVAILABLE_DATA_PLACEHOLDER = '--'
_ITEM_TYPE_TO_TOOLTIP_DICT = {GUI_ITEM_TYPE.SHELL: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_SHELL),
 GUI_ITEM_TYPE.EQUIPMENT: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_EQUIPMENT),
 GUI_ITEM_TYPE.OPTIONALDEVICE: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_OPTIONALDEVICE),
 GUI_ITEM_TYPE.VEHICLE_MODULES: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_MODULE),
 GUI_ITEM_TYPE.VEHICLE: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_VEHICLE),
 ACTION_TOOLTIPS_TYPE.BOOSTER: i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_TYPE_BOOSTERS)}

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

    def _getHighLightType(self):
        return SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def getDisplayableData(self, *args, **kwargs):
        return {'blocksData': self._packBlocks(*args, **kwargs),
         'marginAfterBlock': self.__marginAfterBlock,
         'marginAfterSeparator': self.__marginAfterSeparator,
         'contentMargin': self._getContentMargin(),
         'width': self._getWidth(),
         'highlightType': self._getHighLightType()}


class DynamicBlocksTooltipData(BlocksTooltipData):
    """
    This tooltip can be updated during its displaying.
    """

    def __init__(self, context, toolTipType):
        super(DynamicBlocksTooltipData, self).__init__(context, toolTipType)
        self.__isVisible = False

    def stopUpdates(self):
        """
        The method is called when Tooltip manager is disposed.
        But this tooltip will be alive during the whole app life cycle
        """
        self.__isVisible = False

    def isVisible(self):
        return self.__isVisible

    def changeVisibility(self, isVisible):
        self.__isVisible = isVisible

    def updateData(self):
        if self.isVisible() and self.app is not None:
            self.app.updateTooltip(self.buildToolTip(), self.getType())
        return


class EfficiencyTooltipData(BlocksTooltipData):
    _packers = {BATTLE_EFFICIENCY_TYPES.ARMOR: efficiency.ArmorItemPacker,
     BATTLE_EFFICIENCY_TYPES.DAMAGE: efficiency.DamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: efficiency.KillItemPacker,
     BATTLE_EFFICIENCY_TYPES.DETECTION: efficiency.DetectionItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: efficiency.AssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.CRITS: efficiency.CritsItemPacker,
     BATTLE_EFFICIENCY_TYPES.CAPTURE: efficiency.CaptureItemPacker,
     BATTLE_EFFICIENCY_TYPES.DEFENCE: efficiency.DefenceItemPacker,
     BATTLE_EFFICIENCY_TYPES.STUN: efficiency.StunItemPacker}

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.EFFICIENCY)
        self._setWidth(300)

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
    lobbyContext = dependency.descriptor(ILobbyContext)

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
                statusDescription = ms('#tooltips:Contact/resource/%s' % resourceID)
            commonGuiData['statusDescription'] = statusDescription
            if defaultName and USER_TAG.INVALID_NAME in tags:
                commonGuiData['userProps']['userName'] = defaultName
            units = []
            currentUnit = ''
            region = self.lobbyContext.getRegionCode(userEntity.getID())
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
            if USER_TAG.IGNORED in tags or USER_TAG.IGNORED_TMP in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += ms(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_IGNORED)
            if USER_TAG.SUB_PENDING_IN in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += ms(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_FRIENDSHIPREQUEST)
            if groupsStr != '':
                units.append(self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_GROUPS, groupsStr + '.'))
            if len(units) > 0:
                commonGuiData['units'] = units
            return commonGuiData

    def __makeUnitStr(self, descr, val):
        return makeHtmlString('html_templates:contacts/contact', 'tooltipUnitTxt', {'descr': ms(descr),
         'value': val})

    def __makeIconUnitStr(self, icon, descr):
        return self.__converter.makeIconTag(iconPath=icon) + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': ms(descr)})

    def __makeReferralStr(self, descr):
        return self.__converter.makeIconTag(key='referrTag') + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': ms(descr)})

    def __addBR(self, currentUnit):
        return '<br/>' if currentUnit != '' else ''

    def __addComma(self, currStr):
        return ', ' if currStr != '' else ''


class StrongholdTooltipData(ToolTipBaseData):

    def _getEntity(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        return dispatcher.getEntity()

    def _getData(self):
        return self._getEntity().getStrongholdSettings()


class SortieDivisionTooltipData(StrongholdTooltipData):

    def __init__(self, context):
        super(SortieDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self):
        if not self._getEntity().isStrongholdSettingsValid():
            return
        headerData = self._getEntity().getStrongholdSettings().getHeader()
        isSortie = self._getEntity().isSortie()
        minLvl = headerData.getMinLevel()
        maxLvl = headerData.getMaxLevel()
        divisLevel = int2roman(minLvl)
        if maxLvl != minLvl:
            divisLevel += ' - ' + int2roman(maxLvl)
        minPlayers = headerData.getMinPlayersCount()
        maxPlayers = headerData.getMaxPlayersCount()
        divisPlayers = str(minPlayers)
        if minPlayers != maxPlayers:
            divisPlayers += '-' + str(maxPlayers)
        battleDuration = headerData.getBattleDurationMinutes()
        minutes = i18n.makeString(FORTIFICATIONS.STRONGHOLDTOOLTIPS_MINUTS)
        hours = i18n.makeString(FORTIFICATIONS.STRONGHOLDTOOLTIPS_HOURS)
        battleDurationTime = '%d%s' % (battleDuration, minutes)
        divisionData = {}
        level = int2roman(maxLvl)
        if self._getEntity().isSortie():
            divisTime = battleDurationTime
            divisName = i18n.makeString(FORTIFICATIONS.STRONGHOLDTOOLTIPS_SORTIETITLE, level=level)
        else:
            battleSeriesDurationMinuts = headerData.getBattleSeriesDurationMinuts()
            battleSeriesDurationHours = headerData.getBattleSeriesDurationHours()
            if battleSeriesDurationHours >= 1:
                battleSeriesDurationTime = '%d%s' % (battleSeriesDurationHours, hours)
            else:
                battleSeriesDurationTime = '%d%s' % (battleSeriesDurationMinuts, minutes)
            divisTime = '%s (%s)' % (battleDurationTime, battleSeriesDurationTime)
            direction = getDirection(headerData.getDirection())
            divisName = i18n.makeString(FORTIFICATIONS.STRONGHOLDTOOLTIPS_FORTTITLE, direction=direction)
        resourceMultiplier = headerData.getIndustrialResourceMultiplier()
        if resourceMultiplier > 1:
            dailyBonus = 'x%d' % resourceMultiplier
            divisionData['dailyBonus'] = dailyBonus
        divisionData['isSortie'] = isSortie
        divisionData['divisName'] = divisName
        divisionData['divisLevels'] = divisLevel
        divisionData['divisLegionnaires'] = str(headerData.getMaxLegionariesCount())
        divisionData['divisPlayers'] = divisPlayers
        divisionData['divisTime'] = divisTime
        return {'divisions': [divisionData]}

    def __getPlayerLimitsStr(self, minCount, maxCount):
        return text_styles.main(str(minCount) + ' - ' + str(maxCount))

    def __getBonusStr(self, bonus):
        return ''.join((text_styles.defRes(BigWorld.wg_getIntegralFormat(bonus) + ' '), icons.nut()))


class ReserveTooltipData(StrongholdTooltipData):

    def __init__(self, context):
        super(ReserveTooltipData, self).__init__(context, TOOLTIP_TYPE.RESERVE)

    def __getSelectReason(self, reserve, selected):
        reasonMap = {SUPPORT_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_SUPPORTACTIVATION,
         REQUISITION_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_REQUISITIONACTIVATION,
         HEAVYTRUCKS_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_HEAVYTRUCKSACTIVATION}
        if selected:
            title = i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_SELECTED)
        else:
            title = i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_READYTOSELECT)
        groupType = reserve.getGroupType()
        reason = i18n.makeString(reasonMap[groupType])
        return (title, reason)

    def getDisplayableData(self, *args, **kwargs):
        data = self._getData()
        reserves = data.getReserve()
        isLegionary = self._getEntity().getPlayerInfo().isLegionary()
        toolTipData = {}
        reserveId = args[0]
        reserve = reserves.getReserveById(reserveId)
        moduleLabel = getReserveNameVO(reserve.getType())
        infoLevel = '%s %s' % (int2roman(reserve.getLevel()), i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_LEVEL))
        selected = reserve in reserves.getSelectedReserves()
        reserveCount = reserves.getReserveCount(reserve.getType(), reserve.getLevel())
        if selected:
            reserveCount -= 1
        infoCount = i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_INSTORAGE, count=reserveCount)
        infoDescription1 = '+%s%%' % reserve.getBonusPercent()
        infoDescription2 = '%s' % reserve.getDescription()
        infoDescription3 = i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_CONDITIONREQUISITION) if reserve.isRequsition() else i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_CONDITION)
        selected = reserve in reserves.getSelectedReserves()
        infoStatus, infoDescription = self.__getSelectReason(reserve, selected)
        toolTipData['moduleLabel'] = moduleLabel
        toolTipData['infoTitle'] = reserve.getTitle()
        toolTipData['infoDescription'] = infoDescription
        toolTipData['level'] = reserve.getLevel()
        toolTipData['infoLevel'] = infoLevel
        if not isLegionary:
            toolTipData['infoCount'] = infoCount
        toolTipData['infoDescription1'] = infoDescription1
        toolTipData['infoDescription2'] = infoDescription2
        toolTipData['infoDescription3'] = infoDescription3
        toolTipData['infoStatus'] = infoStatus
        return toolTipData


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
    connectionMgr = dependency.descriptor(IConnectionManager)

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
        if self.connectionMgr.peripheryID == 0:
            serverBlocks.append(self.__packServerBlock(wrapServerName(self.connectionMgr.serverUserName), self.__getPingData(self.connectionMgr.url), HOST_AVAILABILITY.IGNORED, True, isColorBlind))
        if len(simpleHostList):
            currServUrl = self.connectionMgr.url
            serverBlocks.append(self.__packServerListBlock(simpleHostList, currServUrl, isColorBlind))
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
        pingValue, pingStatus = pingData
        pintStr = formatPingStatus(csisStatus, isColorBlind, isSelected, pingStatus, pingValue)
        return formatters.packTextParameterBlockData(cls.__formatServerName(name, isSelected), pintStr, valueWidth=55, gap=2, padding=formatters.packPadding(left=40))

    @classmethod
    def __packServerListBlock(cls, simpleHostList, currServUrl, isColorBlind=False):
        """
        Collect all server names and statuses for one textBlock
        """
        serverNames = []
        pingTexts = []
        for key, name, csisStatus, peripheryID in simpleHostList:
            pingValue, pingStatus = cls.__getPingData(key)
            isSelected = currServUrl == key
            pintStr = formatPingStatus(csisStatus, isColorBlind, isSelected, pingStatus, pingValue)
            serverNames.append(cls.__formatServerName(name, isSelected))
            pingTexts.append(pintStr)

        return formatters.packTextParameterBlockData(concatStylesToMultiLine(*serverNames), concatStylesToMultiLine(*pingTexts), valueWidth=55, gap=2, padding=formatters.packPadding(left=40))

    @classmethod
    def __formatServerName(cls, name, isSelected=False):
        if isSelected:
            result = text_styles.main(name + ' ' + ms(TOOLTIPS.HEADER_MENU_SERVER_CURRENT))
        else:
            result = text_styles.standard(name)
        return result

    @classmethod
    def __getPingData(cls, url):
        pingData = g_preDefinedHosts.getHostPingData(url)
        if pingData.status == PING_STATUSES.REQUESTED:
            return PingData(pingData.value, PING_STATUSES.UNDEFINED)
        else:
            return pingData


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
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, type, key, newPrice, oldPrice, isBuying, forCredits=False, rentPackage=None):
        descr = ''
        newPrice = Money.makeFromMoneyTuple(newPrice)
        oldPrice = Money.makeFromMoneyTuple(oldPrice)
        hasRentCompensation = False
        hasPersonalDiscount = False
        rentCompensation = None
        defaultCurrencyType = Currency.GOLD
        itemName = ''
        deviceNameType = None
        deviceName = None
        if type == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            if key == 'freeXPToTManXPRate':
                defaultCurrencyType = 'freeXp'
        elif type == ACTION_TOOLTIPS_TYPE.RENT:
            item = self.itemsCache.items.getItemByCD(int(key))
            itemName = '%s/rent/price' % item.name.split(':')[-1]
            deviceNameType = item.itemTypeID
        elif type == ACTION_TOOLTIPS_TYPE.ITEM:
            item = self.itemsCache.items.getItemByCD(int(key))
            if item.itemTypeID in GUI_ITEM_TYPE.VEHICLE_COMPONENTS:
                itemName = '%s/price' % item.name
            elif item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                itemName = '%s/%s' % (item.name.split(':')[-1], 'price')
            deviceNameType = item.itemTypeID
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                shop = self.itemsCache.items.shop
                shopPrice = shop.getItemPrice(item.intCD)
                personalPrice = shop.getPersonalVehicleDiscountPrice(item.intCD)
                if personalPrice is not None and personalPrice.getSignValue(defaultCurrencyType) <= shopPrice.getSignValue(defaultCurrencyType):
                    hasPersonalDiscount = True
            if not isBuying:
                sellingActions = self.eventsCache.getItemAction(item, False, forCredits)
                if sellingActions:

                    def filterFunc(item):
                        (forGold, _), _ = item
                        return forGold

                    sellForGoldAction = findFirst(filterFunc, sellingActions)
                    if sellForGoldAction:
                        defaultCurrencyType = Currency.GOLD
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                if item.isRented and not item.rentalIsOver and item.rentCompensation.gold > 0:
                    hasRentCompensation = True
                    rentCompensation = item.rentCompensation.gold
        elif type == ACTION_TOOLTIPS_TYPE.CAMOUFLAGE:
            intCD, type = cPickle.loads(key)
            item = self.itemsCache.items.getItemByCD(int(intCD))
            itemName = '%s/camouflage/priceFactor' % item.name.split(':')[-1]
        elif type == ACTION_TOOLTIPS_TYPE.EMBLEMS:
            group, type = cPickle.loads(key)
            itemName = '%s/priceFactor' % group
        elif type == ACTION_TOOLTIPS_TYPE.AMMO:
            item = self.itemsCache.items.getItemByCD(int(key))
            itemName = '%s/price' % item.name
            deviceNameType = item.itemTypeID
        elif type == ACTION_TOOLTIPS_TYPE.BOOSTER:
            item = self.goodiesCache.getBooster(int(key))
            itemName = 'booster_%s/price' % item.boosterID
            deviceNameType = ACTION_TOOLTIPS_TYPE.BOOSTER
        _ms = makeHtmlString
        _template = 'html_templates:lobby/quests/actions'
        _format = BigWorld.wg_getGoldFormat
        fmtNewGold = _ms(_template, defaultCurrencyType, {'value': _format(newPrice.gold)}) if newPrice.gold else ''
        fmtNewCredits = _ms(_template, Currency.CREDITS, {'value': _format(newPrice.credits)}) if newPrice.credits else ''
        fmtNewCrystal = _ms(_template, Currency.CRYSTAL, {'value': _format(newPrice.crystal)}) if newPrice.crystal else ''
        fmtOldGold = _ms(_template, defaultCurrencyType, {'value': _format(oldPrice.gold)}) if oldPrice.gold else ''
        fmtOldCredits = _ms(_template, Currency.CREDITS, {'value': _format(oldPrice.credits)}) if oldPrice.credits else ''
        fmtOldCrystal = _ms(_template, Currency.CRYSTAL, {'value': _format(oldPrice.crystal)}) if oldPrice.crystal else ''
        if newPrice.isSet(Currency.GOLD) and newPrice.isSet(Currency.CREDITS):
            formatedNewPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtNewCredits, gold=fmtNewGold)
        elif newPrice.isSet(Currency.GOLD) and newPrice.isSet(Currency.CRYSTAL):
            formatedNewPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtNewCrystal, gold=fmtNewGold)
        elif newPrice.isSet(Currency.CREDITS) and newPrice.isSet(Currency.CRYSTAL):
            formatedNewPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtNewCredits, gold=fmtNewCrystal)
        elif newPrice.isSet(Currency.GOLD):
            formatedNewPrice = fmtNewGold
        elif newPrice.isSet(Currency.CRYSTAL):
            formatedNewPrice = fmtNewCrystal
        else:
            formatedNewPrice = fmtNewCredits
        if oldPrice.isSet(Currency.GOLD) and oldPrice.isSet(Currency.CREDITS):
            formatedOldPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtOldCredits, gold=fmtOldGold)
        elif oldPrice.isSet(Currency.GOLD) and oldPrice.isSet(Currency.CRYSTAL):
            formatedOldPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtOldCrystal, gold=fmtOldGold)
        elif oldPrice.isSet(Currency.CRYSTAL) and oldPrice.isSet(Currency.CREDITS):
            formatedOldPrice = i18n.makeString(TOOLTIPS.ACTIONPRICE_EXCHANGE_CURRENCYOR, credits=fmtOldCredits, gold=fmtOldCrystal)
        elif oldPrice.isSet(Currency.GOLD):
            formatedOldPrice = fmtOldGold
        elif oldPrice.isSet(Currency.CRYSTAL):
            formatedOldPrice = fmtOldCrystal
        else:
            formatedOldPrice = fmtOldCredits
        body = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
        if itemName:
            affectedAction = self.eventsCache.getAffectedAction(itemName)
            if affectedAction:
                actionUserName = ''
                action = self.eventsCache.getActions().get(affectedAction[ACTION_ENTITY_ITEM.ACTION_NAME_IDX])
                if action:
                    actionUserName = i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAME, actionName=action.getUserName())
                deviceName = _ITEM_TYPE_TO_TOOLTIP_DICT.get(deviceNameType, '')
                hasAffectedActions = affectedAction[2]
                if hasAffectedActions or hasPersonalDiscount:
                    descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_SEVERALACTIONS, deviceName=deviceName, actionName=actionUserName)
                else:
                    descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, actionName=actionUserName)
        if hasPersonalDiscount:
            descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORPERSONALDISCOUNT)
        if hasRentCompensation:
            formattedRentCompensation = makeHtmlString('html_templates:lobby/quests/actions', Currency.GOLD, {'value': BigWorld.wg_getGoldFormat(rentCompensation)})
            descr += '\n' + i18n.makeString(TOOLTIPS.ACTIONPRICE_RENTCOMPENSATION, rentCompensation=formattedRentCompensation)
        if not isBuying and deviceName is not None:
            headerText = i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_HEADER)
            bodyText = i18n.makeString(TOOLTIPS.ACTIONPRICE_SELL_BODY, deviceName=deviceName) + '\n\n' + body
        elif not isBuying:
            headerText = i18n.makeString(TOOLTIPS.ACTIONPRICE_CHANGEPRICE_HEADER)
            bodyText = i18n.makeString(TOOLTIPS.ACTIONPRICE_CHANGEPRICE_BODY) + '\n\n' + body
        else:
            headerText = i18n.makeString(TOOLTIPS.ACTIONPRICE_HEADER)
            bodyText = descr + '\n\n' + body if descr else body
        return {'header': headerText,
         'body': bodyText}


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
            moreVehsStr = ms(TOOLTIPS.QUESTS_VEHICLESBONUS_VEHICLESLEFT, count=vehiclesLeft)
            col2.append(text_styles.warning(moreVehsStr))
            col2Str = '<br>'.join(col2)
            columns = [col1Str, col2Str]
        return {'name': ms(TOOLTIPS.QUESTS_VEHICLESBONUS_TITLE),
         'columns': columns}


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


_CurrencySetting = namedtuple('_CurrencySetting', 'text, icon, textStyle, frame')

class CURRENCY_SETTINGS(object):
    BUY_CREDITS_PRICE = 'buyCreditsPrice'
    RESTORE_PRICE = 'restorePrice'
    BUY_GOLD_PRICE = 'buyGoldPrice'
    BUY_CRYSTAL_PRICE = 'buyCrystalPrice'
    RENT_CREDITS_PRICE = 'rentCreditsPrice'
    RENT_GOLD_PRICE = 'rentGoldPrice'
    SELL_PRICE = 'sellPrice'
    UNLOCK_PRICE = 'unlockPrice'
    __BUY_SETTINGS = {Currency.CREDITS: BUY_CREDITS_PRICE,
     Currency.GOLD: BUY_GOLD_PRICE,
     Currency.CRYSTAL: BUY_CRYSTAL_PRICE}
    __RENT_SETTINGS = {Currency.CREDITS: RENT_CREDITS_PRICE,
     Currency.GOLD: RENT_GOLD_PRICE}

    @classmethod
    def getRentSetting(cls, currency):
        return cls.__RENT_SETTINGS.get(currency, cls.RENT_CREDITS_PRICE)

    @classmethod
    def getBuySetting(cls, currency):
        return cls.__BUY_SETTINGS.get(currency, cls.BUY_CREDITS_PRICE)


_OPERATIONS_SETTINGS = {CURRENCY_SETTINGS.BUY_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.RESTORE_PRICE: _CurrencySetting('#tooltips:vehicle/restore_price', icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.BUY_GOLD_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.BUY_CRYSTAL_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.crystal(), text_styles.crystal, ICON_TEXT_FRAMES.CRYSTAL),
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
            actionText = text_styles.main(ms(TOOLTIPS.VEHICLE_ACTION_PRC, actionPrc=text_styles.stats(str(percent) + '%'), oldPrice=oldPriceText))
            text = text_styles.concatStylesToMultiLine(text, actionText)
            settingsFrame = settings.frame
            if settingsFrame in Currency.ALL:
                newPrice = MONEY_UNDEFINED.replace(settingsFrame, price)
                oldPrice = MONEY_UNDEFINED.replace(settingsFrame, oldPrice)
            else:
                newPrice = Money(credits=price)
                oldPrice = Money(credits=oldPrice)
            return formatters.packSaleTextParameterBlockData(name=text, saleData={'newPrice': newPrice.toMoneyTuple(),
             'oldPrice': oldPrice.toMoneyTuple(),
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


class HeaderCrystalInfo(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(HeaderCrystalInfo, self).__init__(ctx, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI)
        self._setContentMargin(top=20, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=0)
        self._setWidth(280)

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(HeaderCrystalInfo, self)._packBlocks(*args, **kwargs)
        titleBlocks = list()
        titleBlocks.append(formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HEADER_BUTTONS_CRYSTAL_TITLE), text_styles.standard(TOOLTIPS.HEADER_BUTTONS_CRYSTAL_CURRENCYDESC), padding=formatters.packPadding(bottom=15)))
        tooltipBlocks.append(formatters.packBuildUpBlockData(titleBlocks))
        valueBlocks = list()
        valueBlock = formatters.packTextParameterWithIconBlockData(text_styles.crystal(TOOLTIPS.HEADER_BUTTONS_CRYSTAL_AVAILABLE), text_styles.crystal(BigWorld.wg_getIntegralFormat(self.itemsCache.items.stats.money.crystal)), RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICONBIG, padding=formatters.packPadding(bottom=15), valueWidth=84)
        valueBlocks.append(valueBlock)
        tooltipBlocks.append(formatters.packBuildUpBlockData(valueBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        decsBlocks = list()
        decsBlocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.HEADER_BUTTONS_CRYSTAL_FIRSTDESC), padding=formatters.packPadding(bottom=10)))
        decsBlocks.append(formatters.packTextBlockData(text_styles.standard(TOOLTIPS.HEADER_BUTTONS_CRYSTAL_SECONDDESC)))
        tooltipBlocks.append(formatters.packBuildUpBlockData(decsBlocks))
        return tooltipBlocks


class MissionsToken(BlocksTooltipData):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(MissionsToken, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=13, left=12, bottom=0, right=0)
        self._setMargins(afterBlock=6, afterSeparator=16)
        self._setWidth(298)

    def _packBlocks(self, tokenId, questId, *args):
        items = super(MissionsToken, self)._packBlocks(*args)
        mainQuest = self.eventsCache.getQuests()[questId]
        children = mainQuest.getChildren()[tokenId]

        def filterfunc(quest):
            return quest.getGroupID() == mainQuest.getGroupID() and quest.getID() in children

        quests = self.eventsCache.getQuests(filterfunc).values()
        quests = sorted(quests, missionsSortFunc, reverse=True)
        curToken = None
        for token in mainQuest.accountReqs.getTokens():
            if token.getID() == tokenId:
                curToken = token
                break

        items.append(self.__packTitleBlock(curToken))
        items.append(self.__packQuestsBlock(quests))
        items.append(self.__packBottomBlock(curToken))
        return items

    def __packTitleBlock(self, token):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(makeString(TOOLTIPS.MISSIONS_TOKEN_HEADER, name=makeString(token.getUserName()))), img=token.getImage(TOKEN_SIZES.MEDIUM), txtPadding={'top': 14,
         'left': 11,
         'right': 5})

    def __packQuestsBlock(self, quests):
        blocks = []
        if len(quests) == 1:
            quest = quests[0]
            blocks.append(formatters.packTextBlockData(text_styles.main(makeString(TOOLTIPS.MISSIONS_TOKEN_QUESTS_SINGLE, name=text_styles.neutral(quest.getUserName()))), padding={'left': -10}))
        else:
            blocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.MISSIONS_TOKEN_QUESTS_MULTIPLE), padding={'left': -10,
             'bottom': 6}))
            for quest in quests:
                questName = makeString(MENU.QUOTE, string=quest.getUserName())
                blocks.append(formatters.packTextBlockData(text_styles.main(makeString(TOOLTIPS.MISSIONS_TOKEN_QUEST, name=text_styles.neutral(questName))), padding={'top': -4}))

        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding={'left': 17,
         'bottom': 13})

    def __packBottomBlock(self, token):
        needCount = token.getNeededCount()
        gotCount = token.getReceivedCount()
        if not gotCount:
            text = text_styles.main(TOOLTIPS.MISSIONS_TOKEN_PROGRESS_NONE)
        else:
            text = text_styles.main(makeString(TOOLTIPS.MISSIONS_TOKEN_PROGRESS, current=text_styles.neutral(gotCount), total=str(needCount)))
        return formatters.packAlignedTextBlockData(text, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding={'top': -1,
         'bottom': 15,
         'left': -12})

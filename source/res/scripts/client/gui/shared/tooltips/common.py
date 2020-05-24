# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
import logging
import math
from collections import namedtuple, defaultdict
import ArenaType
import constants
from soft_exception import SoftException
import ResMgr
import nations
from gui import g_htmlTemplates, makeHtmlString, GUI_NATIONS
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getReserveNameVO, getDirection
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.ARENAS import ARENAS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clans import formatters as clans_fmts
from gui.clans.items import formatField
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.battle_pass_chose_winner_tooltip_view import BattlePassChoseWinnerTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.lobby.battle_pass.tooltips.vehicle_points_tooltip_view import VehiclePointsTooltipView
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control.items.stronghold_items import SUPPORT_TYPE, REQUISITION_TYPE, HEAVYTRUCKS_TYPE
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.server_events.events_helpers import missionsSortFunc
from gui.server_events.formatters import TOKEN_SIZES, DISCOUNT_TYPE
from gui.shared.formatters import formatActionPrices
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.servers import formatPingStatus, wrapServerName
from gui.shared.formatters.text_styles import concatStylesToMultiLine
from gui.shared.formatters.time_formatters import getTimeLeftStr, getTillTimeByResource
from gui.shared.gui_items import GUI_ITEM_TYPE, ACTION_ENTITY_ITEM
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE, ToolTipParameterField
from gui.shared.tooltips import efficiency
from gui.shared.tooltips import formatters
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from helpers import i18n, time_utils, html, int2roman
from helpers.i18n import makeString
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter, makeClanFullName, makeContactStatusDescription
from messenger.m_constants import USER_TAG
from messenger.storage import storage_getter
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY, PING_STATUSES, PingData
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IIGRController, IServerStatsController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.techtree_events import ITechTreeEventsListener
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)
_UNAVAILABLE_DATA_PLACEHOLDER = '--'
_PARENTHESES_OPEN = '('
_PARENTHESES_CLOSE = ')'
_SPACE = ' '
_ITEM_TYPE_TO_TOOLTIP_DICT = {GUI_ITEM_TYPE.SHELL: backport.text(R.strings.tooltips.actionPrice.sell.type.shell()),
 GUI_ITEM_TYPE.EQUIPMENT: backport.text(R.strings.tooltips.actionPrice.sell.type.equipment()),
 GUI_ITEM_TYPE.OPTIONALDEVICE: backport.text(R.strings.tooltips.actionPrice.sell.type.optionalDevice()),
 GUI_ITEM_TYPE.VEHICLE_MODULES: backport.text(R.strings.tooltips.actionPrice.sell.type.module()),
 GUI_ITEM_TYPE.VEHICLE: backport.text(R.strings.tooltips.actionPrice.sell.type.vehicle()),
 ACTION_TOOLTIPS_TYPE.BOOSTER: backport.text(R.strings.tooltips.actionPrice.sell.type.boosters())}

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
                        if metaList:
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
                    if metaList and leftTime > 0:
                        header = makeHtmlString('html_templates:lobby/tooltips', 'prem_igr_veh_quest_header', ctx={'qLabel': metaList[0].format()})
                        text = i18n.makeString('#tooltips:vehicleIgr/specialAbility')
                        localization = '#tooltips:vehicleIgr/%s'
                        actionLeft = getTimeLeftStr(localization, leftTime, timeStyle=text_styles.stats)
                        text += '\n' + actionLeft
                        premVehQuests.append({'header': header,
                         'descr': text})

        descriptionTemplate = 'igr_description' if not qLabels else 'igr_description_with_quests'
        igrPercent = (self.igrCtrl.getXPFactor() - 1) * 100
        igrType = self.igrCtrl.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == constants.IGR_TYPE.PREMIUM else 'basic')
        return {'title': backport.text(R.strings.tooltips.igr.title(), igrIcon=icon),
         'description': makeHtmlString('html_templates:lobby/tooltips', descriptionTemplate, {'igrValue': '{0}%'.format(backport.getIntegralFormat(igrPercent))}),
         'quests': [ i.format(**template.ctx) for i in qLabels ],
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
        self.item = None
        return

    @classmethod
    def addAdvancedBlock(cls, data, disableAnim):
        displayableData = data['data']
        block = formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LOBBY_ICONBTNALT, txtOffset=40, padding=formatters.packPadding(bottom=-7, top=-5, left=20 - displayableData['contentMargin']['left']), desc=text_styles.main(backport.text(R.strings.tooltips.advanced.info())), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ADVANCED_KEY_BLOCK_LINKAGE)
        block['data']['animated'] = not disableAnim
        displayableData['blocksData'].append(block)

    def getDisplayableData(self, *args, **kwargs):
        return {'blocksData': self._packBlocks(*args, **kwargs),
         'marginAfterBlock': self.__marginAfterBlock,
         'marginAfterSeparator': self.__marginAfterSeparator,
         'contentMargin': self._getContentMargin(),
         'width': self._getWidth(),
         'highlightType': self._getHighLightType()}

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


class FakeTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(FakeTooltipData, self).__init__(context, TOOLTIP_TYPE.FAKE)


class DynamicBlocksTooltipData(BlocksTooltipData):

    def __init__(self, context, toolTipType):
        super(DynamicBlocksTooltipData, self).__init__(context, toolTipType)
        self.__isVisible = False

    def isDynamic(self):
        return True

    def stopUpdates(self):
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
     BATTLE_EFFICIENCY_TYPES.ASSIST_STUN: efficiency.StunItemPacker}

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.EFFICIENCY)
        self._setWidth(300)

    def _packBlocks(self, data):
        return self._packers[data.type]().pack(data.toDict()) if data is not None and data.type in self._packers else []


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
            if resourceID == constants.WG_GAMES.TANKS:
                statusDescription = makeContactStatusDescription(userEntity.isOnline(), tags, userEntity.getClientInfo())
            else:
                statusDescription = makeString('#tooltips:Contact/resource/%s' % resourceID)
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
            if currentUnit != '':
                units.append(currentUnit)
            groupsStr = ''
            userGroups = userEntity.getGroups()
            if userGroups:
                groupsStr += ', '.join(map(html.escape, userGroups))
            if clanAbbrev and USER_TAG.CLAN_MEMBER in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeClanFullName(clanAbbrev)
            if USER_TAG.IGNORED in tags or USER_TAG.IGNORED_TMP in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_IGNORED)
            if USER_TAG.SUB_PENDING_IN in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_FRIENDSHIPREQUEST)
            if groupsStr != '':
                units.append(self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_GROUPS, groupsStr + '.'))
            if units:
                commonGuiData['units'] = units
            return commonGuiData

    def __makeUnitStr(self, descr, val):
        return makeHtmlString('html_templates:contacts/contact', 'tooltipUnitTxt', {'descr': makeString(descr),
         'value': val})

    def __makeIconUnitStr(self, icon, descr):
        return self.__converter.makeIconTag(iconPath=icon) + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': makeString(descr)})

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
        return ''.join((text_styles.defRes(backport.getIntegralFormat(bonus) + ' '), icons.nut()))


class ReserveTooltipData(StrongholdTooltipData):

    def __init__(self, context):
        super(ReserveTooltipData, self).__init__(context, TOOLTIP_TYPE.RESERVE)

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
        infoCount = i18n.makeString(FORTIFICATIONS.STRONGHOLDRESERVE_TOOLTIP_INSTORAGE, count=makeHtmlString('html_templates:lobby/fortifications/strongholdReserve', 'inStorage', {'text': reserveCount}))
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
        if simpleHostList:
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
        pingValue, pingStatus = pingData
        pintStr = formatPingStatus(csisStatus, isColorBlind, isSelected, pingStatus, pingValue, useBigSize=True)
        return formatters.packTextParameterBlockData(cls.__formatServerName(name, isSelected), pintStr, valueWidth=55, gap=2, padding=formatters.packPadding(left=40))

    @classmethod
    def __packServerListBlock(cls, simpleHostList, currServUrl, isColorBlind=False):
        serverNames = []
        pingTexts = []
        for key, name, csisStatus, _ in simpleHostList:
            pingValue, pingStatus = cls.__getPingData(key)
            isSelected = currServUrl == key
            pintStr = formatPingStatus(csisStatus, isColorBlind, isSelected, pingStatus, pingValue, useBigSize=True)
            serverNames.append(cls.__formatServerName(name, isSelected))
            pingTexts.append(pintStr)

        return formatters.packTextParameterBlockData(concatStylesToMultiLine(*serverNames), concatStylesToMultiLine(*pingTexts), valueWidth=55, gap=2, padding=formatters.packPadding(left=40))

    @classmethod
    def __formatServerName(cls, name, isSelected=False):
        if isSelected:
            result = text_styles.main(name + ' ' + makeString(TOOLTIPS.HEADER_MENU_SERVER_CURRENT))
        else:
            result = text_styles.standard(name)
        return result

    @classmethod
    def __getPingData(cls, url):
        pingData = g_preDefinedHosts.getHostPingData(url)
        return PingData(pingData.value, PING_STATUSES.UNDEFINED) if pingData.status == PING_STATUSES.REQUESTED else pingData


class ClanCommonInfoTooltipData(ToolTipBaseData):
    clanCtrl = dependency.descriptor(IWebController)

    def __init__(self, context):
        super(ClanCommonInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.CLAN_PROFILE)
        self.__usersInfoHelper = UsersInfoHelper()

    def getDisplayableData(self, clanDBID):
        data = self.clanCtrl.getClanCommonData(clanDBID)
        if data is None:
            return {}
        else:
            rating = formatField(getter=data.getRating, formatter=backport.getIntegralFormat)
            count = formatField(getter=data.getBattlesCount, formatter=backport.getIntegralFormat)
            wins = formatField(getter=data.getWinsRatio, formatter=lambda value: backport.getNiceNumberFormat(value) + '%')
            exp = formatField(getter=data.getAvgExp, formatter=backport.getIntegralFormat)
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


class _BattleStatus(object):
    __slots__ = ('level', 'msg', 'style', 'prefix')

    def __init__(self, level, msg, style, prefix):
        super(_BattleStatus, self).__init__()
        self.level = level
        self.msg = msg
        self.style = style
        self.prefix = prefix

    def getMsgText(self):
        return makeString(self.msg)

    def getResText(self, count):
        return ''.join((self.style('%s %s' % (self.prefix, backport.getIntegralFormat(count))), icons.nut()))


class ActionTooltipData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, itemType, key, newPrice, oldPrice, isBuying, forCredits=False, rentPackage=None):
        descr = ''
        hasRentCompensation = False
        hasPersonalDiscount = False
        rentCompensation = None
        itemName = ''
        deviceNameType = None
        deviceName = None
        if itemType == ACTION_TOOLTIPS_TYPE.RENT:
            item = self.itemsCache.items.getItemByCD(int(key))
            itemName = '%s/rent/price' % item.name.split(':')[-1]
            deviceNameType = item.itemTypeID
        elif itemType == ACTION_TOOLTIPS_TYPE.ITEM:
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
                if personalPrice is not None and personalPrice.getShortage(shopPrice).isDefined():
                    hasPersonalDiscount = True
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                if item.isRented and not item.rentalIsOver and item.rentCompensation.gold > 0:
                    hasRentCompensation = True
                    rentCompensation = item.rentCompensation.gold
        elif itemType == ACTION_TOOLTIPS_TYPE.CAMOUFLAGE:
            intCD, itemType = cPickle.loads(key)
            item = self.itemsCache.items.getItemByCD(int(intCD))
            itemName = '%s/camouflage/priceFactor' % item.name.split(':')[-1]
        elif itemType == ACTION_TOOLTIPS_TYPE.EMBLEMS:
            group, itemType = cPickle.loads(key)
            itemName = '%s/priceFactor' % group
        elif itemType == ACTION_TOOLTIPS_TYPE.AMMO:
            item = self.itemsCache.items.getItemByCD(int(key))
            itemName = '%s/price' % item.name
            deviceNameType = item.itemTypeID
        elif itemType == ACTION_TOOLTIPS_TYPE.BOOSTER:
            item = self.goodiesCache.getBooster(int(key))
            itemName = 'booster_%s/price' % item.boosterID
            deviceNameType = ACTION_TOOLTIPS_TYPE.BOOSTER
        elif itemType == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            itemName = key
        template = 'html_templates:lobby/quests/actions'
        formatedOldPrice, formatedNewPrice = formatActionPrices(oldPrice, newPrice, isBuying)
        body = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
        actionUserName = ''
        if itemName:
            affectedAction = self.eventsCache.getAffectedAction(itemName)
            if affectedAction:
                action = self.eventsCache.getActions().get(affectedAction[ACTION_ENTITY_ITEM.ACTION_NAME_IDX])
                if action and action.getUserName():
                    actionUserName = i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAME, actionName=action.getUserName())
                deviceName = _ITEM_TYPE_TO_TOOLTIP_DICT.get(deviceNameType, '')
                hasAffectedActions = affectedAction[ACTION_ENTITY_ITEM.AFFECTED_ACTIONS_IDX]
                if hasAffectedActions or hasPersonalDiscount:
                    if hasPersonalDiscount:
                        action = i18n.makeString(TOOLTIPS.ACTIONPRICE_SEVERALACTIONS_PERSONAL)
                    else:
                        action = i18n.makeString(TOOLTIPS.ACTIONPRICE_SEVERALACTIONS_ACTION, actionName=actionUserName)
                    descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_SEVERALACTIONS, deviceName=deviceName, action=action)
                elif actionUserName:
                    descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, actionName=actionUserName)
        if hasRentCompensation:
            formattedRentCompensation = makeHtmlString(template, Currency.GOLD, {'value': backport.getGoldFormat(rentCompensation)})
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


class ActionSlotTooltipData(ToolTipBaseData):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(ActionSlotTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, newPrice, oldPrice):
        affectedAction = self.eventsCache.getAffectedAction('slotsPrices')
        actionUserName = None
        if affectedAction:
            action = self.eventsCache.getActions().get(affectedAction[ACTION_ENTITY_ITEM.ACTION_NAME_IDX])
            if action:
                actionUserName = i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAMESLOT, actionName=action.getUserName())
        formatedOldPrice, formatedNewPrice = formatActionPrices(oldPrice, newPrice, True)
        template = 'html_templates:lobby/tooltips/'
        headerText = i18n.makeString(TOOLTIPS.TANKS_CAROUSEL_BUY_SLOT_HEADER)
        bodyText = i18n.makeString(TOOLTIPS.TANKS_CAROUSEL_BUY_SLOT_BODY)
        bodyText = '{}\n\n'.format(bodyText)
        sep = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_TOOL_TIP_SEPARATOR, 283, 1, 15, 0)
        if actionUserName is not None:
            fa = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, actionName=text_styles.stats(actionUserName))
            pr = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY_SLOT, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
            bodyText += makeHtmlString(template, 'sell_slot_action', {'separator': sep,
             'foraction': fa,
             'prices': pr})
        return {'header': headerText,
         'body': bodyText}


class BaseDiscountTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(BaseDiscountTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    @classmethod
    def _packDisplayableData(cls, cost, fullCost, currencyType=DISCOUNT_TYPE.GOLD):
        headerText = i18n.makeString(TOOLTIPS.ACTIONPRICE_HEADER)
        bodyText = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=cls._formatPrice(fullCost, currencyType), newPrice=cls._formatPrice(cost, currencyType))
        return {'header': headerText,
         'body': bodyText}

    @staticmethod
    def _formatPrice(cost, currencyType):
        template = 'html_templates:lobby/quests/actions'
        format_ = backport.getGoldFormat
        return makeHtmlString(template, currencyType, {'value': format_(cost)}) if cost is not None else ''


class PriceDiscountTooltipData(BaseDiscountTooltipData):

    def getDisplayableData(self, cost, fullCost, currencyType):
        return self._packDisplayableData(cost, fullCost, currencyType)


class FrontlineDiscountTooltipData(BaseDiscountTooltipData):

    def getDisplayableData(self, cost, fullCost, currencyType=DISCOUNT_TYPE.GOLD, frontlineDiscount=0):
        onlyFrontlineActive = fullCost - frontlineDiscount == cost
        headerText = i18n.makeString(backport.text(R.strings.tooltips.actionPrice.header()))
        if onlyFrontlineActive:
            bodyTemplate = backport.text(R.strings.tooltips.actionPrice.body.frontline())
            discount = frontlineDiscount
        else:
            bodyTemplate = backport.text(R.strings.tooltips.actionPrice.body.frontline_with_sse())
            discount = fullCost - cost
        bodyText = i18n.makeString(bodyTemplate, discount=self._formatPrice(discount, currencyType), oldPrice=self._formatPrice(fullCost, currencyType), newPrice=self._formatPrice(cost, currencyType))
        return {'header': headerText,
         'body': bodyText}


class ActionXPTooltipData(BaseDiscountTooltipData):

    def getDisplayableData(self, newPrice, oldPrice):
        oldPrice = Money.makeFromMoneyTuple(oldPrice)
        if not oldPrice.isDefined():
            oldPrice = Money(credits=0)
        currency = Currency.CREDITS
        for currency in Currency.ALL:
            currencyValue = oldPrice.get(currency)
            if currencyValue is not None:
                break

        newPrice = Money.makeFromMoneyTuple(newPrice)
        if not newPrice.isDefined():
            newPrice = Money.makeFrom(currency, 0)
        isGoldPrice = newPrice.isCurrencyDefined(Currency.GOLD)
        return self._packDisplayableData(newPrice.gold if isGoldPrice else newPrice.credits, oldPrice.gold if isGoldPrice else oldPrice.credits, DISCOUNT_TYPE.FREE_XP if isGoldPrice else DISCOUNT_TYPE.XP)


class ToolTipFortWrongTime(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipFortWrongTime, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, wrongState, timePeriods):

        def formatReceivedData(target):
            return text_styles.error(target)

        if wrongState == 'wrongTime':
            return {'header': i18n.makeString(TOOLTIPS.FORTWRONGTIME_HEADER),
             'body': i18n.makeString(TOOLTIPS.FORTWRONGTIME_BODY, local=backport.getShortTimeFormat(time_utils.getCurrentTimestamp()), server=backport.getShortTimeFormat(time_utils.getCurrentLocalServerTimestamp()))}
        elif (wrongState == 'lockTime' or wrongState == 'ownDefenceTime') and timePeriods is not None and len(timePeriods) >= 1:
            timeStart, timeFinish = timePeriods[0]
            return {'header': i18n.makeString(TOOLTIPS.FORTWRONGTIME_LOCKTIME_HEADER),
             'body': i18n.makeString(TOOLTIPS.FORTWRONGTIME_LOCKTIME_BODY, timeStart=formatReceivedData(timeStart), timeFinish=formatReceivedData(timeFinish))}
        else:
            raise SoftException('%s: Unexpected state: %s' % (self, wrongState))
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


class FortSortieTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(FortSortieTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, data):
        division = text_styles.main(i18n.makeString(data.divisionName))
        inBattleIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_SWORDSICON, 16, 16, -3, 0)
        descriptionText = text_styles.main(i18n.makeString(data.descriptionForTT)) if data.descriptionForTT != '' else ''
        return {'titleText': text_styles.highTitle(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_TITLE, name=data.creatorName)),
         'divisionText': text_styles.standard(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_DIVISION, division=division)),
         'descriptionText': descriptionText,
         'hintText': text_styles.standard(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_HINT)),
         'inBattleText': text_styles.error(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_INBATTLE) + ' ' + inBattleIcon) if data.isInBattle else '',
         'isInBattle': data.isInBattle}


class SettingsMinimapCircles(BlocksTooltipData):

    def __init__(self, context):
        super(SettingsMinimapCircles, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setContentMargin(top=15, left=19, bottom=6, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(364)

    def getTextBlocksForCircleDescr(self, title, body):
        blocks = []
        blocks.append(formatters.packTextBlockData(title, padding={'bottom': 3}))
        blocks.append(formatters.packTextBlockData(body, padding={'bottom': 9}))
        return blocks

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
        maxViewRangeBody = text_styles.main(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_MAXVIEWRANGE_AS3_BODY) % constants.VISIBILITY.MAX_RADIUS
        textBlocks.extend(self.getTextBlocksForCircleDescr(maxViewRangeTitle, maxViewRangeBody))
        drawRangeHtml = makeHtmlString(templateName, 'draw_range_title') + lineBreak
        drawRangeTitle = drawRangeHtml % i18n.makeString(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_DRAWRANGE_TITLE)
        drawRangeBody = text_styles.main(TOOLTIPS.SETTINGS_MINIMAPCIRCLES_DRAWRANGE_BODY)
        textBlocks.extend(self.getTextBlocksForCircleDescr(drawRangeTitle, drawRangeBody))
        tooltipBlocks.append(formatters.packBuildUpBlockData(textBlocks, padding={'top': -1}))
        return tooltipBlocks


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


_CurrencySetting = namedtuple('_CurrencySetting', ('text', 'icon', 'textStyle', 'frame'))

class CURRENCY_SETTINGS(object):
    BUY_CREDITS_PRICE = 'buyCreditsPrice'
    RESTORE_PRICE = 'restorePrice'
    BUY_GOLD_PRICE = 'buyGoldPrice'
    BUY_CRYSTAL_PRICE = 'buyCrystalPrice'
    BUY_EVENT_COIN_PRICE = 'buyEventCoinPrice'
    RENT_CREDITS_PRICE = 'rentCreditsPrice'
    RENT_GOLD_PRICE = 'rentGoldPrice'
    SELL_PRICE = 'sellPrice'
    UNLOCK_PRICE = 'unlockPrice'
    REMOVAL_CREDITS_PRICE = 'removalCreditsPrice'
    REMOVAL_GOLD_PRICE = 'removalGoldPrice'
    REMOVAL_CRYSTAL_PRICE = 'removalCrystalPrice'
    UPGRADABLE_CREDITS_PRICE = 'upgradableCreditsPrice'
    __BUY_SETTINGS = {Currency.CREDITS: BUY_CREDITS_PRICE,
     Currency.GOLD: BUY_GOLD_PRICE,
     Currency.CRYSTAL: BUY_CRYSTAL_PRICE,
     Currency.EVENT_COIN: BUY_EVENT_COIN_PRICE}
    __RENT_SETTINGS = {Currency.CREDITS: RENT_CREDITS_PRICE,
     Currency.GOLD: RENT_GOLD_PRICE}
    __REMOVAL_SETTINGS = {Currency.CREDITS: REMOVAL_CREDITS_PRICE,
     Currency.GOLD: REMOVAL_GOLD_PRICE,
     Currency.CRYSTAL: REMOVAL_CRYSTAL_PRICE}
    __UPGRADABLE_SETTINGS = {Currency.CREDITS: UPGRADABLE_CREDITS_PRICE}

    @classmethod
    def getRentSetting(cls, currency):
        return cls.__RENT_SETTINGS.get(currency, cls.RENT_CREDITS_PRICE)

    @classmethod
    def getBuySetting(cls, currency):
        return cls.__BUY_SETTINGS.get(currency, cls.BUY_CREDITS_PRICE)

    @classmethod
    def getRemovalSetting(cls, currency):
        return cls.__REMOVAL_SETTINGS.get(currency, cls.REMOVAL_GOLD_PRICE)

    @classmethod
    def getUpgradableSetting(cls, currency):
        return cls.__UPGRADABLE_SETTINGS.get(currency, cls.UPGRADABLE_CREDITS_PRICE)


_OPERATIONS_SETTINGS = {CURRENCY_SETTINGS.BUY_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.RESTORE_PRICE: _CurrencySetting('#tooltips:vehicle/restore_price', icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.BUY_GOLD_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.BUY_CRYSTAL_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.crystal(), text_styles.crystal, ICON_TEXT_FRAMES.CRYSTAL),
 CURRENCY_SETTINGS.BUY_EVENT_COIN_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_BUY_PRICE, icons.eventCoin(), text_styles.eventCoin, ICON_TEXT_FRAMES.EVENT_COIN),
 CURRENCY_SETTINGS.RENT_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_MINRENTALSPRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.RENT_GOLD_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_MINRENTALSPRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.SELL_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_SELL_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.UNLOCK_PRICE: _CurrencySetting(TOOLTIPS.VEHICLE_UNLOCK_PRICE, icons.xpCost(), text_styles.expText, ICON_TEXT_FRAMES.XP_PRICE),
 CURRENCY_SETTINGS.REMOVAL_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_DISMANTLING_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS),
 CURRENCY_SETTINGS.REMOVAL_GOLD_PRICE: _CurrencySetting(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_DISMANTLING_PRICE, icons.gold(), text_styles.gold, ICON_TEXT_FRAMES.GOLD),
 CURRENCY_SETTINGS.REMOVAL_CRYSTAL_PRICE: _CurrencySetting(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_DISMANTLING_PRICE, icons.crystal(), text_styles.crystal, ICON_TEXT_FRAMES.CRYSTAL),
 CURRENCY_SETTINGS.UPGRADABLE_CREDITS_PRICE: _CurrencySetting(TOOLTIPS.MODULEFITS_UPGRADABLE_PRICE, icons.credits(), text_styles.credits, ICON_TEXT_FRAMES.CREDITS)}

def _getCurrencySetting(key):
    if key not in _OPERATIONS_SETTINGS:
        _logger.error('Unsupported currency type "%s"!', key)
        return None
    else:
        return _OPERATIONS_SETTINGS[key]


def getFormattedPriceString(price, currencySetting, neededValue=None):
    _int = backport.getIntegralFormat
    settings = _getCurrencySetting(currencySetting)
    if settings is None:
        return
    else:
        valueFormatted = settings.textStyle(_int(price))
        icon = settings.icon
        neededText = getFormattedNeededValue(settings, _int(neededValue)) if neededValue else ''
        return text_styles.concatStylesWithSpace(valueFormatted, icon, neededText)


def getFormattedNeededValue(settings, neededValue):
    needFormatted = settings.textStyle(neededValue)
    neededText = text_styles.concatStylesToSingleLine(text_styles.standard(_PARENTHESES_OPEN), text_styles.error(backport.text(R.strings.tooltips.vehicle.graph.body.notEnough())), _SPACE, needFormatted, _SPACE, settings.icon, text_styles.standard(_PARENTHESES_CLOSE))
    return neededText


def getFormattedDiscountPriceString(currencySetting, percent, oldPrice):
    _int = backport.getIntegralFormat
    settings = _getCurrencySetting(currencySetting)
    if settings is None:
        return
    else:
        icon = settings.icon
        oldPriceText = text_styles.concatStylesToSingleLine(settings.textStyle(_int(oldPrice)), icon)
        text = text_styles.standard(backport.text(R.strings.tooltips.vehicle.action_prc(), actionPrc=text_styles.stats(str(percent) + '%'), oldPrice=oldPriceText))
        return text


def makePriceBlock(price, currencySetting, neededValue=None, oldPrice=None, percent=0, valueWidth=-1, leftPadding=61, forcedText=''):
    _int = backport.getIntegralFormat
    oldPriceText = ''
    hasAction = percent != 0
    settings = _getCurrencySetting(currencySetting)
    if settings is None:
        return
    valueFormatted = settings.textStyle(_int(price))
    icon = settings.icon
    if hasAction:
        oldPriceText = text_styles.concatStylesToSingleLine(icon, settings.textStyle(_int(oldPrice)))
    neededText = getFormattedNeededValue(settings, _int(neededValue)) if neededValue else ''
    text = text_styles.concatStylesWithSpace(text_styles.main(settings.text if not forcedText else forcedText), neededText)
    if hasAction:
        actionText = text_styles.main(makeString(TOOLTIPS.VEHICLE_ACTION_PRC, actionPrc=text_styles.stats(str(percent) + '%'), oldPrice=oldPriceText))
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
    else:
        return formatters.packTextParameterWithIconBlockData(name=text, value=valueFormatted, icon=settings.frame, valueWidth=valueWidth, padding=formatters.packPadding(left=-5))


def makeCompoundPriceBlock(currencySetting, itemPrice, blockWidth=150, forcedText=''):
    settings = _getCurrencySetting(currencySetting)
    if settings is None:
        return
    else:
        blocks = [formatters.packTextBlockData(text_styles.main(settings.text if not forcedText else forcedText)), formatters.packItemPriceBlockData(itemPrice, padding=formatters.packPadding(top=-4))]
        return formatters.packBuildUpBlockData(blocks, blockWidth=blockWidth, padding=formatters.packPadding(bottom=-8))


class SettingsBaseKey(BlocksTooltipData):
    TEMPLATE_NAME = 'html_templates:lobby/tooltips/settings_key_commands'

    def __init__(self, context):
        super(SettingsBaseKey, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setWidth(350)
        self._headerKey = TOOLTIPS.SETTINGS_KEYFOLLOWME_TITLE
        self._enemyBlockImage = ''
        self._enemyBlockTitle = ''
        self._allyBlockImage = ''
        self._allyBlockTitle = ''

    def _getEnemyDescription(self):
        enemyDescriptionHtml = makeHtmlString(SettingsBaseKey.TEMPLATE_NAME, 'enemy_description')
        return text_styles.main(makeString(TOOLTIPS.SETTINGS_KEY_ENEMY_BODY, enemy=enemyDescriptionHtml % i18n.makeString(TOOLTIPS.SETTINGS_KEY_TARGET_ENEMY)))

    def _getAllyDescription(self):
        allyDescriptionHtml = makeHtmlString(SettingsBaseKey.TEMPLATE_NAME, 'ally_description')
        return text_styles.main(makeString(TOOLTIPS.SETTINGS_KEY_ALLY_BODY, ally=allyDescriptionHtml % i18n.makeString(TOOLTIPS.SETTINGS_KEY_TARGET_ALLY)))

    def _packBlocks(self, *args):
        tooltipBlocks = super(SettingsBaseKey, self)._packBlocks()
        headerBlock = formatters.packTitleDescBlock(text_styles.highTitle(self._headerKey))
        enemyBlock = formatters.packImageTextBlockData(title=text_styles.middleTitle(self._enemyBlockTitle), desc=self._getEnemyDescription(), img=self._enemyBlockImage, imgPadding={'left': -4,
         'right': 4}, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding={'top': -8})
        allyBlock = formatters.packImageTextBlockData(title=text_styles.middleTitle(self._allyBlockTitle), desc=self._getAllyDescription(), img=self._allyBlockImage, imgPadding={'left': -4,
         'right': 4}, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding={'top': -8})
        tooltipBlocks.append(headerBlock)
        tooltipBlocks.append(enemyBlock)
        tooltipBlocks.append(allyBlock)
        return tooltipBlocks


class SettingsKeyChargeFire(BlocksTooltipData):

    def __init__(self, context):
        super(SettingsKeyChargeFire, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setWidth(350)
        self._headerKey = TOOLTIPS.SETTINGS_KEYCHARGEFIRE_TITLE
        self._enemyBlockImage = RES_ICONS.MAPS_ICONS_SETTINGS_DUAL_GUN

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(SettingsKeyChargeFire, self)._packBlocks(*args, **kwargs)
        tooltipBlocks.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.highTitle(self._headerKey)), formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.SETTINGS_KEYCHARGEFIRE_DEFAULTKEY), img=self._enemyBlockImage, imgPadding={'left': -4,
          'right': 4}, imgAtLeft=True, txtPadding=None, txtGap=0, txtOffset=-1, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding={'top': -8})]))
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


class HeaderMoneyAndXpTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(HeaderMoneyAndXpTooltipData, self).__init__(ctx, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI)
        self._setContentMargin(top=17, left=20, bottom=18, right=13)
        self._setMargins(afterBlock=0)
        self._setWidth(290)
        self._btnType = None
        return

    def _packBlocks(self, btnType=None, *args, **kwargs):
        tooltipBlocks = super(HeaderMoneyAndXpTooltipData, self)._packBlocks(*args, **kwargs)
        self._btnType = btnType
        if self._btnType is None:
            _logger.error('HeaderMoneyAndXpTooltipData empty btnType!')
            return tooltipBlocks
        else:
            valueBlock = formatters.packMoneyAndXpValueBlock(value=self._getValue(), icon=self._getIcon(), iconYoffset=self._getIconYOffset())
            return formatters.packMoneyAndXpBlocks(tooltipBlocks, btnType=self._btnType, valueBlocks=[valueBlock])

    def _getValue(self):
        valueStr = '0'
        if self._btnType == CURRENCIES_CONSTANTS.GOLD:
            valueStr = text_styles.gold(backport.getIntegralFormat(self.itemsCache.items.stats.money.gold))
        elif self._btnType == CURRENCIES_CONSTANTS.CREDITS:
            valueStr = text_styles.credits(backport.getIntegralFormat(self.itemsCache.items.stats.money.credits))
        elif self._btnType == CURRENCIES_CONSTANTS.CRYSTAL:
            valueStr = text_styles.crystal(backport.getIntegralFormat(self.itemsCache.items.stats.money.crystal))
        elif self._btnType == CURRENCIES_CONSTANTS.EVENT_COIN:
            valueStr = text_styles.eventCoin(backport.getIntegralFormat(self.itemsCache.items.stats.money.eventCoin))
        elif self._btnType == CURRENCIES_CONSTANTS.FREE_XP:
            valueStr = text_styles.expText(backport.getIntegralFormat(self.itemsCache.items.stats.actualFreeXP))
        return valueStr

    def _getIconYOffset(self):
        offset = 2
        if self._btnType == CURRENCIES_CONSTANTS.CRYSTAL:
            offset = 1
        return offset

    def _getIcon(self):
        icon = self._btnType
        if self._btnType == CURRENCIES_CONSTANTS.FREE_XP:
            icon = 'freeXP'
        return icon


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
        quests = sorted(quests, key=missionsSortFunc, reverse=True)
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
            listToAdd = ''
            for quest in quests:
                questName = makeString(MENU.QUOTE, string=quest.getUserName())
                listToAdd = text_styles.concatStylesToMultiLine(listToAdd, text_styles.main(makeString(TOOLTIPS.MISSIONS_TOKEN_QUEST, name=text_styles.neutral(questName))))

            blocks.append(formatters.packTextBlockData(listToAdd, padding={'top': -4}))
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


class VehicleEliteBonusTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleEliteBonusTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE_ELITE_BONUS)
        self.bonusId = 0
        self._setContentMargin(top=20, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=0, afterSeparator=10)
        self._setWidth(365)

    def _packBlocks(self, *args, **kwargs):
        bonusId = self.context.buildItem(*args, **kwargs)
        content = super(VehicleEliteBonusTooltipData, self)._packBlocks(*args, **kwargs)
        title = ''
        body = ''
        icon = ''
        if bonusId == VEHPREVIEW_CONSTANTS.BATTLE_BONUS:
            title = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_BATTLE_HEADER
            body = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_BATTLE_BODY
            icon = RES_ICONS.MAPS_ICONS_VEHPREVIEW_BONUS_BATTLE
        elif bonusId == VEHPREVIEW_CONSTANTS.CREW_BONUS:
            title = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_CREW_HEADER
            body = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_CREW_BODY
            icon = RES_ICONS.MAPS_ICONS_VEHPREVIEW_BONUS_CREW
        elif bonusId == VEHPREVIEW_CONSTANTS.CREDIT_BONUS:
            title = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_CREDIT_HEADER
            body = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_CREDIT_BODY
            icon = RES_ICONS.MAPS_ICONS_VEHPREVIEW_BONUS_CREDIT
        elif bonusId == VEHPREVIEW_CONSTANTS.REPLACE_BONUS:
            title = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_REPLACE_HEADER
            body = TOOLTIPS.VEHICLEPREVIEW_ELITEBONUS_REPLACE_BODY
            icon = RES_ICONS.MAPS_ICONS_VEHPREVIEW_BONUS_REPLACE
        content.append(formatters.packTextBlockData(text_styles.highTitle(title)))
        content.append(formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        content.append(formatters.packTextBlockData(text_styles.main(body)))
        return content


class VehicleHistoricalReferenceTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleHistoricalReferenceTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE_HISTORICAL_REFERENCE)
        self.bonusId = 0
        self._setContentMargin(top=0, left=19, bottom=20, right=20)
        self._setMargins(afterBlock=0, afterSeparator=10)
        self._setWidth(365)

    def _packBlocks(self, *args, **kwargs):
        item = self.context.buildItem(*args, **kwargs)
        content = super(VehicleHistoricalReferenceTooltipData, self)._packBlocks(*args, **kwargs)
        blocks = list()
        blocks.append(formatters.packImageBlockData(img='../maps/icons/tooltip/flag_160x100/{}.png'.format(item.nationName), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding={'left': -19}))
        blocks.append(formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.VEHICLEPREVIEW_HISTORICALREFERENCE_TITLE), padding={'top': -72}))
        blocks.append(formatters.packTextBlockData(text_styles.main(item.fullDescription), padding={'top': 10}))
        content.append(formatters.packBuildUpBlockData(blocks))
        return content


class BattleTraining(BlocksTooltipData):

    def __init__(self, context):
        super(BattleTraining, self).__init__(context, None)
        self._setWidth(540)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(BattleTraining, self)._packBlocks(*args, **kwargs)
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.BATTLETYPES_BATTLETEACHING_HEADER), desc=text_styles.main(i18n.makeString(TOOLTIPS.BATTLETYPES_BATTLETEACHING_BODY, map1=i18n.makeString(ARENAS.C_10_HILLS_NAME), battles=BATTLES_TO_SELECT_RANDOM_MIN_LIMIT))))
        return items


class SquadBonusTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(SquadBonusTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.SQUAD_BONUS)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(SquadBonusTooltipContent())


class VehiclePointsTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(VehiclePointsTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_PASS_VEHICLE_POINTS)

    def getDisplayableData(self, intCD, *args, **kwargs):
        return DecoratedTooltipWindow(VehiclePointsTooltipView(intCD), useDecorator=False)


class BattlePassInProgressTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BattlePassInProgressTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_PASS_IN_PROGRESS)

    def getDisplayableData(self, *args, **kwargs):
        return BattlePassInProgressTooltipView()


class BattlePassCompletedTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BattlePassCompletedTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_PASS_COMPLETED)

    def getDisplayableData(self, *args, **kwargs):
        return BattlePassCompletedTooltipView()


class BattlePassChoseWinnerTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BattlePassChoseWinnerTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_PASS_CHOSE_WINNER)

    def getDisplayableData(self, *args, **kwargs):
        return BattlePassChoseWinnerTooltipView()


class BattlePassNotStartedTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(BattlePassNotStartedTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_PASS_NOT_STARTED)

    def getDisplayableData(self, *args, **kwargs):
        return BattlePassNotStartedTooltipView()


class TechTreeEventTooltipBase(BlocksTooltipData):
    _eventsListener = dependency.descriptor(ITechTreeEventsListener)

    def __init__(self, context):
        super(TechTreeEventTooltipBase, self).__init__(context, None)
        self._setWidth(365)
        return

    def _actionNameBlock(self, title, description, icon):
        return formatters.packImageTextBlockData(title=text_styles.neutral(title), desc=text_styles.standard(description), img=icon, imgPadding=formatters.packPadding(top=-1), padding=formatters.packPadding(bottom=10))

    def _actionExpireBlock(self, actionID):
        timeLeftStr = getTillTimeByResource(self._eventsListener.getTimeTillEnd(actionID), R.strings.tooltips.techTreePage.event.timeLeft)
        return formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.techTreePage.event.time(), time=text_styles.main(timeLeftStr))), padding=formatters.packPadding(top=10, left=23))


class TechTreeDiscountInfoTooltip(TechTreeEventTooltipBase):

    def _packBlocks(self, *args, **kwargs):
        items = super(TechTreeDiscountInfoTooltip, self)._packBlocks(*args, **kwargs)
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.HEADER_BUTTONS_TECHTREE_HEADER), desc=text_styles.main(TOOLTIPS.HEADER_BUTTONS_TECHTREE_BODY)))
        if not self._eventsListener.actions:
            return items
        actionGoups = defaultdict(list)
        for actionID in self._eventsListener.actions:
            actionGoups[self._eventsListener.getTimeTillEnd(actionID)].append(actionID)

        for idx, actionIDs in enumerate([ actionGoups[key] for key in sorted(actionGoups.keys()) ]):
            items.append(self.__packActionBlock(actionIDs, not idx))

        return items

    def __packActionBlock(self, actionIDs, packHeader=False):
        blocks = list()
        if packHeader:
            blocks.append(self._actionNameBlock(backport.text(R.strings.tooltips.techTreePage.event.name(), eventName=self._eventsListener.getUserName(actionIDs[0])), backport.text(R.strings.tooltips.header.buttons.techtree.extended.description()), backport.image(R.images.gui.maps.icons.library.discount())))
        else:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.header.buttons.techtree.extended.description())), padding=formatters.packPadding(bottom=10, left=23)))
        for actionID in actionIDs:
            nationIDs = self._eventsListener.getNations(actionID=actionID)
            separator = '   '
            for nation in GUI_NATIONS:
                if nations.INDICES[nation] in nationIDs:
                    icon = icons.makeImageTag(getNationsFilterAssetPath(nation), 26, 16, -4)
                    nationName = text_styles.main(backport.text(R.strings.nations.dyn(nation)()))
                    blocks.append(formatters.packTextBlockData(text_styles.concatStylesToSingleLine(icon, separator, nationName), padding=formatters.packPadding(left=43)))

        blocks.append(self._actionExpireBlock(actionIDs[0]))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class TechTreeNationDiscountTooltip(TechTreeEventTooltipBase):

    def _packBlocks(self, nation):
        items = super(TechTreeNationDiscountTooltip, self)._packBlocks()
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.techTreePage.nations.dyn(nation)()))))
        nationID = nations.INDICES[nation]
        closestAction = self._eventsListener.getActiveAction(nationID=nationID)
        if nationID not in self._eventsListener.getNations():
            return items
        blocks = list()
        blocks.append(self._actionNameBlock(backport.text(R.strings.tooltips.techTreePage.event.name(), eventName=self._eventsListener.getUserName(closestAction)), backport.text(R.strings.tooltips.techTreePage.event.description(), nation=backport.text(R.strings.nations.dyn(nation).genetiveCase())), backport.image(R.images.gui.maps.icons.library.discount())))
        blocks.append(self._actionExpireBlock(closestAction))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items

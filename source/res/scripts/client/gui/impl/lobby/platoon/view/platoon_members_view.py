# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_members_view.py
import logging
from enum import Enum
import functools
import BigWorld
import VOIP
from CurrentVehicle import g_currentVehicle
from UnitBase import UNDEFINED_ESTIMATED_TIME, UNIT_ROLE
from constants import PREBATTLE_TYPE, REQUEST_COOLDOWN, SQUAD_DIFFICULTY_EVENTS
from debug_utils import LOG_DEBUG_DEV
from frameworks.wulf import WindowFlags, ViewSettings, WindowStatus
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES import MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.Waiting import Waiting
from gui.impl import backport
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.platoon.difficulty_dropdown_item_model import DifficultyDropdownItemModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_label_element_model import SlotLabelElementModel, Types
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.lobby.halloween.event_helpers import notifyCursorOver3DScene
from gui.impl.lobby.platoon.platoon_helpers import formatSearchEstimatedTime, removeNationFromTechName
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from gui.impl.lobby.platoon.tooltip.platoon_event_tooltip import EventTooltip
from gui.impl.lobby.platoon.tooltip.platoon_wtr_tooltip import WTRTooltip
from gui.impl.lobby.platoon.view.slot_label_html_handler import SlotLabelHtmlParser
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.platoon.view.subview.platoon_tiers_filter_subview import SettingsPopover
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.impl.pub import ViewImpl
from gui.prb_control import prb_getters
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE, SELECTOR_BATTLE_TYPES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.shared.gui_items.badge import Badge
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import i18n, dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from skeletons.gui.afk_controller import IAFKController
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from messenger.m_constants import USER_TAG
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from messenger.ext import channel_num_gen
from adisp import process
_logger = logging.getLogger(__name__)
_strButtons = R.strings.platoon.buttons
DIFFICULTY_ICON = '%(level)'
DIFFICULTY_DISABLED = '%(lock)'
DIFFICULTY_INFO = '%(info)'

def getMemberContextMenuData(event, platoonSlotsData):
    userName = event.getArgument('userName')
    if userName:
        for it in platoonSlotsData:
            playerData = it['player']
            if playerData is not None and playerData['userName'] == userName:
                return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, playerData)

    _logger.warning('Username %s not found in platoon slots data', userName)
    return


def _floatToPercents(value):
    return int(value * 100)


class _BonusState(Enum):
    NO_BONUS = 0
    BONUS = 1
    UNIT_BONUS = 2
    PREMIUM_BONUS = 3


class _LayoutStyle(Enum):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class SquadMembersView(ViewImpl, CallbackDelayer):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __afkController = dependency.descriptor(IAFKController)
    _battleType = 'standard'

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.MembersWindow(), model=MembersWindowModel())
        self._currentBonusState = None
        super(SquadMembersView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def _onLoading(self, *args, **kwargs):
        self.__addListeners()
        self._addSubviews()
        with self.viewModel.transaction() as model:
            model.setCanMinimize(True)
        self._initWindowData()
        self._updateMembers()

    def _initialize(self, *args, **kwargs):
        self.__setPreBattleCarouselOpened(True)
        self.__setPreBattleCarouselFocus(True)

    def _finalize(self):
        self.__removeListeners()
        self.__setPreBattleCarouselOpened(False)
        self.__setPreBattleCarouselFocus(False)
        self.clearCallbacks()

    def _addSubviewToLayout(self, subview):
        self.setChildView(subview.layoutID, subview)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())
        self._addSubviewToLayout(TiersLimitSubview())

    def createPopOverContent(self, event):
        return SettingsPopover()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.platoon.EventTooltips():
            tooltipID = int(event.getArgument('id'))
            commander = next((slot.player for slot in self.viewModel.getSlots() if slot.player.getIsCommander()), None)
            header = ''
            level = commander.commonData.getSquadDifficultyLevel()
            if tooltipID == SQUAD_DIFFICULTY_EVENTS.COMMANDER:
                header = backport.text(R.strings.tooltips.event.squad.difficulty.dropdown.header())
                body = backport.text(R.strings.tooltips.event.squad.difficulty.dropdown.commander.body())
            elif tooltipID == SQUAD_DIFFICULTY_EVENTS.MEMBER:
                header = backport.text(R.strings.tooltips.event.squad.difficulty.dropdown.header())
                body = backport.text(R.strings.tooltips.event.squad.difficulty.dropdown.body())
            elif tooltipID == SQUAD_DIFFICULTY_EVENTS.LOCK:
                body = backport.text(R.strings.tooltips.event.squad.difficulty.lock(), icon=DIFFICULTY_DISABLED, level=DIFFICULTY_ICON)
                level = commander.commonData.getMaxDifficultyLevel()
            elif tooltipID == SQUAD_DIFFICULTY_EVENTS.INFO:
                body = backport.text(R.strings.tooltips.event.squad.difficulty.warning(), icon=DIFFICULTY_INFO)
            else:
                _logger.error('Cannot find appropriate tooltip for event: %s', str(tooltipID))
                return
            return EventTooltip(level=level, header=header, body=body)
        elif contentID == R.views.lobby.platoon.AlertTooltip():
            if self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH):
                return
            tooltip = R.strings.platoon.buttons.findPlayers.tooltip
            header = tooltip.header()
            if not self.__platoonCtrl.isSearchingForPlayersEnabled():
                body = tooltip.noAssembling.body()
            else:
                body = tooltip.noSuitableTank.body()
            return AlertTooltip(header, body)
        elif contentID == R.views.lobby.premacc.squad_bonus_tooltip_content.SquadBonusTooltipContent():
            return self._createHeaderInfoTooltip()
        else:
            if contentID == R.views.lobby.platoon.WTRTooltip():
                slotId = event.getArgument('slotId')
                slot = next((slot for slot in self.viewModel.getSlots() if slot.getSlotId() == slotId), None)
                if slot is not None:
                    commonData = slot.player.commonData
                    return WTRTooltip(commonData.getName(), commonData.getClanTag(), commonData.getBadgeID(), commonData.getRating(), commonData.getMaxDifficultyLevelMessage(), commonData.getIsEvent(), commonData.getMaxDifficultyLevel())
            return super(SquadMembersView, self).createToolTipContent(event=event, contentID=contentID)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getMemberContextMenuData(event, self.__platoonCtrl.getPlatoonSlotsData())
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.onStatusChanged += self.__onStatusChangedContextMenu
                window.load()
                return window
        return super(SquadMembersView, self).createContextMenu(event)

    def __onStatusChangedContextMenu(self, windowStatus):
        if windowStatus == WindowStatus.DESTROYED and self.__platoonCtrl.isInPlatoon():
            self._updateMembers()

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.btnInviteFriends.onClick += self._onInviteFriends
            model.btnSwitchReady.onClick += self._onSwitchReady
            model.btnFindPlayers.onClick += self._onFindPlayers
            model.header.btnMuteAll.onClick += self._onToggleMuteAll
            model.header.btnLeavePlatoon.onClick += self._onLeavePlatoon
            model.onClosed += self._onLeavePlatoon
            model.onMinimized += self.__onMinimized
            model.onFocusChange += self.__onFocusChange
        self.__platoonCtrl.onMembersUpdate += self._updateMembers
        g_messengerEvents.voip.onPlayerSpeaking += self.__onPlayerSpeaking
        g_messengerEvents.voip.onChannelEntered += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLeft += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelAvailable += self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLost += self.__updateVoiceChatToggleState
        g_currentVehicle.onChanged += self.__updateReadyButton
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__onUsersReceived
        usersEvents.onUserActionReceived += self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged += self._updateMembers
        g_eventBus.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateReadyButton, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__platoonCtrl.onAvailableTiersForSearchChanged += self.__onAvailableTiersForSearchChanged
        self.__platoonCtrl.onAutoSearchCooldownChanged += self._updateFindPlayersButton

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.btnInviteFriends.onClick -= self._onInviteFriends
            model.btnSwitchReady.onClick -= self._onSwitchReady
            model.btnFindPlayers.onClick -= self._onFindPlayers
            model.header.btnMuteAll.onClick -= self._onToggleMuteAll
            model.header.btnLeavePlatoon.onClick -= self._onLeavePlatoon
            model.onClosed -= self._onLeavePlatoon
            model.onMinimized -= self.__onMinimized
            model.onFocusChange -= self.__onFocusChange
        self.__platoonCtrl.onMembersUpdate -= self._updateMembers
        g_messengerEvents.voip.onPlayerSpeaking -= self.__onPlayerSpeaking
        g_messengerEvents.voip.onChannelEntered -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLeft -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelAvailable -= self.__updateVoiceChatToggleState
        g_messengerEvents.voip.onChannelLost -= self.__updateVoiceChatToggleState
        g_currentVehicle.onChanged -= self.__updateReadyButton
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__onUsersReceived
        usersEvents.onUserActionReceived -= self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged -= self._updateMembers
        g_eventBus.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateReadyButton, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__platoonCtrl.onAvailableTiersForSearchChanged -= self.__onAvailableTiersForSearchChanged
        self.__platoonCtrl.onAutoSearchCooldownChanged -= self._updateFindPlayersButton

    def __onServerSettingsChange(self, diff):
        if 'unit_assembler_config' in diff:
            self._updateButtons()

    def __onAvailableTiersForSearchChanged(self):
        self._updateButtons()

    def __getEstimatedTimeInQueue(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            estimatedTime = unitMgr.unit.getEstimatedTimeInQueue()
            if estimatedTime != UNDEFINED_ESTIMATED_TIME:
                return formatSearchEstimatedTime(estimatedTime)

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        slotModelArray = self.viewModel.getSlots()
        for it in slotModelArray:
            if it.player.getAccID() == str(accountDBID):
                return it.player.voice.setIsSpeaking(isSpeak)

    def _updateMembers(self):
        platoonCtrl = self.__platoonCtrl
        slots = platoonCtrl.getPlatoonSlotsData()
        searching = platoonCtrl.isInSearch()
        isWTREnabled = self.__lobbyContext.getServerSettings().isWTREnabled()
        accID = BigWorld.player().id
        estimatedTime = self.__getEstimatedTimeInQueue()
        playerIDs = []
        with self.viewModel.transaction() as model:
            slotModelArray = model.getSlots()
            slotModelArray.clear()
            slotCount = 0
            for it in slots:
                playerData = it.get('player', {})
                isEvent = it.get('isEvent')
                slot = SlotModel()
                slot.setIsEmpty(not bool(playerData))
                if playerData:
                    playerAccID = playerData.get('accID', None)
                    if playerAccID and playerAccID in playerIDs:
                        continue
                    elif playerAccID:
                        playerIDs.append(playerAccID)
                    slot.player.commonData.setName(playerData.get('userName', ''))
                    slot.player.commonData.setColor('#DE1E7E')
                    slot.player.setIsReady(playerData.get('readyState', False))
                    slot.player.setIsBanned(playerData.get('afkIsBanned', False))
                    slot.player.setAccID(str(playerData.get('dbID', None)))
                    slot.player.setIsCommander(playerData.get('isCommander', False))
                    slot.player.setIsCurrentUser(accID == playerAccID)
                    slot.player.commonData.setClanTag(playerData.get('clanAbbrev', ''))
                    slot.player.setIsPrem(it.get('hasPremiumAccount', False))
                    slot.player.commonData.setRating(playerData.get('accountWTR', '') if isWTREnabled else '')
                    badgeIconPath = playerData.get('badgeVisualVO', {}).get('icon', '')
                    slot.player.commonData.setBadgeID(Badge.getBadgeIDFromIconPath(badgeIconPath))
                    playerStatus = it.get('playerStatus', PLAYER_GUI_STATUS.NORMAL)
                    slot.setIsInBattle(playerStatus == PLAYER_GUI_STATUS.BATTLE)
                    if playerStatus == PLAYER_GUI_STATUS.BATTLE:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.inBattle()))
                    elif playerStatus == PLAYER_GUI_STATUS.BANNED:
                        slot.setInfoText(backport.text(R.strings.event.squad.afk.warning(), pardonDate=formatTimeAndDate(playerData.get('afkExpireTime', 0))))
                    elif playerStatus != PLAYER_GUI_STATUS.READY:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.notReady()))
                    isAdditionalMsgVisible = it.get('isVisibleAdtMsg', False)
                    if isAdditionalMsgVisible and not isEvent:
                        additionalMsg = it.get('additionalMsg', '')
                        slot.setInfoText(additionalMsg)
                    isOffline = playerData.get('isOffline', False)
                    if isOffline:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.connectionLost()))
                    colors = playerData.get('colors', [])
                    if len(colors) > 1:
                        slot.player.commonData.setColor('#' + '{0:06X}'.format(colors[1 if isOffline else 0]))
                    tags = playerData.get('tags', [])
                    slot.player.voice.setIsMutedByUser(USER_TAG.MUTED in tags)
                    slot.player.setIsIgnored(USER_TAG.IGNORED in tags)
                    slot.player.commonData.setIsEvent(isEvent)
                    squadDifficultyLevel = it.get('squadDifficultyLevel')
                    if squadDifficultyLevel:
                        slot.player.commonData.setSquadDifficultyLevel(squadDifficultyLevel)
                    maxDifficultyLevel = it.get('maxDifficultyLevel')
                    if maxDifficultyLevel is not None:
                        maxDifficultyMsg = backport.text(R.strings.event.event.difficulty.squad_player_max_difficulty_level())
                        slot.player.commonData.setMaxDifficultyLevelMessage(maxDifficultyMsg)
                        slot.player.commonData.setMaxDifficultyLevel(maxDifficultyLevel)
                    vehicle = it.get('selectedVehicle', {})
                    if vehicle:
                        vehicleItem = self.__itemsCache.items.getItemByCD(vehicle.get('intCD', 0))
                        slot.player.vehicle.setIsPremium(vehicleItem.isPremium or vehicleItem.isElite)
                        slot.player.vehicle.setName(vehicleItem.shortUserName)
                        slot.player.vehicle.setTechName(replaceHyphenToUnderscore(removeNationFromTechName(vehicleItem.name)))
                        slot.player.vehicle.setTier(vehicleItem.level)
                        slot.player.vehicle.setType(vehicleItem.type)
                        slot.player.vehicle.setNation(vehicleItem.nationName)
                else:
                    slot.setIsSearching(searching)
                    slot.setInfoText(backport.text(R.strings.platoon.members.card.empty()))
                    slot.setEstimatedTime(estimatedTime)
                    slotLabelHtml = it.get('slotLabel', '')
                    if slotLabelHtml:
                        self.__convertSlotLabelData(slot.getSlotLabelElements(), slotLabelHtml)
                slot.setSlotId(slotCount)
                slotCount += 1
                slotModelArray.addViewModel(slot)

            slotModelArray.invalidate()
            self._updateButtons()
            self._updateHeader()
        return

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.randomBattle()))))
        return title

    def _getBackgroundImage(self):
        layoutStyle = self.__getLayoutStyle()
        fileName = '{battleType}_{layout}_list'.format(battleType=self._battleType, layout=layoutStyle.value)
        return backport.image(R.images.gui.maps.icons.platoon.members_window.backgrounds.dyn(fileName)())

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.standard.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.standard.body())
        return (tooltipHeader, tooltipBody)

    def _getBonusState(self):
        if self.__isPremiumBonusEnabled():
            playerInfo = self.__platoonCtrl.getPlayerInfo()
            if playerInfo and playerInfo.hasPremium:
                return _BonusState.PREMIUM_BONUS
            if self.__platoonCtrl.isUnitWithPremium():
                return _BonusState.UNIT_BONUS
            return _BonusState.BONUS
        return _BonusState.NO_BONUS

    def _initWindowData(self):
        with self.viewModel.transaction() as model:
            model.setCanMinimize(True)
            title = self._getTitle()
            model.setRawTitle(title)
            header, body = self._getWindowInfoTooltipHeaderAndBody()
            model.setWindowTooltipHeader(header)
            model.setWindowTooltipBody(body)
            backgroundImage = self._getBackgroundImage()
            model.header.setBackgroundImage(backgroundImage)
            layoutStyle = self.__getLayoutStyle()
            model.setIsHorizontal(layoutStyle == _LayoutStyle.HORIZONTAL)
        self._setBonusInformation(self._getBonusState())

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(True)
            model.setShowNoBonusPlaceholder(False)
            bonusesArray = model.getBonuses()
            bonusesArray.clear()
            xpBonusModel = self._createXpBonusModel()
            bonusesArray.addViewModel(xpBonusModel)
            creditBonusModel = self._createPremiumBonusModel(bonusState)
            if creditBonusModel:
                bonusesArray.addViewModel(creditBonusModel)
            bonusesArray.invalidate()
        self._currentBonusState = bonusState

    def _updateHeader(self):
        bonusState = self._getBonusState()
        if bonusState != self._currentBonusState:
            self._setBonusInformation(bonusState)

    def _createHeaderInfoTooltip(self):
        bonusState = self._getBonusState()
        return SquadBonusTooltipContent() if bonusState in (_BonusState.PREMIUM_BONUS, _BonusState.UNIT_BONUS) else self._createSimpleBonusTooltip()

    def _createSimpleBonusTooltip(self):
        bonusFactor = _floatToPercents(self.__eventsCache.getSquadXPFactor())
        bonusFactor = str(bonusFactor) + '%'
        header = backport.text(R.strings.tooltips.squadBonus.complex.header())
        body = backport.text(R.strings.tooltips.squadBonus.complex.body(), bonus=bonusFactor)
        return self._createSimpleTooltipContent(header=header, body=body)

    def _createSimpleTooltipContent(self, header, body):
        contentID = R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent()
        return SimpleTooltipContent(contentID=contentID, header=header, body=body)

    def _createXpBonusModel(self):
        xpBonusModel = BonusModel()
        xpBonusModel.setCurrency(BonusModel.XP)
        xpBonusModel.setAmount(_floatToPercents(self.__eventsCache.getSquadXPFactor()))
        return xpBonusModel

    def _createPremiumBonusModel(self, bonusState):
        if bonusState in (_BonusState.PREMIUM_BONUS, _BonusState.UNIT_BONUS):
            squadPremiumBonus = self.__lobbyContext.getServerSettings().squadPremiumBonus
            amount = squadPremiumBonus.ownCredits if bonusState == _BonusState.PREMIUM_BONUS else squadPremiumBonus.mateCredits
            amount = int(round(amount * 100))
            creditBonusModel = BonusModel()
            creditBonusModel.setCurrency(BonusModel.CREDITS)
            creditBonusModel.setAmount(amount)
            return creditBonusModel
        else:
            return None

    def _updateButtons(self):
        platoonCtrl = self.__platoonCtrl
        isInQueue = platoonCtrl.isInQueue()
        playerInfo = platoonCtrl.getPlayerInfo()
        isCommander = False
        if playerInfo:
            isCommander = playerInfo.isCommander()
        canSendInvite = platoonCtrl.getPermissions().canSendInvite()
        isInSearch = platoonCtrl.isInSearch()
        self.__updateVoiceChatToggleState()
        with self.viewModel.transaction() as model:
            model.setIsCommander(isCommander)
            model.header.btnLeavePlatoon.setCaption(backport.text(_strButtons.leavePlatoon.caption()))
            model.header.btnLeavePlatoon.setDescription(backport.text(_strButtons.leavePlatoon.description()))
            model.header.btnLeavePlatoon.setIsEnabled(not isInQueue)
            model.setShouldShowInvitePlayersButton(True)
            model.btnInviteFriends.setCaption(backport.text(_strButtons.invite.caption()))
            model.btnInviteFriends.setDescription(backport.text(_strButtons.invite.description()))
            model.btnInviteFriends.setIsEnabled(platoonCtrl.hasFreeSlot() and isCommander and canSendInvite and not isInQueue and not isInSearch)
        self._updateFindPlayersButton()
        self.__updateReadyButton()

    def _updateFindPlayersButton(self, *args):
        platoonCtrl = self.__platoonCtrl
        isInQueue = platoonCtrl.isInQueue()
        playerInfo = platoonCtrl.getPlayerInfo()
        isCommander = False
        if playerInfo:
            isCommander = playerInfo.isCommander()
        if not isCommander:
            return
        canStartAutoSearch = platoonCtrl.getPermissions().canStartAutoSearch()
        isInSearch = platoonCtrl.isInSearch()
        isEnabled = isCommander and not isInQueue and canStartAutoSearch and platoonCtrl.hasFreeSlot()
        isCooldown = self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.AUTO_SEARCH)
        hasSearchSupport = self.__platoonCtrl.hasSearchSupport()
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(hasSearchSupport)
            if hasSearchSupport:
                model.btnFindPlayers.setIsEnabled(isEnabled and platoonCtrl.canStartSearch() and not isCooldown)
                model.btnFindPlayers.setHasTooltip(platoonCtrl.hasFreeSlot())
                if isCommander:
                    if isInSearch:
                        cancelButton = _strButtons.cancelSearch
                        model.btnFindPlayers.setCaption(backport.text(cancelButton.caption()))
                        model.btnFindPlayers.setDescription(backport.text(cancelButton.description()))
                        model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_cancel_search())
                        model.btnFindPlayers.setIsLight(False)
                    else:
                        findButton = _strButtons.findPlayers
                        model.btnFindPlayers.setCaption(backport.text(findButton.caption()))
                        model.btnFindPlayers.setDescription(backport.text(findButton.descriptionMembers()))
                        model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_find_players())
                        model.btnFindPlayers.setIsLight(True)

    def _onInviteFriends(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), ctx={'prbName': 'unit',
         'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def _onSwitchReady(self):
        result = yield self.__platoonCtrl.togglePlayerReadyAction()
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def __updateReadyButton(self, *args):
        if not self.__platoonCtrl.isInPlatoon():
            return
        isInQueue = self.__platoonCtrl.isInQueue()
        actionButtonStateVO = self.__getActionButtonStateVO()
        simpleState = actionButtonStateVO.getSimpleState()
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        with self.viewModel.transaction() as model:
            if not self.__platoonCtrl.isInCoolDown(REQUEST_TYPE.SET_PLAYER_STATE):
                model.btnSwitchReady.setIsEnabled(actionButtonStateVO['isEnabled'] and not isInQueue)
            if self.__platoonCtrl.getPlayerInfo().isReady:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.notReady.caption()))
            else:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.ready.caption()))
            description = i18n.makeString(actionButtonStateVO['toolTipData'] + '/body') if actionButtonStateVO['toolTipData'] else ''
            model.btnSwitchReady.setDescription(description)
            if self.__afkController.isBanned:
                model.btnSwitchReady.setTooltipHeader(backport.text(R.strings.tooltips.event.afk.ban.header()))
                model.btnSwitchReady.setDescription(backport.text(R.strings.tooltips.event.afk.ban.fbBody(), value=formatTimeAndDate(self.__afkController.banExpiryTime)))
            model.setFooterMessage(simpleState)
        model.setIsFooterMessageGrey(actionButtonStateVO['isEnabled'] or onlyReadinessText or isInQueue)

    def __getLayoutStyle(self):
        maxSlotCount = self.__platoonCtrl.getMaxSlotCount()
        return _LayoutStyle.HORIZONTAL if maxSlotCount < 4 else _LayoutStyle.VERTICAL

    def __isPremiumBonusEnabled(self):
        return self.__lobbyContext.getServerSettings().squadPremiumBonus.isEnabled

    def __updateVoiceChatToggleState(self, *_):
        voipMgr = VOIP.getVOIPManager()
        isMuteButtonVisible = voipMgr.isVoiceSupported() and voipMgr.isChannelAvailable()
        isVoiceChannelEnabled = voipMgr.isEnabled() and voipMgr.isCurrentChannelEnabled() and isMuteButtonVisible
        with self.viewModel.transaction() as model:
            model.header.btnMuteAll.setIsVisible(isMuteButtonVisible)
            model.header.btnMuteAll.setIsSelected(not isVoiceChannelEnabled)
            if isMuteButtonVisible:
                model.header.btnMuteAll.setIsSelected(not isVoiceChannelEnabled)
                if isVoiceChannelEnabled:
                    tooltipCaption = _strButtons.mute.caption()
                    tooltipBody = _strButtons.mute.description()
                else:
                    tooltipCaption = _strButtons.unMute.caption()
                    tooltipBody = _strButtons.unMute.description()
                model.header.btnMuteAll.setTooltipHeader(backport.text(tooltipCaption))
                model.header.btnMuteAll.setTooltipBody(backport.text(tooltipBody))

    def _onFindPlayers(self):
        platoonCtrl = self.__platoonCtrl
        if platoonCtrl.isInSearch():
            platoonCtrl.cancelSearch()
        else:
            platoonCtrl.startSearch()
            platoonCtrl.requestPlayerQueueInfo()

    def _onToggleMuteAll(self):
        voipMgr = VOIP.getVOIPManager()
        isChannelEnabled = not self.viewModel.header.btnMuteAll.getIsSelected()
        voipMgr.enableCurrentChannel(not isChannelEnabled)
        self.__updateVoiceChatToggleState()

    def _onLeavePlatoon(self):
        self.__platoonCtrl.leavePlatoon()

    def __onMinimized(self):
        self.__platoonCtrl.destroyUI(hideOnly=True)

    def __onFocusChange(self, *args, **kwargs):
        if args:
            self.__setPreBattleCarouselFocus(args[0]['isFocused'])

    def __setPreBattleCarouselFocus(self, isFocusIn):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.ON_WINDOW_CHANGE_FOCUS, self.__getClientID(), MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES.CHANNEL_CAROUSEL_ITEM_TYPE_PREBATTLE, isFocusIn), scope=EVENT_BUS_SCOPE.LOBBY)

    def __setPreBattleCarouselOpened(self, isWindowOpened):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.ON_WINDOW_CHANGE_OPEN_STATE, self.__getClientID(), MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES.CHANNEL_CAROUSEL_ITEM_TYPE_PREBATTLE, isWindowOpened), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getClientID(self):
        prbType = self.__platoonCtrl.getPrbEntityType()
        return channel_num_gen.getClientID4Prebattle(prbType)

    def __getActionButtonStateVO(self):
        return SquadActionButtonStateVO(self.__platoonCtrl.getPrbEntity())

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)
            self.delayCallback(event.coolDown, self.__updateReadyButton)

    def __onUserActionReceived(self, _, user, shadowMode):
        if self.__platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return

    def __onUsersReceived(self, _):
        if self.__platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return

    @staticmethod
    def __convertSlotLabelData(slotLabelArray, slotLabelHtml):
        slotLabelArray.clear()
        parser = SlotLabelHtmlParser()
        parser.feed(slotLabelHtml)
        slotLabelElements = parser.getElements()
        for element in slotLabelElements:
            model = SlotLabelElementModel()
            model.setType(element.get('type', Types.TEXT))
            model.setContent(element.get('text', ''))
            model.setStyleJson(element.get('style', ''))
            slotLabelArray.addViewModel(model)


class EventMembersView(SquadMembersView):
    _battleType = 'event'
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __gameEventCtrl = dependency.descriptor(IGameEventController)
    _R_TOOLTIPS_TEXT = R.strings.tooltips.event.squad

    def __init__(self):
        super(EventMembersView, self).__init__()
        self._playersWithMaxDifficultyLevel = {}
        self.viewModel.setIsEvent(True)

    def _finalize(self):
        self.__removeListeners()
        self.__gameEventCtrl.setSquadDifficultyLevel(None)
        super(EventMembersView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        entity = self.__platoonCtrl.getPrbEntity()
        level = entity.gameEventController.getSquadDifficultyLevel()
        self._selectDifficulty(level, isCommander=entity.isCommander())
        super(EventMembersView, self)._onLoading(*args, **kwargs)
        self._addListeners()
        self._updateButtons()
        self._fillModel()

    @staticmethod
    def _showWaiting(show):
        if show:
            Waiting.show('sinhronize')
        else:
            Waiting.hide('sinhronize')

    def _updateMembers(self):
        super(EventMembersView, self)._updateMembers()
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            entity = self.__platoonCtrl.getPrbEntity()
            model.setIsCommander(entity.isCommander())
            model.setIsEvent(True)
            self._checkCommandersDifficultyLevel()
            self._updatePlayersWithMaxDifficultyLevel(model)
            self._fillDifficultyDropdown(model)

    def _selectDifficulty(self, difficultyLevel, force=False, isCommander=False):
        entity = self.__platoonCtrl.getPrbEntity()
        if (self.viewModel.getIsCommander() or isCommander) and entity.gameEventController.hasDifficultyLevelToken(difficultyLevel):
            self._showWaiting(True)
            callback = functools.partial(self._showWaiting, False)
            BigWorld.callback(REQUEST_COOLDOWN.CMD_CHANGE_SELECTED_DIFFICULTY_LEVEL, callback)
            BigWorld.player().changeSelectedDifficultyLevel(int(difficultyLevel), force)
            self.__setSelected(self.viewModel.eventDifficulty.getSelected(), difficultyLevel)

    def _checkCommandersDifficultyLevel(self):
        entity = self.__platoonCtrl.getPrbEntity()
        if entity.isCommander():
            return
        _, unit = entity.getUnit()
        for player in unit.getPlayers().itervalues():
            if player['role'] & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR:
                level = player.get('extraData', {}).get('eventEnqueueData', {}).get('difficultyLevel')
                entity.gameEventController.setSquadDifficultyLevel(level)
                return
            LOG_DEBUG_DEV('EventSquadView._setCommandersDifficultyLevel. Could not find commander.')

    def _updatePlayersWithMaxDifficultyLevel(self, model):
        if not model.getIsCommander():
            return
        entity = self.__platoonCtrl.getPrbEntity()
        unitMgrID = entity.getID()
        playersDifficultyLevels = {}
        for slot in entity.getSlotsIterator(*entity.getUnit(unitMgrID=unitMgrID)):
            if slot.player:
                maxDifficulyLevel = slot.player.extraData.get('eventEnqueueData').get('maxDifficultyLevel')
                playersDifficultyLevels[slot.player.slotIdx] = maxDifficulyLevel

        self._playersWithMaxDifficultyLevel = playersDifficultyLevels
        LOG_DEBUG_DEV('EventSquadView._updatePlayersWithMaxDifficultyLevel._playersWithMaxDifficultyLevelwas updated with players: ', playersDifficultyLevels)

    def _showInfoWarningByLevel(self, dropDownLevel):
        for maxLevel in self._playersWithMaxDifficultyLevel.itervalues():
            if maxLevel < dropDownLevel:
                return True

        return False

    def _fillDifficultyItem(self, level):
        entity = self.__platoonCtrl.getPrbEntity()
        disabled = not entity.gameEventController.hasDifficultyLevelToken(level)
        levelModel = DifficultyDropdownItemModel()
        levelModel.setIsDisabled(disabled)
        levelModel.setShowInfoIcon(self._showInfoWarningByLevel(level))
        levelModel.setLabel(backport.text(R.strings.event.event.squad_difficulty(), level=''))
        levelModel.setId(level)
        return levelModel

    def _fillDifficultyDropdown(self, model):
        entity = self.__platoonCtrl.getPrbEntity()
        levels = entity.gameEventController.getDifficultyLevels()
        eventDifficulty = model.eventDifficulty
        difficultyDropdownItems = eventDifficulty.getItems()
        difficultyDropdownItems.clear()
        for level in levels:
            difficultyItem = self._fillDifficultyItem(level)
            difficultyDropdownItems.addViewModel(difficultyItem)

        difficultyDropdownItems.invalidate()
        squadLevel = entity.gameEventController.getSquadDifficultyLevel()
        model.setSelectedDifficulty(str(squadLevel))
        self.__setSelected(eventDifficulty.getSelected(), int(squadLevel))

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _getTitle(self):
        title = ' '.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.event()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.event.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.event.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(True)
            model.setShowNoBonusPlaceholder(True)
            infoText = R.strings.messenger.dialogs.squadChannel.headerMsg.eventFormationRestriction()
            model.noBonusPlaceholder.setText(infoText)
            model.noBonusPlaceholder.setIcon(R.images.gui.maps.icons.battleTypes.c_64x64.event())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return _BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)

    def _addListeners(self):
        model = self.viewModel
        model.eventDifficulty.onChange += self.__onEventDifficultyChanged
        model.onOverViewChange += self.__onOverViewChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitPlayerInfoChanged += self.__onUnitPlayerInfoChanged
            unitMgr.unit.onUnitPlayerRoleChanged += self.__onUnitPlayerRoleChanged

    def __removeListeners(self):
        model = self.viewModel
        model.eventDifficulty.onChange -= self.__onEventDifficultyChanged
        model.onOverViewChange -= self.__onOverViewChange
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitPlayerInfoChanged -= self.__onUnitPlayerInfoChanged
            unitMgr.unit.onUnitPlayerRoleChanged -= self.__onUnitPlayerRoleChanged

    def __onEventDifficultyChanged(self, args=None):
        level = args.get('selectedIds')
        if level:
            self._selectDifficulty(int(level))

    def __setSelected(self, model, value):
        model.clear()
        model.addNumber(value)
        model.invalidate()

    def __onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        playerInfo = self.__platoonCtrl.getPlayerInfo()
        if not playerInfo.isCurrentPlayer():
            return
        diff = prevRoleFlags ^ nextRoleFlags
        if diff & UNIT_ROLE.CREATOR > 0:
            entity = self.__platoonCtrl.getPrbEntity()
            currentSquadDifficultyLevel = entity.gameEventController.getSquadDifficultyLevel()
            maxDifficultyLevel = playerInfo.extraData.get('eventEnqueueData', {}).get('maxDifficultyLevel')
            difficultyLevelToSet = min(maxDifficultyLevel, currentSquadDifficultyLevel)
            self._selectDifficulty(int(difficultyLevelToSet), True, True)

    def __onUnitPlayerInfoChanged(self, accountDBID, playerData):
        playerInfo = self.__platoonCtrl.getPlayerInfo()
        entity = self.__platoonCtrl.getPrbEntity()
        if playerInfo.isCurrentPlayer():
            level = playerData.get('extraData', {}).get('eventEnqueueData', {}).get('difficultyLevel')
            entity.gameEventController.setSquadDifficultyLevel(level)
        self.__updateSelectedDifficultyLevel()
        self._checkCommandersDifficultyLevel()

    def __onUnitPlayerStateChanged(self, pInfo):
        playerInfo = self.__platoonCtrl.getPlayerInfo()
        if playerInfo.isCurrentPlayer() and not playerInfo.isReady and not playerInfo.isCommander():
            entity = self.__platoonCtrl.getPrbEntity()
            maxDifficultyLevel = playerInfo.extraData.get('eventEnqueueData', {}).get('maxDifficultyLevel')
            if maxDifficultyLevel < entity.gameEventController.getSquadDifficultyLevel():
                entity.gameEventController.setSelectedDifficultyLevel(maxDifficultyLevel)

    def __updateSelectedDifficultyLevel(self):
        with self.viewModel.transaction() as model:
            if model.getIsCommander():
                entity = self.__platoonCtrl.getPrbEntity()
                difficultyLevel = entity.gameEventController.getSelectedDifficultyLevel()
                entity.gameEventController.setSquadDifficultyLevel(difficultyLevel)
            self._fillDifficultyDropdown(model)

    def __onOverViewChange(self, args=None):
        if args is None:
            _logger.error("Can't notified cursor over changed. args=None. Please fix JS")
            return
        else:
            notifyCursorOver3DScene(args.get('isOver3dScene', False))
            return


class EpicMembersView(SquadMembersView):
    _battleType = 'epic'

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.epic()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        header = backport.text(R.strings.platoon.members.header.tooltip.epic.header())
        body = backport.text(R.strings.platoon.members.header.tooltip.epic.body())
        return (header, body)

    def _setBonusInformation(self, bonusState):
        hasBonuses = bonusState != _BonusState.NO_BONUS
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(hasBonuses)
            model.setShowNoBonusPlaceholder(not hasBonuses)
            if hasBonuses:
                bonusesArray = model.getBonuses()
                bonusesArray.clear()
                xpBonusModel = self._createXpBonusModel()
                bonusesArray.addViewModel(xpBonusModel)
                creditBonusModel = self._createPremiumBonusModel(bonusState)
                if creditBonusModel:
                    bonusesArray.addViewModel(creditBonusModel)
                bonusesArray.invalidate()
            else:
                infoText = R.strings.messenger.dialogs.squadChannel.headerMsg.epicBattleFormationRestriction()
                model.noBonusPlaceholder.setText(infoText)
                model.noBonusPlaceholder.setIcon(R.images.gui.maps.icons.battleTypes.c_64x64.epicbattle())
        self._currentBonusState = bonusState


class BattleRoyalMembersView(SquadMembersView):
    _battleType = 'royal'

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.battleRoyale()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.battleRoyale.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.battleRoyale.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(False)
            model.setShowNoBonusPlaceholder(False)
        self._currentBonusState = bonusState

    def _getBonusState(self):
        return _BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        return None


class MapboxMembersView(SquadMembersView):
    _battleType = SELECTOR_BATTLE_TYPES.MAPBOX

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.mapbox()))))
        return title

    def _updateFindPlayersButton(self, *args):
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(value=False)


class MembersWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, initialPosition=None):
        prbType = self.__platoonCtrl.getPrbEntityType()
        content = None
        if prbType == PREBATTLE_TYPE.SQUAD:
            content = SquadMembersView()
        elif prbType == PREBATTLE_TYPE.EVENT:
            content = EventMembersView()
        elif prbType == PREBATTLE_TYPE.EPIC:
            content = EpicMembersView()
        elif prbType == PREBATTLE_TYPE.BATTLE_ROYALE:
            content = BattleRoyalMembersView()
        elif prbType == PREBATTLE_TYPE.MAPBOX:
            content = MapboxMembersView()
        if content is None:
            _logger.debug('PrbType is unknown %d', prbType)
        super(MembersWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=content)
        if initialPosition:
            self.move(initialPosition.x, initialPosition.y)
        return

    def show(self):
        super(MembersWindow, self).show()
        self.bringToFront()

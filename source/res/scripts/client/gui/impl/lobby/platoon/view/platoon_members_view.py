# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_members_view.py
import logging
from enum import Enum
import BigWorld
import VOIP
from CurrentVehicle import g_currentVehicle
from UnitBase import UNDEFINED_ESTIMATED_TIME
from constants import PREBATTLE_TYPE
from frameworks.wulf import WindowFlags, ViewSettings, WindowStatus
from frameworks.wulf.gui_constants import ViewStatus
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES import MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.lobby.platoon.platoon_helpers import formatSearchEstimatedTime, Position, removeNationFromTechName, getVehicleDescriptorByIntCD
from gui.impl.lobby.platoon.tooltip.platoon_alert_tooltip import AlertTooltip
from gui.impl.lobby.platoon.tooltip.platoon_wtr_tooltip import WTRTooltip
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.platoon.view.subview.platoon_tiers_filter_subview import SettingsPopover
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.impl.pub import ViewImpl
from gui.prb_control import prb_getters
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, checkForTags
from gui.shared.gui_items.badge import Badge
from helpers import i18n, dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from nations import NAMES
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from messenger.m_constants import USER_TAG
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from messenger.ext import channel_num_gen
from adisp import process
_logger = logging.getLogger(__name__)
_strButtons = R.strings.platoon.buttons

def getMemberContextMenuData(event, platoonSlotsData):
    userName = event.getArgument('userName')
    if userName:
        for it in platoonSlotsData:
            playerData = it['player']
            if playerData is not None and playerData['userName'] == userName:
                contextMenuArgs = {'dbID': playerData['dbID'],
                 'userName': userName}
                return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, contextMenuArgs)

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
    _battleType = 'standard'
    DELAY_FOR_READY_TOGGLE = 5

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
        if contentID == R.views.lobby.platoon.AlertTooltip():
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
                    return WTRTooltip(commonData.getName(), commonData.getClanTag(), commonData.getBadgeID(), commonData.getRating())
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
        if windowStatus == WindowStatus.DESTROYED:
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
        g_currentVehicle.onChanged += self.__updateReadyButtonText
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__onUsersReceived
        usersEvents.onUserActionReceived += self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged += self._updateMembers
        g_eventBus.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateReadyButtonText, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__onVehicleStateChanged

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
        g_currentVehicle.onChanged -= self.__updateReadyButtonText
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__onUsersReceived
        usersEvents.onUserActionReceived -= self.__onUserActionReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged -= self._updateMembers
        g_eventBus.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updateReadyButtonText, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted -= self.__onVehicleStateChanged

    def __onServerSettingsChange(self, diff):
        if 'unit_assembler_config' in diff:
            self._updateButtons()

    def __onVehicleStateChanged(self, *args, **kwargs):
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
        slots = self.__platoonCtrl.getPlatoonSlotsData()
        searching = self.__platoonCtrl.isInSearch()
        isWTREnabled = self.__lobbyContext.getServerSettings().isWTREnabled()
        accID = BigWorld.player().id
        estimatedTime = self.__getEstimatedTimeInQueue()
        with self.viewModel.transaction() as model:
            slotModelArray = model.getSlots()
            slotModelArray.clear()
            slotCount = 0
            for it in slots:
                playerData = it.get('player', {})
                slot = SlotModel()
                slot.setIsEmpty(not bool(playerData))
                slot.setSlotLabelHtml(it.get('slotLabel', ''))
                if playerData:
                    slot.player.commonData.setName(playerData.get('userName', ''))
                    slot.player.commonData.setColor('#DE1E7E')
                    slot.player.setIsReady(playerData.get('readyState', False))
                    slot.player.setAccID(str(playerData.get('dbID', None)))
                    slot.player.setIsCommander(playerData.get('isCommander', False))
                    slot.player.setIsCurrentUser(accID == playerData.get('accID', None))
                    slot.player.commonData.setClanTag(playerData.get('clanAbbrev', ''))
                    slot.player.setIsPrem(it.get('hasPremiumAccount', False))
                    slot.player.commonData.setRating(playerData.get('accountWTR', '') if isWTREnabled else '')
                    badgeIconPath = playerData.get('badgeVisualVO', {}).get('icon', '')
                    slot.player.commonData.setBadgeID(Badge.getBadgeIDFromIconPath(badgeIconPath))
                    playerStatus = it.get('playerStatus', PLAYER_GUI_STATUS.NORMAL)
                    slot.setIsInBattle(playerStatus == PLAYER_GUI_STATUS.BATTLE)
                    if playerStatus == PLAYER_GUI_STATUS.BATTLE:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.inBattle()))
                    elif playerStatus != PLAYER_GUI_STATUS.READY:
                        slot.setInfoText(backport.text(R.strings.platoon.members.card.notReady()))
                    isAdditionalMsgVisible = it.get('isVisibleAdtMsg', False)
                    if isAdditionalMsgVisible:
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
                    vehicle = it.get('selectedVehicle', {})
                    if vehicle:
                        vehicleDesc = getVehicleDescriptorByIntCD(vehicle.get('intCD', 0))
                        slot.player.vehicle.setIsPremium(checkForTags(vehicleDesc.type.tags, VEHICLE_TAGS.PREMIUM))
                        slot.player.vehicle.setName(vehicle.get('shortUserName', ''))
                        slot.player.vehicle.setTechName(removeNationFromTechName(vehicle.get('name', '')))
                        slot.player.vehicle.setTier(vehicle.get('level', 0))
                        slot.player.vehicle.setType(vehicle.get('type', ''))
                        slot.player.vehicle.setNation(NAMES[vehicle.get('nationID', 0)])
                else:
                    slot.setIsSearching(searching)
                    slot.setInfoText(backport.text(R.strings.platoon.members.card.empty()))
                    slot.setEstimatedTime(estimatedTime)
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
        isInQueue = self.__platoonCtrl.isInQueue()
        playerInfo = self.__platoonCtrl.getPlayerInfo()
        isCommander = False
        if playerInfo:
            isCommander = playerInfo.isCommander()
        canSendInvite = self.__platoonCtrl.getPermissions().canSendInvite()
        canStartAutoSearch = self.__platoonCtrl.getPermissions().canStartAutoSearch()
        isInSearch = self.__platoonCtrl.isInSearch()
        self.__updateVoiceChatToggleState()
        with self.viewModel.transaction() as model:
            model.setIsCommander(isCommander)
            model.header.btnLeavePlatoon.setCaption(backport.text(_strButtons.leavePlatoon.caption()))
            model.header.btnLeavePlatoon.setDescription(backport.text(_strButtons.leavePlatoon.description()))
            model.header.btnLeavePlatoon.setIsEnabled(not isInQueue)
            model.btnInviteFriends.setCaption(backport.text(_strButtons.invite.caption()))
            model.btnInviteFriends.setDescription(backport.text(_strButtons.invite.description()))
            model.btnInviteFriends.setIsEnabled(self.__platoonCtrl.hasFreeSlot() and isCommander and canSendInvite and not isInQueue and not isInSearch)
            isEnabled = isCommander and not isInQueue and canStartAutoSearch and self.__platoonCtrl.hasFreeSlot()
            model.btnFindPlayers.setIsEnabled(isEnabled and self.__platoonCtrl.canStartSearch())
            if isCommander:
                if isInSearch:
                    model.btnFindPlayers.setCaption(backport.text(_strButtons.cancelSearch.caption()))
                    model.btnFindPlayers.setDescription(backport.text(_strButtons.cancelSearch.description()))
                    model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_cancel_search())
                else:
                    model.btnFindPlayers.setCaption(backport.text(_strButtons.findPlayers.caption()))
                    model.btnFindPlayers.setDescription(backport.text(_strButtons.findPlayers.descriptionMembers()))
                    model.btnFindPlayers.setSoundClickName(R.sounds.gui_platoon_2_find_players())
        self.__updateReadyButtonText()

    def _onInviteFriends(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY), ctx={'prbName': 'unit',
         'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def _onSwitchReady(self):
        result = yield self.__platoonCtrl.togglePlayerReadyAction()
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def __updateReadyButtonText(self, *args):
        if not self.__platoonCtrl.isInPlatoon():
            return
        isInQueue = self.__platoonCtrl.isInQueue()
        actionButtonStateVO = self.__getActionButtonStateVO()
        simpleState = actionButtonStateVO.getSimpleState()
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        with self.viewModel.transaction() as model:
            if self.hasDelayedCallback(self.__enableReadyButtonCallback) is False:
                model.btnSwitchReady.setIsEnabled(actionButtonStateVO['isEnabled'] and not isInQueue)
            if self.__platoonCtrl.getPlayerInfo().isReady:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.notReady.caption()))
            else:
                model.btnSwitchReady.setCaption(backport.text(_strButtons.ready.caption()))
            model.btnSwitchReady.setDescription(i18n.makeString(actionButtonStateVO['toolTipData'] + '/body'))
            model.setFooterMessage(simpleState)
        model.setIsFooterMessageGrey(actionButtonStateVO['isEnabled'] or onlyReadinessText)

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

    def __enableReadyButtonCallback(self):
        with self.viewModel.transaction() as model:
            if self.__platoonCtrl.isInQueue() is False:
                model.btnSwitchReady.setIsEnabled(True)
        self.__updateReadyButtonText()
        return

    def _onFindPlayers(self):
        if self.__platoonCtrl.isInSearch():
            self.__platoonCtrl.cancelSearch()
        else:
            self.__platoonCtrl.startSearch()
            TiersLimitSubview.resetState()
            self.__platoonCtrl.requestPlayerQueueInfo()

    def _onToggleMuteAll(self):
        voipMgr = VOIP.getVOIPManager()
        isChannelEnabled = not self.viewModel.header.btnMuteAll.getIsSelected()
        voipMgr.enableCurrentChannel(not isChannelEnabled)
        self.__updateVoiceChatToggleState()

    def _onLeavePlatoon(self):
        self.__platoonCtrl.leavePlatoon()
        TiersLimitSubview.resetState()

    def __onMinimized(self):
        self.__platoonCtrl.hide()

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
            self.delayCallback(self.DELAY_FOR_READY_TOGGLE, self.__enableReadyButtonCallback)

    def __onUserActionReceived(self, _, user, shadowMode):
        if self.__platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return

    def __onUsersReceived(self, _):
        if self.__platoonCtrl.getPrbEntity() is not None:
            self._updateMembers()
        return


class EventMembersView(SquadMembersView):
    _battleType = 'event'

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.event()))))
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
        return self._createSimpleTooltipContent(header=tooltip.header(), body=tooltip.body())


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
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setText(R.strings.messenger.dialogs.squadChannel.headerMsg.battleRoyaleHint())
        self._currentBonusState = bonusState

    def _getBonusState(self):
        return _BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        return None


class MembersWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    previousPosition = None

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
        if content is None:
            _logger.debug('PrbType is unknown %d', prbType)
        super(MembersWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=content)
        if initialPosition:
            self.move(initialPosition.x, initialPosition.y)
            return
        else:
            if MembersWindow.previousPosition:
                self.move(MembersWindow.previousPosition.x, MembersWindow.previousPosition.y)
            return

    def show(self):
        super(MembersWindow, self).show()
        self.bringToFront()

    def _finalize(self):
        if self.content.viewStatus > ViewStatus.LOADING:
            MembersWindow.previousPosition = Position(self.position[0], self.position[1])

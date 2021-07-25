# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/profile_view.py
from collections import namedtuple
from copy import deepcopy
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from async import async, await
from crew2 import settings_globals
from crew2.crew2_consts import GENDER_TO_OPPOSITE
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.dialogs.dialogs import showDetachmentChangeCommanderDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_constants import CommanderCardConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_model import CommanderCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.profile_view_model import ProfileViewModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers import getNationSettings, getCommanderTypeSettings
from gui.impl.lobby.detachment.popovers.filters.commander_filters import defaultCommanderPopoverFilter, defaultCommanderToggleFilter, toggleCriteria, popoverCriteria, PortraitTypes, ORDER
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewStatus
from gui.impl.lobby.detachment.tooltips.commander_look_tooltip import CommanderLookTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.detachment import DetachmentChangePassport, CrewSkinEquip
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE
from gui.shared.gui_items.crew_skin import localizedFullName
from uilogging.detachment.loggers import DetachmentToggleLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import ACTION, GROUP
_CardInfo = namedtuple('_CardInfo', 'id type portraitType gender nation amount iconName isUsed newAmount')
_COMMANDER_LOOK_TOOLTIP_ID = 'commander_look_tooltip'
_PORTRAIT_TYPE_TO_VM_CONST = {PortraitTypes.DOCUMENT: CommanderCardConstants.PORTRAIT_TYPE_DOCUMENT,
 PortraitTypes.SKIN: CommanderCardConstants.PORTRAIT_TYPE_SKIN}

class ProfileView(NavigationViewImpl, FiltersMixin):
    __slots__ = ('_detInvID', '_detachment', '_cards', '__ctx')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    detachmentCache = dependency.descriptor(IDetachmentCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _defaultPopoverSetter = staticmethod(defaultCommanderPopoverFilter)
    _defaultToggleSetter = staticmethod(defaultCommanderToggleFilter)
    _popoverFilters = defaultCommanderPopoverFilter()
    _toggleFilters = defaultCommanderToggleFilter()
    uiLogger = DetachmentToggleLogger(GROUP.COMMANDER_PROFILE)

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProfileViewModel()
        super(ProfileView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self._detInvID = ctx['detInvID']
        self._detachment = self.detachmentCache.getDetachment(self._detInvID)
        self._cards = self.__getCards()
        self.__ctx = {'currentCount': 0,
         'totalCount': 0}
        super(ProfileView, self)._resetData()
        ProfileView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    def _initialize(self):
        super(ProfileView, self)._initialize()
        self.uiLogger.startAction(ACTION.OPEN)

    def _finalize(self):
        self._detInvID = None
        self._detachment = None
        self._cards = None
        self.uiLogger.stopAction(ACTION.OPEN)
        super(ProfileView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(ProfileView, self).getViewModel()

    def createPopOverContent(self, event):
        ToggleFilterPopoverViewStatus.uiLogger.setGroup(self.uiLogger.group)
        return ToggleFilterPopoverViewStatus(R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.common(), FilterStatusModel.DIVIDER, (getCommanderTypeSettings(), getNationSettings(R.strings.tooltips.filterToggle.nation.skins.body())), self._changePopoverFilterCallback, self._activatePopoverViewCallback, ProfileView._popoverFilters, self.__ctx, customResetFunc=self._resetPopoverFilters)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == _COMMANDER_LOOK_TOOLTIP_ID:
                id_ = event.getArgument('id')
                cardItem = self._cards[int(id_)]
                if cardItem.portraitType == PortraitTypes.SKIN:
                    CommanderLookTooltip.uiLogger.setGroup(self.uiLogger.group)
                    return CommanderLookTooltip(cardItem.id)
        return None

    def _initModel(self, vm):
        super(ProfileView, self)._initModel(vm)
        self._initFilters(vm, ORDER, FilterContext.PROFILE)
        self.__fillModel(vm)

    def _addListeners(self):
        super(ProfileView, self)._addListeners()
        model = self.viewModel
        model.onCommanderClick += self.__onCommanderClick
        model.onHoverNewCommander += self.__onHoverNewCommander
        self._subscribeFilterHandlers(self.viewModel)
        g_clientUpdateManager.addCallbacks({'inventory': self.__onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        model = self.viewModel
        model.onCommanderClick -= self.__onCommanderClick
        model.onHoverNewCommander -= self.__onHoverNewCommander
        self._unsubscribeFilterHandlers(self.viewModel)
        super(ProfileView, self)._removeListeners()

    def _onLoadPage(self, args=None):
        args['detInvID'] = self._detInvID
        super(ProfileView, self)._onLoadPage(args)

    def _fillList(self, model):
        cards = self.__getFilteredCards()
        numberFiltered = len(cards)
        self.__ctx['currentCount'] = numberFiltered
        filtersModel = model.filtersModel
        filtersModel.setCurrent(numberFiltered)
        detachment = self._detachment
        nationID = self._detachment.nationID
        tankNation = nations.MAP[nationID]
        commandersList = model.getCommandersList()
        commandersList.clear()
        for uid, card in cards:
            state = CommanderCardConstants.STATE_AVAILABLE
            if card.portraitType == PortraitTypes.DOCUMENT:
                selected = not detachment.skinID and card.id == detachment.getDescriptor().cmdrPortraitID
                fullname = detachment.cmdrFullName if selected else ''
            else:
                selected = detachment.skinID and card.id == detachment.skinID
                crewSkin = self.itemsCache.items.getCrewSkin(card.id)
                fullname = localizedFullName(crewSkin)
                if card.nation and tankNation != card.nation or card.amount == 0:
                    state = CommanderCardConstants.STATE_DISABLE
            if selected:
                state = CommanderCardConstants.STATE_SELECTED
            commanderCardModel = CommanderCardModel()
            commanderCardModel.setId(uid)
            commanderCardModel.setIconName(card.iconName)
            commanderCardModel.setState(state)
            commanderCardModel.setType(card.type)
            commanderCardModel.setNation(card.nation)
            commanderCardModel.setAmount(card.amount)
            commanderCardModel.setNewItemsAmount(card.newAmount)
            commanderCardModel.setName(fullname)
            commanderCardModel.setPortraitType(_PORTRAIT_TYPE_TO_VM_CONST.get(card.portraitType))
            commandersList.addViewModel(commanderCardModel)

        commandersList.invalidate()

    def _resetData(self):
        super(ProfileView, self)._resetData()
        self._resetPopover()

    def _resetPopoverFilters(self):
        super(ProfileView, self)._resetPopoverFilters()
        self._resetPopover()

    def _resetPopover(self):
        if not self.__getFilteredCards():
            ProfileView._popoverFilters.update(self._defaultPopoverSetter())
        ProfileView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    def __fillModel(self, model):
        totalCount = len(self._cards)
        tankNation = nations.MAP[self._detachment.nationID]
        self.__ctx['totalCount'] = totalCount
        model.filtersModel.setTotal(totalCount)
        model.setVehicleNation(tankNation)
        self._fillList(model)

    def __getCards(self):
        detachment = self._detachment
        cards = []
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
            items = sorted(items.itervalues(), key=self.__skinSortingValue, reverse=True)
            for item in items:
                cards.append(_CardInfo(item.getID(), CommanderCardConstants.COMMANDER_TYPE_HISTORICAL if item.getHistorical() else CommanderCardConstants.COMMANDER_TYPE_NON_HISTORICAL, PortraitTypes.SKIN, None, item.getNation() or '', item.getFreeCount(), item.getIconID(), any(item.getDetachmentIDs()), item.getNewCount()))

        nationID = self._detachment.nationID
        cmdrGender = detachment.cmdrGender
        for gender in (cmdrGender, GENDER_TO_OPPOSITE[cmdrGender]):
            portraitIDs = settings_globals.g_characterProperties.getCommonPortraitIDs(nationID, gender)
            for portraitID in sorted(portraitIDs):
                iconName = settings_globals.g_characterProperties.getPortraitByID(nationID, portraitID, gender)
                cards.append(_CardInfo(portraitID, CommanderCardConstants.COMMANDER_TYPE_DEFAULT, PortraitTypes.DOCUMENT, gender, '', 0, iconName, False, 0))

        return dict(enumerate(cards))

    def __skinSortingValue(self, skin):
        nationID = self._detachment.nationID
        nation = nations.MAP[nationID]
        return (skin.getNation() is None, skin.getNation() == nation, skin.getID())

    def __getFilteredCards(self):
        criteria = popoverCriteria(self._popoverFilters)
        criteria |= toggleCriteria([ f for f, active in self._toggleFilters.iteritems() if active ])
        return [ (index, card) for index, card in self._cards.iteritems() if criteria(card) ]

    @async
    def __onCommanderClick(self, args=None):
        if isViewLoaded(R.views.lobby.detachment.dialogs.ChangeCommanderDialogView()):
            return
        else:
            if args is not None:
                cardID = int(args['id'])
                cardItem = self._cards[cardID]
                if cardItem.portraitType == PortraitTypes.SKIN and cardItem.id == self._detachment.skinID:
                    return
                ctx = {'type': cardItem.type,
                 'detachment': self._detachment,
                 'portraitID': cardItem.id,
                 'portraitIconName': cardItem.iconName,
                 'portraitType': cardItem.portraitType}
                curFirstNameID = self._detachment.getDescriptor().cmdrFirstNameID
                curSecondNameID = self._detachment.getDescriptor().cmdrSecondNameID
                if cardItem.portraitType == PortraitTypes.DOCUMENT:
                    ctx.update({'gender': cardItem.gender,
                     'firstNameID': curFirstNameID,
                     'secondNameID': curSecondNameID})
                g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.CHANGE_COMMANDER_LOOK_DIALOG)
                sdr = yield await(showDetachmentChangeCommanderDialogView(self.getParentWindow(), ctx))
                result, data = sdr.result
                if result is not DialogButtons.SUBMIT:
                    return
                firstNameID = data['nameID'] or curFirstNameID
                secondNameID = data['secondNameID'] or curSecondNameID
                curPortraitID = self._detachment.getDescriptor().cmdrPortraitID
                curSkinID = self._detachment.skinID
                changesInDocument = (firstNameID != curFirstNameID or secondNameID != curSecondNameID or curPortraitID != cardItem.id or curSkinID) and cardItem.portraitType == PortraitTypes.DOCUMENT
                changesInSkin = cardItem.portraitType == PortraitTypes.SKIN and curSkinID != cardItem.id
                if changesInDocument or changesInSkin:
                    self.__processChange(cardItem, firstNameID, secondNameID)
            return

    @decorators.process('updating')
    def __processChange(self, cardItem, firstNameID, secondNameID):
        if cardItem.portraitType == PortraitTypes.DOCUMENT:
            result = yield DetachmentChangePassport(self._detInvID, cardItem.gender, firstNameID, secondNameID, cardItem.id).request()
        else:
            result = yield CrewSkinEquip(self._detachment, cardItem.id).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self._onBack()

    def _addDefaultPopoverFilter(self):
        ProfileView._popoverFilters[PopoverFilterGroups.NATION].add(nations.MAP[self._detachment.nationID])

    def __onHoverNewCommander(self, args=None):
        uid = args['id']
        cardItem = self._cards[uid]
        if not cardItem.newAmount or cardItem.portraitType != PortraitTypes.SKIN:
            return
        with self.viewModel.transaction() as model:
            commandersList = model.getCommandersList()
            cmdrModel = findFirst(lambda model: model.getId() == uid, commandersList)
            crewSkin = self.itemsCache.items.getCrewSkin(cardItem.id)
            self.__saveViewedData({cardItem.id: crewSkin.getCount()})
            self._cards[uid] = cardItem._replace(newAmount=0)
            cmdrModel.setNewItemsAmount(0)
            commandersList.invalidate()

    def __onClientUpdate(self, diff):
        self._detachment = self.detachmentCache.getDetachment(self._detInvID)
        self._cards = self.__getCards()
        with self.viewModel.transaction() as model:
            self.__fillModel(model)

    def __getNameByID(self, firstNameID, secondNameID):
        nationID = self._detachment.nationID
        gender = self._detachment.cmdrGender
        pool = settings_globals.g_characterProperties
        firstName = pool.getFirstNameByID(nationID, firstNameID, gender=gender)
        secondName = pool.getSecondNameByID(nationID, secondNameID, gender=gender)
        return (firstName, secondName)

    def __saveViewedData(self, viewedItems):
        if not viewedItems:
            return
        crewSkins = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        crewSkins.update(viewedItems)
        AccountSettings.setSettings(CREW_SKINS_VIEWED, crewSkins)

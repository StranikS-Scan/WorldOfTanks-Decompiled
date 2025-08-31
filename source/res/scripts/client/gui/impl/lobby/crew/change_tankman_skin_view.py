# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/change_tankman_skin_view.py
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.dialogs.dialogs import showSkinApplyDialog, showDocumentChangeDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_data_card_model import PersonalDataCardModel, DataCardState, DataCardType
from gui.impl.gen.view_models.views.lobby.crew.change_tankman_skin_view_model import ChangeTankmanSkinViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.crew.filter import getPersonalDataCardTypeSettings
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, CrewSkinsDataProvider, DocumentsDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.crew_skin import localizedFullName, CrewSkin, GenderRestrictionsLocales
from helpers import dependency
from items import tankmen
from items.components.crew_skins_constants import CREW_SKIN_PROPERTIES_MASKS, TANKMAN_SEX
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from th_async import th_async, th_await
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class ChangeTankmanSkinView(ViewImpl):
    __slots__ = ('__tankmanID', '__selectedIcon', '__selectedIconID', '__selectedSkinID', '__selectedNation', 'filterPanelWidget', '__filterState', '__tankman', '__dataProviders')
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.personalData())
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    onTankmanIconChanged = Event.Event()

    def __init__(self, layoutID, **kwargs):
        self.__tankmanID = kwargs.get('tankmanID')
        self.__selectedIcon = kwargs.get('selectedIcon')
        self.__selectedIconID = kwargs.get('selectedIconID')
        self.__selectedSkinID = kwargs.get('selectedSkinID')
        self.__selectedNation = kwargs.get('selectedNation')
        settings = ViewSettings(layoutID, ViewFlags.VIEW, ChangeTankmanSkinViewModel())
        self.__tankman = None
        self.__filterState = FilterState({FilterState.GROUPS.PERSONALDATATYPE.value: ['suitableSkin', 'document']})
        self.filterPanelWidget = FilterPanelWidget(getPersonalDataCardTypeSettings(), None, R.strings.crew.filter.popup.skinChange.title(), self.__filterState, panelType=FilterPanelType.PERSONALDATA, popoverTooltipHeader=R.strings.crew.personalData.filter.tooltip.popoverButton.title(), popoverTooltipBody=R.strings.crew.personalData.filter.tooltip.popoverButton.body())
        self.__dataProviders = CompoundDataProvider(skins=CrewSkinsDataProvider(self.__filterState, self.tankman), documents=DocumentsDataProvider(self.__filterState, self.tankman))
        super(ChangeTankmanSkinView, self).__init__(settings, **kwargs)
        return

    @property
    def viewModel(self):
        return super(ChangeTankmanSkinView, self).getViewModel()

    @property
    def tankman(self):
        if self.__tankman is None:
            self.__tankman = self.itemsCache.items.getTankman(self.__tankmanID)
        return self.__tankman

    @property
    def skinID(self):
        return self.tankman.skinID if self.__selectedSkinID is None else self.__selectedSkinID

    @property
    def iconID(self):
        return self.tankman.descriptor.iconID if self.__selectedIconID is None else self.__selectedIconID

    @property
    def icon(self):
        return self.tankman.icon if self.__selectedIcon is None else self.__selectedIcon

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChangeTankmanSkinView, self).createToolTip(event)

    @staticmethod
    def getTooltipData(event):
        return createTooltipData(specialAlias=event.getArgument('tooltipId'), isSpecial=True, specialArgs=(int(event.getArgument('skinId')),))

    def _onLoading(self, *args, **kwargs):
        super(ChangeTankmanSkinView, self)._onLoading(*args, **kwargs)
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self.filterPanelWidget)
        self.__dataProviders.subscribe()
        self.__dataProviders.update()

    def _getEvents(self):
        return ((self.viewModel.onResetFilters, self.__onResetFilters),
         (self.viewModel.onNewCardViewed, self.__onNewCardViewed),
         (self.viewModel.onCardSelected, self.__onCardSelected),
         (self.viewModel.onViewClose, self.__onViewClose),
         (self.__filterState.onStateChanged, self.__onFilterStateUpdated),
         (self.__dataProviders.onDataChanged, self.__fillModel),
         (self.platoonCtrl.onMembersUpdate, self.__onMembersUpdate))

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryUpdate),)

    def _clear(self):
        self.__tankman = None
        return

    def _finalize(self):
        self._clear()
        self.__dataProviders.unsubscribe()
        self.__dataProviders.clear()
        super(ChangeTankmanSkinView, self)._finalize()

    def __onMembersUpdate(self):
        self.destroyWindow()

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff or GUI_ITEM_TYPE.CREW_SKINS in invDiff:
            tankman = self.itemsCache.items.getTankman(self.__tankmanID)
            if tankman is None:
                return
            self.__tankman = tankman
            self.__dataProviders.reinit(self.tankman)
            self.__dataProviders.update()
        return

    @args2params(int)
    def __onNewCardViewed(self, cardID):
        newCount = 0
        with self.viewModel.transaction() as tx:
            cards = tx.getCardList()
            for card in cards:
                if card.getId() == cardID:
                    newCount = card.getNewAmount()
                    card.setNewAmount(0)
                    break

            cards.invalidate()
        crewSkins = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        viewedSkinsCount = crewSkins.get(cardID, 0)
        crewSkins[cardID] = viewedSkinsCount + newCount
        AccountSettings.setSettings(CREW_SKINS_VIEWED, crewSkins)

    @th_async
    @args2params(int, bool)
    def __onCardSelected(self, cardID, isSkin):
        if isSkin:
            if self.__selectedSkinID != cardID:
                result = yield showSkinApplyDialog(cardID, self.__tankmanID)
                self.__checkResultData(result.result[0], True, cardID, None)
        else:
            docsProvider = self.__dataProviders['documents']
            cardData = None
            for item in docsProvider.items():
                if item.icon.id == cardID:
                    cardData = item
                    break

            result = yield th_await(showDocumentChangeDialog(self.__tankmanID, cardData))
            result, tankmanIcon = result.result
            self.__checkResultData(result, False, tankmanIcon.id, tankmanIcon.value)
        return

    def __checkResultData(self, result, isSkin, iconId, icon=None):
        if result:
            self.__fillModel()
            if isSkin:
                self.__selectedSkinID = iconId
                self.onTankmanIconChanged(icon, iconId, isSkin)
            else:
                self.__selectedIcon = icon
                self.__selectedIconID = iconId
                self.onTankmanIconChanged(icon, iconId, isSkin)
            self.destroyWindow()

    def __onResetFilters(self):
        self.filterPanelWidget.resetState()

    def __onViewClose(self):
        self.destroyWindow()

    def __onFilterStateUpdated(self):
        self.__dataProviders.update()
        self.filterPanelWidget.applyStateToModel()

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setIsCardsLocked(self.__isTankmanLocked())
            tx.setNation(self.__selectedNation)
            cards = tx.getCardList()
            cards.clear()
            selectedCard = PersonalDataCardModel()
            self.__fillSelectedCard(selectedCard)
            cards.addViewModel(selectedCard)
            self.__fillCrewSkins(cards)
            self.__fillDocuments(cards)
            if len(cards) == 1:
                cards.clear()
            self.filterPanelWidget.updateAmountInfo(len(cards), self.__dataProviders.initialItemsCount)
            cards.invalidate()

    def __fillSelectedCard(self, card):
        if self.__selectedSkinID:
            skin = self.itemsCache.items.getCrewSkin(self.__selectedSkinID)
            self.__fillSkinCard(card, skin)
        else:
            self.__fillDocumentCard(card, self.iconID, self.icon)
            card.setCardState(DataCardState.SELECTED)
            card.setName(self.tankman.fullUserName)

    def __fillDocuments(self, cards):
        for icon, _, _ in self.__dataProviders['documents'].items():
            card = PersonalDataCardModel()
            if icon.id != self.iconID:
                self.__fillDocumentCard(card, icon.id, icon.value)
                if card.getCardState() != DataCardState.SELECTED:
                    cards.addViewModel(card)

    def __fillDocumentCard(self, card, cardId, icon):
        card.setId(cardId)
        card.setIcon(R.images.gui.maps.icons.tankmen.icons.big.dyn(Tankman.getDynIconName(icon))())
        card.setCardType(DataCardType.DOCUMENT)
        card.setCardState(DataCardState.DEFAULT)
        if self.__isTankmanLocked():
            card.setCardState(DataCardState.DISABLED)

    def __fillCrewSkins(self, cards):
        skins = self.__dataProviders['skins'].items()
        if self.tankman and self.tankman.skinID:
            skins.append(self.itemsCache.items.getCrewSkin(self.tankman.skinID))
        for item in skins:
            vm = PersonalDataCardModel()
            self.__fillSkinCard(vm, item)
            if vm.getCardState() != DataCardState.SELECTED:
                cards.addViewModel(vm)

    def __fillSkinCard(self, card, crewSkin):
        cache = tankmen.g_cache.crewSkins()
        restrictionsLocales = {}
        if crewSkin.getSex() in TANKMAN_SEX.ALL:
            restrictionsLocales[CREW_SKIN_PROPERTIES_MASKS.SEX] = backport.text(R.strings.item_types.tankman.gender.dyn(GenderRestrictionsLocales.KEYS[crewSkin.getSex()])())
        if crewSkin.getNation() is not None:
            restrictionsLocales[CREW_SKIN_PROPERTIES_MASKS.NATION] = backport.text(R.strings.nations.dyn(crewSkin.getNation())())
        isValid, validationMask, _ = cache.validateCrewSkin(self.tankman.descriptor, crewSkin.getID())
        card.setId(crewSkin.getID())
        card.setName(localizedFullName(crewSkin))
        if crewSkin.getNation() is not None:
            card.setNation(crewSkin.getNation())
        card.setIcon(R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(crewSkin.getIconID())())
        if self.tankman and self.tankman.skinID == crewSkin.getID() and not self.tankman.skinID == self.__selectedSkinID:
            inventoryCount = crewSkin.getFreeCount() + 1
        elif self.__selectedSkinID == crewSkin.getID() and self.tankman.skinID != self.__selectedSkinID:
            inventoryCount = crewSkin.getFreeCount() - 1
        else:
            inventoryCount = crewSkin.getFreeCount()
        card.setInventoryCount(inventoryCount)
        card.setNewAmount(crewSkin.getNewCount())
        card.setCardType(DataCardType.SKIN)
        card.setCardState(DataCardState.DEFAULT)
        if self.__selectedSkinID == crewSkin.getID():
            card.setCardState(DataCardState.SELECTED)
        elif not isValid or inventoryCount == 0 or self.__isTankmanLocked():
            card.setCardState(DataCardState.DISABLED)
        restrictions = card.getRestrictions()
        if not isValid:
            restrictionsLoc = list(restrictionsLocales.iteritems())
            restrictionsLoc.sort(key=lambda position: position[0])
            for key, loc in restrictionsLoc:
                if key & validationMask:
                    restrictions.addString(loc)

        return

    def __isTankmanLocked(self):
        return self.tankman.isLockedByVehicle() or self.tankman.descriptor.getRestrictions().isPassportReplacementForbidden()


class ChangeTankmanSkinViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, tankmanID, selectedIcon, selectedIconID, selectedSkinID, selectedNation, parent=None):
        super(ChangeTankmanSkinViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ChangeTankmanSkinView(R.views.lobby.crew.ChangeTankmanSkinView(), tankmanID=tankmanID, selectedIcon=selectedIcon, selectedIconID=selectedIconID, selectedSkinID=selectedSkinID, selectedNation=selectedNation), parent=parent)

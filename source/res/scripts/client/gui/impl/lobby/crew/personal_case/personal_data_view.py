# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/personal_case/personal_data_view.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.dialogs.dialogs import showSkinApplyDialog, showDocumentChangeDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_data_card_model import PersonalDataCardModel, DataCardState, DataCardType
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_data_view_model import PersonalDataViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.crew.filter import getPersonalDataCardTypeSettings
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, CrewSkinsDataProvider, DocumentsDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.crew_skin import localizedFullName, CrewSkin, GenderRestrictionsLocales
from gui.shared.gui_items.processors.tankman import CrewSkinUnequip
from gui.shared.utils import decorators
from helpers import dependency
from items import tankmen
from items.components.crew_skins_constants import CREW_SKIN_PROPERTIES_MASKS, TANKMAN_SEX
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewPersonalDataKeys
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class PersonalDataView(IPersonalTab, BasePersonalCaseView):
    __slots__ = ('tankmanID', 'filterPanelWidget', '__filterState', '__tankman')
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.personalData())
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, layoutID=R.views.lobby.crew.personal_case.PersonalDataView(), **kwargs):
        self.tankmanID = kwargs.get('tankmanID')
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, PersonalDataViewModel())
        self.__tankman = None
        self.__filterState = FilterState({FilterState.GROUPS.PERSONALDATATYPE.value: ['suitableSkin', 'document']})
        self.filterPanelWidget = FilterPanelWidget(getPersonalDataCardTypeSettings(), None, R.strings.crew.filter.popup.skinChange.title(), self.__filterState, panelType=FilterPanelType.PERSONALDATA, popoverTooltipHeader=R.strings.crew.personalData.filter.tooltip.popoverButton.title(), popoverTooltipBody=R.strings.crew.personalData.filter.tooltip.popoverButton.body())
        self.__dataProviders = CompoundDataProvider(skins=CrewSkinsDataProvider(self.__filterState, self.tankman), documents=DocumentsDataProvider(self.__filterState, self.tankman))
        super(PersonalDataView, self).__init__(settings, **kwargs)
        return

    @property
    def viewModel(self):
        return super(PersonalDataView, self).getViewModel()

    @property
    def tankman(self):
        if self.__tankman is None:
            self.__tankman = self.itemsCache.items.getTankman(self.tankmanID)
        return self.__tankman

    def onChangeTankman(self, tankmanID):
        self.tankmanID = tankmanID
        self.__tankman = self.itemsCache.items.getTankman(tankmanID)
        self.__dataProviders.reinit(self.tankman)
        self.__dataProviders.update()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PersonalDataView, self).createToolTip(event)

    @staticmethod
    def getTooltipData(event):
        return createTooltipData(specialAlias=event.getArgument('tooltipId'), isSpecial=True, specialArgs=(int(event.getArgument('skinId')),))

    def _onLoading(self, *args, **kwargs):
        super(PersonalDataView, self)._onLoading(*args, **kwargs)
        self.getParentView().setChildView(FilterPanelWidget.LAYOUT_ID(), self.filterPanelWidget)
        self.__dataProviders.subscribe()
        self.__dataProviders.update()

    def _getEvents(self):
        return ((self.viewModel.onResetFilters, self.__onResetFilters),
         (self.viewModel.onNewCardViewed, self.__onNewCardViewed),
         (self.viewModel.onCardSelected, self.__onCardSelected),
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
        super(PersonalDataView, self)._finalize()

    def __onMembersUpdate(self):
        self.destroyWindow()

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff or GUI_ITEM_TYPE.CREW_SKINS in invDiff:
            tankman = self.itemsCache.items.getTankman(self.tankmanID)
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

    @wg_async
    @args2params(int, bool)
    def __onCardSelected(self, cardID, isSkin):
        tankman = self.itemsCache.items.getTankman(self.tankmanID)
        if isSkin:
            self.uiLogger.logClick(CrewPersonalDataKeys.SKIN_CARD)
            if tankman.skinID != cardID:
                showSkinApplyDialog(cardID, self.tankmanID)
            else:
                self.__unEquipCrewSkin()
        else:
            self.uiLogger.logClick(CrewPersonalDataKeys.DOCUMENT_CARD)
            docsProvider = self.__dataProviders['documents']
            cardData = None
            for item in docsProvider.items():
                if item.icon.id == cardID:
                    cardData = item
                    break

            result = yield wg_await(showDocumentChangeDialog(self.tankmanID, cardData))
            if result.result and tankman.isInSkin:
                self.__unEquipCrewSkin()
        return

    @decorators.adisp_process('updating')
    def __unEquipCrewSkin(self):
        unEquip = CrewSkinUnequip(self.tankmanID)
        yield unEquip.request()

    def __onResetFilters(self):
        self.filterPanelWidget.resetState()

    def __onFilterStateUpdated(self):
        self.__dataProviders.update()
        self.filterPanelWidget.applyStateToModel()

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setIsCardsLocked(self.__isTankmanLocked())
            cards = tx.getCardList()
            cards.clear()
            cards.invalidate()
            selectedCard = PersonalDataCardModel()
            self.__fillSelectedCard(selectedCard)
            cards.addViewModel(selectedCard)
            self.__fillCrewSkins(cards)
            self.__fillDocuments(cards)
            if len(cards) == 1:
                cards.clear()
            self.filterPanelWidget.updateAmountInfo(len(cards), self.__dataProviders.initialItemsCount + 1)

    def __fillSelectedCard(self, card):
        if self.tankman.isInSkin:
            skin = self.itemsCache.items.getCrewSkin(self.tankman.skinID)
            self.__fillSkinCard(card, skin)
        else:
            self.__fillDocumentCard(card, self.tankman.descriptor.iconID, self.tankman.icon, self.tankman.firstUserName, self.tankman.lastUserName)

    def __fillDocuments(self, cards):
        for icon, firstname, lastname in self.__dataProviders['documents'].items():
            card = PersonalDataCardModel()
            self.__fillDocumentCard(card, icon.id, icon.value, firstname.value, lastname.value)
            if card.getCardState() != DataCardState.SELECTED:
                cards.addViewModel(card)

    def __fillDocumentCard(self, card, cardId, icon, firstname, lastname):
        card.setId(cardId)
        card.setName('%s %s' % (firstname, lastname))
        card.setIcon(R.images.gui.maps.icons.tankmen.icons.big.dyn(Tankman.getDynIconName(icon))())
        card.setCardType(DataCardType.DOCUMENT)
        card.setCardState(DataCardState.DEFAULT)
        if self.tankman.descriptor.iconID == cardId:
            card.setName(self.tankman.fullUserName)
            if not self.tankman.isInSkin:
                card.setCardState(DataCardState.SELECTED)
        elif self.__isTankmanLocked():
            card.setCardState(DataCardState.DISABLED)

    def __fillCrewSkins(self, cards):
        for item in self.__dataProviders['skins'].items():
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
        inventoryCount = crewSkin.getFreeCount()
        card.setInventoryCount(inventoryCount)
        card.setNewAmount(crewSkin.getNewCount())
        card.setCardType(DataCardType.SKIN)
        card.setCardState(DataCardState.DEFAULT)
        if self.tankmanID in crewSkin.getTankmenIDs():
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

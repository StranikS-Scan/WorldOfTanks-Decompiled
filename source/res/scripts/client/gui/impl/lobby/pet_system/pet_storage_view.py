# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/pet_storage_view.py
import logging
from itertools import chain
from adisp import adisp_process
from frameworks.wulf import WindowFlags
from frameworks.wulf.view.array import fillStringsArray
from gui.game_control.links import URLMacros
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.pet_card_model import PetCardModel
from gui.impl.gen.view_models.views.lobby.pet_system.pet_name_model import PetNameModel
from gui.impl.gen.view_models.views.lobby.pet_system.pet_storage_view_model import PetStorageViewModel, SynergyStateEnum, VisibilityStateEnum
from gui.impl.gen.view_models.views.lobby.pet_system.promotion_model import PromoBonus
from gui.impl.lobby.pet_system.tooltips.synergy_tooltip import SynergyTooltip
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.pet_system.bonus_helper import BonusItem, BonusNameToPromoStr
from gui.pet_system.pet_item_helper import PetItem, PromoPetItem
from gui.pet_system.pet_ui_settings import PetUISettings
from gui.pet_system.processor import SelectActivePetProcessor, SelectPetActiveBonusProcessor, SelectPetNameProcessor, SelectPetStateProcessor
from gui.pet_system.synergy_helper import SynergyItem
from gui.server_events.events_dispatcher import showMissions
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events as events_constants
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showPetInfoPage, showShop, showHangar
from helpers import dependency
from pet_system_common import pet_constants
from pet_system_common.PetPromoConfig import PromoSource
from pet_system_common.pet_constants import PetStateBehavior
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.pet_system import IPetSystemController
_logger = logging.getLogger(__name__)
STATE_MAPPING = {VisibilityStateEnum.ALWAYS.value: PetStateBehavior.BASIC,
 VisibilityStateEnum.DISABLEANIMATION.value: PetStateBehavior.CALM,
 VisibilityStateEnum.ONLYINTOPETPLACE.value: PetStateBehavior.HIDDEN}
MODEL_STATE_MAPPING = {PetStateBehavior.BASIC: VisibilityStateEnum.ALWAYS,
 PetStateBehavior.CALM: VisibilityStateEnum.DISABLEANIMATION,
 PetStateBehavior.HIDDEN: VisibilityStateEnum.ONLYINTOPETPLACE}

class PetStorageView(ViewComponent):
    LAYOUT_ID = R.views.mono.pet_system.pet_storage()
    __petController = dependency.descriptor(IPetSystemController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        super(PetStorageView, self).__init__(self.LAYOUT_ID, PetStorageViewModel, *args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        super(PetStorageView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        events = super(PetStorageView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onPetSelect, self.__onPetSelect),
         (self.viewModel.onBonusSelect, self.__onBonusSelect),
         (self.viewModel.onCardSelect, self.__onCardSelect),
         (self.viewModel.onSaveName, self.__updatePetName),
         (self.viewModel.onCloseNameSelection, self.__updateSeenNames),
         (self.viewModel.onSaveVisibility, self.__updateStateBehavior),
         (self.viewModel.onInfoPageOpen, self.__openInfoPage),
         (self.viewModel.promotionModel.onChallengeSelect, self.__onToGameView),
         (self.viewModel.promotionModel.onPurchaseSelect, self.__onToPurchase),
         (self.__petController.onUpdateEventData, self.__tryToShowEvent),
         (self.__petController.onUpdateUnlockedPetsIDs, self.__onUpdateUnlockedPetsIDs),
         (self.__petController.onUpdateAppliedBonus, self.__updateBonusCount),
         (self.__petController.onUpdateSynergy, self.__onUpdateSynergy),
         (self.__petController.onUpdateActivePet, self.__onUpdateActivePet),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _getListeners(self):
        events = super(PetStorageView, self)._getListeners()
        return events + ((events_constants.PetSystemEvent.LAST_SEEN_SYNERGY_LEVEL_UPDATED, self.__onUpdateSynergy, EVENT_BUS_SCOPE.LOBBY),)

    @property
    def viewModel(self):
        return super(PetStorageView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SynergyTooltip(petID=self.getViewModel().getPetID()) if contentID == R.views.mono.pet_system.tooltips.synergy_tooltip() else None

    def closeWindow(self):
        self.destroyWindow()
        showHangar()

    def __onClose(self):
        self.closeWindow()

    def __update(self):
        self.__setActivePet()
        self.__updatePetData()
        self.__updateBonuses()
        self.__updateCards()
        self.__updateNameList()

    def __setActivePet(self, petId=None):
        activePetId = petId or self.__petController.getActivePet()
        petInHangar = self.__petController.getPetIDInHangar()
        with self.getViewModel().transaction() as tx:
            tx.setActivePetID(activePetId)
            tx.setIsPetSelected(petInHangar == activePetId)
            tx.setVisibilityState(MODEL_STATE_MAPPING.get(self.__petController.getStateBehavior()))

    def __updatePetData(self, petId=None):
        activePetId = self.__petController.getActivePet()
        petInHangar = self.__petController.getPetIDInHangar()
        currentPetId = petId or petInHangar
        isPromo = currentPetId not in self.__petController.getUnlockedPets()
        itemClass = PromoPetItem if isPromo else PetItem
        if currentPetId:
            with self.getViewModel().transaction() as tx:
                tx.promotionModel.setIsPromotionEnabled(isPromo)
                if isPromo:
                    promoPetSources = self.__petController.getPetsPromoConfig().getSources(currentPetId)
                    tx.promotionModel.setIsChallengeButtonEnabled(PromoSource.QUEST_PROGRESSION in promoPetSources)
                    tx.promotionModel.setIsPurchaseButtonEnabled(PromoSource.SHOP in promoPetSources)
                    promoStrList = []
                    petBonusID = first(BonusItem.getPetBonuses(currentPetId))
                    promoStrList.append(BonusNameToPromoStr.get(BonusItem.getBonusName(petBonusID)))
                    promoStrList.append(PromoBonus.EVENTS.value)
                    if self.__petController.getGeneralConfig().showCaseEnabled:
                        promoStrList.append(PromoBonus.SHOWOFF.value)
                    promoBonuses = tx.promotionModel.getPromotionBonuses()
                    fillStringsArray(promoStrList, promoBonuses)
                    self.__markPromoAsSeen(currentPetId, tx)
                tx.setPetNameID(itemClass.getCurrentNameId(currentPetId))
                tx.setPetID(currentPetId)
                tx.setPetType(itemClass.getPetType(currentPetId))
                tx.setBreedName(itemClass.getPetBreed(currentPetId))
                tx.setSynergyState(self.__getSynergyState(currentPetId))
                tx.setIsPetSelected(currentPetId == activePetId)
                tx.setHasUniqueName(itemClass.getIsDefaultNameLocked(currentPetId))
                tx.setVisibilityState(MODEL_STATE_MAPPING.get(self.__petController.getStateBehavior()))
                tx.setIsUnsuitableMode(not self.__petController.checkBonusCapsForPetBonus())
            self.__tryToShowEvent()

    def __getSynergyState(self, petID):
        if SynergyItem.isMaxSynergyLevel(petID):
            return SynergyStateEnum.COMPLETE
        return SynergyStateEnum.UPDATEDRECENTLY if SynergyItem.getSynergyLevel(petID) > PetUISettings.getLastSeenSynergyLevel(petID) else SynergyStateEnum.INCOMPLETE

    def __markPromoAsSeen(self, petId, model):
        PetUISettings.addSeenPromoPetID(petId)
        for card in model.getCards():
            if card.getPetID() == petId:
                card.setIsNew(False)
                return

    def __updateBonuses(self):
        self.__updateBonusCount()
        bonuses = BonusItem.getAvailableBonuses()
        if bonuses:
            with self.getViewModel().transaction() as tx:
                bonusesModel = tx.getBonuses()
                bonusesModel.clear()
                BonusItem.packBonusModelData(bonuses, bonusesModel)
                tx.setSelectedBonus(BonusItem.getActiveBonus() or -1)

    def __updateBonusCount(self):
        totalCount = BonusItem.getBonusesPerDay()
        self.viewModel.setCurrentCount(totalCount - BonusItem.getAppliedBonusCount())
        self.viewModel.setTotalCount(totalCount)

    def __updateCards(self):
        unlockedPetIDs = self.__petController.getUnlockedPets()
        promoPetIDs = self.__petController.getPetsPromoConfig().getAvailablePets(unlockedPetIDs)
        seenPetIDs = PetUISettings.getSeenInStoragePetIDs()
        seenPromoPetIDs = PetUISettings.getSeenPromoPetIDs()
        with self.getViewModel().transaction() as tx:
            cards = tx.getCards()
            cards.clear()
            for petID in chain(sorted(promoPetIDs, reverse=True), reversed(unlockedPetIDs)):
                card = PetCardModel()
                card.setPetID(petID)
                if petID not in unlockedPetIDs:
                    card.setIsNew(petID not in seenPromoPetIDs)
                    card.setPetNameID(PromoPetItem.getCurrentNameId(petID))
                    petBonuses = BonusItem.getPetBonuses(petID)
                    if petBonuses:
                        card.setBonusName(BonusItem.getBonusName(first(petBonuses)))
                        card.setBonusValue(BonusItem.getBonusValue(first(petBonuses)))
                else:
                    card.setPetNameID(PetItem.getCurrentNameId(petID))
                card.setIsMaxSynergyLevel(SynergyItem.isMaxSynergyLevel(petID))
                cards.addViewModel(card)
                seenPetIDs.add(petID)

            cards.invalidate()
            PetUISettings.setSeenInStoragePetIDs(seenPetIDs)

    def __updateNameList(self):
        with self.getViewModel().transaction() as tx:
            availableNameIDs = self.__petController.getAvailableNames()
            seenNameIDs = PetUISettings.getSeenPetNameIDs()
            newNameIDs = availableNameIDs - seenNameIDs
            hasNewNames = True if newNameIDs else False
            tx.setHasNewNames(hasNewNames)
            petNames = tx.getPetNames()
            petNames.clear()
            self.__setNames(petNames, newNameIDs, isNew=True)
            self.__setNames(petNames, seenNameIDs, isNew=False)
            petNames.invalidate()

    def __setNames(self, petNames, nameIDs, isNew=False):
        sortedNameIDs = self.__sortNames(nameIDs)
        for nameID in sortedNameIDs:
            nameModel = PetNameModel()
            nameModel.setPetNameID(nameID)
            nameModel.setIsNew(isNew)
            petNames.addViewModel(nameModel)

    @staticmethod
    def __sortNames(nameIDs):
        names = {}
        for nameID in nameIDs:
            names[nameID] = PetItem.getPetName(nameID)

        return sorted(names.keys(), key=lambda x: names[x])

    @adisp_process
    def __onPetSelect(self, args):
        petID = int(args.get('petID'))
        yield SelectActivePetProcessor(petID).request()

    @adisp_process
    def __onBonusSelect(self, args):
        bonusID = args.get('bonusID')
        if not bonusID:
            _logger.error('Invalid bonusID received, args: %s', args)
            return
        bonusID = int(bonusID)
        result = yield SelectPetActiveBonusProcessor(bonusID).request()
        if result.success:
            self.viewModel.setSelectedBonus(bonusID)

    def __onCardSelect(self, args):
        petId = int(args.get('petID'))
        self.__updatePetData(petId)
        self.__petController.changePet(petId)

    @adisp_process
    def __updatePetName(self, args):
        petNameID = int(args.get('petNameID'))
        petID = int(args.get('petID'))
        result = yield SelectPetNameProcessor(petID, petNameID).request()
        if result.success:
            self.getViewModel().setPetNameID(petNameID)
            self.__updateSeenNames()
            for card in self.viewModel.getCards():
                if card.getPetID() == petID:
                    card.setPetNameID(petNameID)

    def __updateSeenNames(self):
        petNameIDs = self.__petController.getAvailableNames()
        PetUISettings.setSeenPetNameIDs(petNameIDs)
        if self.viewModel.getHasNewNames():
            self.__updateNameList()

    @adisp_process
    def __updateStateBehavior(self, args):
        visibilityState = int(args.get('visibilityState'))
        state = STATE_MAPPING.get(visibilityState, PetStateBehavior.BASIC)
        result = yield SelectPetStateProcessor(state).request()
        if result.success:
            self.viewModel.setVisibilityState(VisibilityStateEnum(visibilityState))

    @staticmethod
    def __openInfoPage():
        showPetInfoPage()

    def __tryToShowEvent(self):
        if self.__petController.getActivePet() != self.getViewModel().getPetID() and self.__petController.getActiveEvent():
            self.__petController.showEventView()

    def __onUpdateUnlockedPetsIDs(self, *_):
        self.__petController.changePet(self.__petController.getPetIDInHangar())
        self.__update()

    def __onUpdateSynergy(self, *_):
        self.__updatePetData(self.getViewModel().getPetID())
        self.__updateCards()

    def __onUpdateActivePet(self, petID):
        self.__setActivePet(petID)
        self.__updatePetData(petID)

    def __onServerSettingsChanged(self, diff):
        if pet_constants.PETS_SYSTEM_CONFIG in diff:
            if not self.__petController.isEnabled:
                self.closeWindow()
                return
            sysDiff = diff[pet_constants.PETS_SYSTEM_CONFIG]
            if pet_constants.PetPromoConsts.CONFIG_NAME in sysDiff:
                if not self.__petController.haveActivePromotion() and not self.__petController.getActivePet():
                    self.closeWindow()
                    return
            self.__update()

    @adisp_process
    def __onToPurchase(self):
        shopUrl = PromoPetItem.getPromoShopUrl(self.viewModel.getPetID())
        url = PromoPetItem.getPromoUrl(self.viewModel.getPetID())
        if not url and not shopUrl:
            _logger.error('Invalid urls for pet id %s', self.viewModel.getPetID())
            return
        if shopUrl:
            showShop(shopUrl)
        else:
            url = yield URLMacros().parse(url)
            g_eventBus.handleEvent(events_constants.OpenLinkEvent(events_constants.OpenLinkEvent.SPECIFIED, url=url))

    def __onToGameView(self):
        showMissions()


class PetStorageViewWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(PetStorageViewWindow, self).__init__(content=PetStorageView(), wndFlags=WindowFlags.WINDOW, layer=layer)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/pet_house_marker_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.pet_house_marker_model import PetHouseMarkerModel
from gui.impl.pub import ViewImpl
from gui.pet_system.pet_item_helper import PetItem
from gui.pet_system.pet_ui_settings import PetUISettings
from gui.shared import events as events_constants
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency
from pet_system_common import pet_constants
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.pet_system import IPetSystemController

class PetHouseMarkerView(ViewImpl):
    __petController = dependency.descriptor(IPetSystemController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.pet_house_marker())
        settings.model = PetHouseMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PetHouseMarkerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(PetHouseMarkerView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        events = super(PetHouseMarkerView, self)._getEvents()
        return events + ((self.__petController.onUpdateActivePet, self.__update), (self.__petController.onUpdateUnlockedPetsIDs, self.__update), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _getListeners(self):
        events = super(PetHouseMarkerView, self)._getListeners()
        return events + ((events_constants.PetSystemEvent.SEEN_IN_STORAGE_PET_IDS_UPDATED, self.__update, EVENT_BUS_SCOPE.LOBBY),)

    @property
    def viewModel(self):
        return super(PetHouseMarkerView, self).getViewModel()

    def __update(self, *_):
        with self.getViewModel().transaction() as tx:
            activePetId = self.__petController.getActivePet()
            if activePetId:
                nameId = PetItem.getCurrentNameId(activePetId)
                tx.setPetNameID(nameId)
            else:
                tx.setPetNameID(0)
            seenPetIDs = PetUISettings.getSeenInStoragePetIDs()
            petIDs = self.__petController.getUnlockedAndPromoPets()
            tx.setHasUpdate(any((petID not in seenPetIDs for petID in petIDs)))

    def __onServerSettingsChanged(self, diff):
        sysDiff = diff.get(pet_constants.PETS_SYSTEM_CONFIG, {})
        if pet_constants.PetPromoConsts.CONFIG_NAME in sysDiff:
            self.__update()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_PET_SLOT_VISITED
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.ny_constants import InternalViewState, SyncDataKeys, ViewAliases
from new_year_common.items.components.ny_constants import PET_TOY_TYPES
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel
from new_year.gui.impl.new_year.new_year_helper import updateSlots
from new_year.gui.impl.lobby.new_year.popovers.ny_decorations_popover import NyDecorationsPopover
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_decoration_tooltip import NyPetDecorationTooltip
from helpers import dependency
from new_year.skeletons.new_year import INewYearRaccoonController

class NyPetView(HistorySubModelPresenter):
    _INTERNAL_VIEW_STATE = InternalViewState.RACCOON
    __raccoonCtrl = dependency.descriptor(INewYearRaccoonController)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.onNySettingsChanged, self.__onNySettingsChanged),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene))

    def createToolTipContent(self, event, contentID):
        return NyPetDecorationTooltip(event.getArgument('toyID')) if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetDecorationTooltip() else super(NyPetView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        if not AccountSettings.getNewYear(NY_PET_SLOT_VISITED):
            AccountSettings.setNewYear(NY_PET_SLOT_VISITED, True)
        if event.contentID == R.views.new_year.lobby.new_year.popovers.NyDecorationsPopover():
            slotId = int(event.getArgument('slotId'))
            return NyDecorationsPopover(slotId)
        return super(NyPetView, self).createPopOverContent(event)

    def initialize(self, *args, **kwargs):
        super(NyPetView, self).initialize(*args, **kwargs)
        with self.viewModel.transaction() as model:
            updateSlots(fullUpdate=True, model=model, slotGroup=PET_TOY_TYPES)
            model.setIsSlotVisited(AccountSettings.getNewYear(NY_PET_SLOT_VISITED) or self.__hasToyInSlots(model))

    def finalize(self):
        self.__raccoonCtrl.onViewExit()
        super(NyPetView, self).finalize()

    def __onDataUpdated(self, keys):
        checkKeys = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS}
        with self.viewModel.transaction() as model:
            if set(keys) & checkKeys:
                updateSlots(fullUpdate=True, model=model, slotGroup=PET_TOY_TYPES)

    def __hasToyInSlots(self, model):
        for items in model.groupSlots.getItems():
            for slot in items.slots.getItems():
                if slot.getIsEmpty() is False:
                    return True

        return False

    def __onNySettingsChanged(self):
        config = getNewYearGeneralConfig()
        if config is not None and not config.getPetVisible():
            NewYearNavigation.closeMainView(True)
        return

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        if NewYearNavigation.getCurrentViewName() == ViewAliases.PET_VIEW:
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))

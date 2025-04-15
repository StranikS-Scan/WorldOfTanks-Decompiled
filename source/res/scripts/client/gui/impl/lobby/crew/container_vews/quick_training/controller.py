# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/controller.py
import BigWorld
import typing
import SoundGroups
from goodies import goodie_constants
from gui.impl.dialogs import dialogs
from gui.impl.gen.view_models.views.lobby.crew.help_navigate_from import HelpNavigateFrom
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.crew.container_vews.quick_training.events import QuickTrainingViewEvents
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.shared import event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.items_actions import factory
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import List, Tuple, Callable
    from Event import Event
    from gui.impl.lobby.container_views.base.events import ComponentEventsBase
_ACTION_KEY = 'action'
_ACTION_TYPE_KEY = 'actionType'
_ADD_KEY = 'add'
_PERCENT_KEY = 'percent'
CREW_BOOKS_PURCHASE_ENABLED = 'isCrewBooksPurchaseEnabled'
IS_MENTORING_LICENSE_ENABLED = 'isMentoringLicenseEnabled'
FREE_XP_STEPPER_ACTION = {'perk': {_ADD_KEY: lambda stepper: stepper.getSkillUpXpCost(),
          'subtract': lambda stepper: stepper.getSkillDownXpCost()},
 _PERCENT_KEY: {_ADD_KEY: lambda stepper: stepper.getLevelUpXpCost(),
                'subtract': lambda stepper: stepper.getLevelDownXpCost()}}

class QuickTrainingInteractionController(InteractionController):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getEventsProvider(self):
        return QuickTrainingViewEvents()

    def _getEvents(self):
        return [(self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChange),
         (self.eventsProvider.onFreeXpMouseEnter, self._onFreeXpMouseEnter),
         (self.eventsProvider.onFreeXpSelected, self._onFreeXpSelected),
         (self.eventsProvider.onFreeXpUpdated, self._onFreeXpStepperUpdate),
         (self.eventsProvider.onFreeXpManualInput, self._onFreeXpManualInput),
         (self.eventsProvider.onBookMouseEnter, self._onBookMouseEnter),
         (self.eventsProvider.onBookSelected, self._onBookSelected),
         (self.eventsProvider.onBuyBook, self._onBuyBook),
         (self.eventsProvider.onLearn, self._onLearn),
         (self.eventsProvider.onCancel, self._onCancel),
         (self.eventsProvider.onMentoringClick, self._onMentoringClick),
         (self.eventsProvider.onPostProgressionOpen, self._onPostProgression)]

    def onInventoryUpdate(self, invDiff):
        updatedCrew = {}
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            updatedCrew = invDiff[GUI_ITEM_TYPE.VEHICLE].get('crew', {})
            vehsCompDescr = invDiff[GUI_ITEM_TYPE.VEHICLE].get('compDescr', {})
            if self.context.vehicleID != NO_VEHICLE_ID and self.context.vehicle and self.context.vehicleID in vehsCompDescr and vehsCompDescr[self.context.vehicleID] is None:
                self.view.destroyWindow()
                return
            if self.context.isSingleTankman:
                return
        if updatedCrew:
            updatedVehicleIDs = [ (k[0] if isinstance(k, tuple) else k) for k in updatedCrew.keys() ]
            if self.context.vehicle and self.context.vehicle.invID not in updatedVehicleIDs:
                return
            if self.context.tankmanID not in updatedCrew.values()[0]:
                self.context.update()
            self.__clearAllSelection()
            self.context.updateOnGlobalSync()
            self.view.crewWidget.updateSlotIdx(self.context.slotIdx)
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            if not updatedCrew:
                self.context.updateOnGlobalSync()
            self.__clearAllSelection()
            self.__updatePossibleCrewXp()
        if GUI_ITEM_TYPE.CREW_BOOKS in invDiff:
            self.context.updateBooks()
        self.refresh()
        return

    def onGoodiesUpdate(self, diff):
        if goodie_constants.MENTORING_LICENSE_GOODIE_ID in diff:
            self.refresh()

    def onGlobalFreeXpChange(self):
        self.context.updateOnFreeXpGlobalChange()
        self.__updatePossibleCrewXp()
        self.refresh()

    def onChangeTankman(self, tankmanID=NO_TANKMAN, slotIdx=NO_SLOT):
        self.view.crewWidget.updateSlotIdx(slotIdx)
        self.context.update(tankmanID, slotIdx)
        self.__updatePossibleCrewXp()
        self.refresh()

    def onEmptyWidgetSlotClick(self, _, slotIdx):
        event_dispatcher.showChangeCrewMember(slotIdx, self.context.vehicleID, self.view.layoutID)

    @staticmethod
    def onAbout():
        event_dispatcher.showCrewAboutView(navigateFrom=HelpNavigateFrom.QUICKTRAINING)

    def onCardMouseLeave(self):
        self.context.selection.clearPreSelected()
        self.context.stepper.setInitialPossibleValues()
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onServerSettingsChange(self, diff):
        if CREW_BOOKS_PURCHASE_ENABLED in diff or IS_MENTORING_LICENSE_ENABLED in diff:
            self.refresh()

    def _onFreeXpMouseEnter(self):
        self.__refreshStepperWithAcquiringXp()
        self.context.selection.setPreSelectedFreeXp(self.context.stepper.getSkillUpXpCost())
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onFreeXpSelected(self, isSelected):
        if isSelected:
            self.context.selection.setFreeXpFromPreSelected()
            self.__refreshStepperWithAcquiringXp()
            if self.context.selection.freeXp == 0:
                self.context.selection.freeXp = self.context.stepper.getSkillUpXpCost()
            self.context.selection.clearPreSelected()
        else:
            self.context.selection.freeXp = 0
            self.context.stepper.setInitialPossibleValues()
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onFreeXpStepperUpdate(self, data):
        actionType = data.get(_ACTION_TYPE_KEY, _PERCENT_KEY)
        action = data.get(_ACTION_KEY, _ADD_KEY)
        self.context.selection.freeXp = FREE_XP_STEPPER_ACTION[actionType][action](self.context.stepper)
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onFreeXpManualInput(self, value):
        self.context.selection.freeXp = value
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onBookSelected(self, bookId, count):
        book = self.itemsCache.items.getItemByCD(int(bookId))
        self.context.selection.setBook(book, int(count))
        if self.context.selection.freeXp > 0 and not self.context.selection.hasAnyBook:
            self.context.stepper.setInitialPossibleValues()
            self.context.selection.freeXp = self.context.stepper.getSkillUpXpCost()
        self.context.selection.clearPreSelected()
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onBookMouseEnter(self, bookId):
        book = self.itemsCache.items.getItemByCD(int(bookId))
        self.context.selection.setPreSelectedBook(book)
        self.__updatePossibleCrewXp()
        self.refresh()

    @staticmethod
    def _onBuyBook(bookId):
        dialogs.showCrewBooksPurchaseDialog(crewBookCD=int(bookId))

    def _onLearn(self):
        doActions = []
        if self.context.selection.freeXp > 0 and self.context.canCrewSelectFreeXp:
            doActions.append((factory.USE_FREE_XP_TO_TANKMAN, self.context.selection.freeXp, self.context.tankmanID))
        for bookCD in self.context.selection.books.keys():
            book = self.itemsCache.items.getItemByCD(bookCD)
            count = self.context.selection.getBookCountById(bookCD)
            if book.isPersonal() and self.context.isSingleTankman and not self.context.canCurrentTankmanUsePersonalBook:
                continue
            doActions.append((factory.USE_CREW_BOOK,
             bookCD,
             self.context.vehicleID if self.context.vehicle and not book.isPersonal() else NO_VEHICLE_ID,
             count,
             self.context.tankmanID if self.context.tankmanID != NO_TANKMAN and book.isPersonal() else NO_TANKMAN))

        self.__clearAllSelection()
        hasActionsToPerform = len(doActions) > 0
        if hasActionsToPerform:
            SoundGroups.g_instance.playSound2D(SOUNDS.CREW_LEARN_CLICK)
            BigWorld.player().doActions(doActions)

    def _onCancel(self):
        self.__clearAllSelection()
        self.__updatePossibleCrewXp()
        self.refresh()

    def _onMentoringClick(self):
        event_dispatcher.showMentorAssignment(tankmanInvID=self.context.tankmanID, previousViewID=self.view.layoutID, vehicleInvID=self.context.vehicleID, parent=self.view)

    @staticmethod
    def _onPostProgression():
        event_dispatcher.showCrewPostProgressionView()

    def __clearAllSelection(self):
        self.context.selection.clear()
        self.context.stepper.setInitialPossibleValues()

    def __updatePossibleCrewXp(self):
        self.context.updatePossibleCrewState()
        self.view.crewWidget.updatePossibleSkillsLevel(*self.context.getPossibleCrewSkillsAndEfficiencies())

    def __refreshStepperWithAcquiringXp(self):
        self.context.stepper.setInitialPossibleValues()
        personalBooksXp, commonBooksXp = self.context.selection.getAcquiringBooksXpValues()
        self.context.stepper.setAquiringPersonalXp(commonBooksXp + personalBooksXp)

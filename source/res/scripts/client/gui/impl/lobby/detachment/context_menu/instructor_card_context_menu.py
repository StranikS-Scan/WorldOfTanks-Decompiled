# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/instructor_card_context_menu.py
import BigWorld
from async import async, await
from gui import SystemMessages
from gui.shared.utils import decorators
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.dialogs import dialogs
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.shared.event_dispatcher import showInstructorPageWindow, isViewLoaded
from gui.shared.gui_items.processors.detachment import SetActiveInstructorInDetachment
from helpers import dependency
from items.components.detachment_constants import INVALID_INSTRUCTOR_SLOT_ID
from shared_utils import CONST_CONTAINER
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger

class MenuItems(CONST_CONTAINER):
    PERSONAL_CASE = 'instructorPersonalCase'
    SWITCH_SOUND = 'switchInstructorSound'
    REMOVE = 'removeInstructor'
    MOVE_LEFT = 'moveInstructorLeft'
    MOVE_RIGHT = 'moveInstructorRight'


class MenuHandlers(CONST_CONTAINER):
    PERSONAL_CASE = '_showPersonalCase'
    SWITCH_SOUND = '_switchSound'
    REMOVE = '_removeInstructor'
    MOVE_LEFT = '_moveLeft'
    MOVE_RIGHT = '_moveRight'


class InstructorCardContextMenu(AbstractContextMenuHandler):
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET_CONTEXT_MENU)

    def __init__(self, cmProxy, ctx=None):
        super(InstructorCardContextMenu, self).__init__(cmProxy, ctx, {MenuItems.PERSONAL_CASE: MenuHandlers.PERSONAL_CASE,
         MenuItems.SWITCH_SOUND: MenuHandlers.SWITCH_SOUND,
         MenuItems.REMOVE: MenuHandlers.REMOVE,
         MenuItems.MOVE_LEFT: MenuHandlers.MOVE_LEFT,
         MenuItems.MOVE_RIGHT: MenuHandlers.MOVE_RIGHT})
        self._isInstructorActive = False

    def _initFlashValues(self, ctx):
        self._slotID = int(ctx.slotIndex)
        self._detInvID = int(ctx.detInvID)
        self._detachment = self.__detachmentCache.getDetachment(ctx.detInvID)
        instructorIDs = self._detachment.getInstructorsIDs()
        self._instructorInvID = instructorIDs[self._slotID]

    def _makeMenuLabel(self, menuId):
        return backport.text(R.strings.menu.contextMenu.dyn(menuId)())

    def _generateOptions(self, ctx=None):
        detachment = self._detachment
        vehicle = self.__itemsCache.items.getVehicle(detachment.vehInvID)
        serverSettings = self.__lobbyContext.getServerSettings()
        instructorsIDs = detachment.getInstructorsIDs()
        invID = self._instructorInvID
        instructorItem = self.__detachmentCache.getInstructor(invID)
        capacity = instructorItem.descriptor.getSlotsCount()
        totalSlots = len(instructorsIDs)
        isInstructorSlotsEnabled = serverSettings.isInstructorSlotsEnabled()
        isExcludeInstructorEnabled = serverSettings.isExcludeInstructorEnabled()
        canRemove = not vehicle.isCrewLocked and isInstructorSlotsEnabled and isExcludeInstructorEnabled and not instructorItem.isUnremovable
        activeInstructorInvID = detachment.getDescriptor().getActiveInstructorInvID()
        instuctorHasVoice = bool(instructorItem.voiceOverID)
        self._isInstructorActive = activeInstructorInvID == instructorItem.invID
        options = [self._makeItem(MenuItems.PERSONAL_CASE, self._makeMenuLabel(MenuItems.PERSONAL_CASE), {'enabled': isInstructorSlotsEnabled})]
        if instuctorHasVoice:
            label = 'disableInstructorSound' if self._isInstructorActive else 'enableInstructorSound'
            options.extend([self._makeItem(MenuItems.SWITCH_SOUND, self._makeMenuLabel(label), {'enabled': isInstructorSlotsEnabled})])
        options.append(self._makeItem(MenuItems.REMOVE, self._makeMenuLabel(MenuItems.REMOVE), {'enabled': canRemove}))
        if capacity != totalSlots:
            slotID = instructorsIDs.index(invID)
            canMoveLeft = slotID > 0 and not vehicle.isCrewLocked
            canMoveRight = slotID + capacity < totalSlots and not vehicle.isCrewLocked
            options.extend([self._makeItem(MenuItems.MOVE_LEFT, self._makeMenuLabel(MenuItems.MOVE_LEFT), {'enabled': canMoveLeft and isInstructorSlotsEnabled}), self._makeItem(MenuItems.MOVE_RIGHT, self._makeMenuLabel(MenuItems.MOVE_RIGHT), {'enabled': canMoveRight and isInstructorSlotsEnabled})])
        return options

    def _showPersonalCase(self):
        slotID = self._slotID
        instructorInvID = self._instructorInvID
        args = {'instructorInvID': instructorInvID if instructorInvID is not None else 0,
         'slotID': slotID,
         'detInvID': self._detInvID}
        previousViewSettings = NavigationViewSettings(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': self._detInvID})
        if instructorInvID is not None:
            showInstructorPageWindow({'navigationViewSettings': NavigationViewSettings(NavigationViewModel.INSTRUCTOR_PAGE, args, previousViewSettings)})
        return

    @decorators.process('updating')
    def _switchSound(self):
        slotID = INVALID_INSTRUCTOR_SLOT_ID if self._isInstructorActive else self._slotID
        processor = SetActiveInstructorInDetachment(self._detInvID, slotID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)

    @async
    def _removeInstructor(self):
        if isViewLoaded(R.views.lobby.detachment.dialogs.DemountInstructorDialogView()):
            return
        else:
            yield await(dialogs.demountInstructor(None, ctx={'instructorInvID': self._instructorInvID}))
            return

    def _moveLeft(self):
        BigWorld.player().inventory.moveInstructor(self._detInvID, self._slotID, -1)

    def _moveRight(self):
        BigWorld.player().inventory.moveInstructor(self._detInvID, self._slotID, 1)

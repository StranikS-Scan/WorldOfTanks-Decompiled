# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchor_states.py
import logging
from Math import Vector3
from gui.Scaleform.daapi.view.lobby.customization.shared import isSlotFilled, isItemsQuantityLimitReached, REGIONS_SLOTS
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from vehicle_outfit.outfit import Area
_logger = logging.getLogger(__name__)
_ANCHOR_SHIFT = {GUI_ITEM_TYPE.EMBLEM: 0.5,
 GUI_ITEM_TYPE.INSCRIPTION: 0.3}
_REGION_ANCHOR_SHIFT = 0.2

class StateContext(object):
    __slots__ = ('_state',)

    def __init__(self):
        super(StateContext, self).__init__()
        self._state = None
        return

    def changeState(self, newState):
        if self._state is not None:
            self._state.onExitState()
        self._state = newState
        self._state.onEnterState()
        return

    def destroy(self):
        self._state = None
        return


class Anchor(StateContext):
    __slots__ = ('__service', '__slotId', '__uid', '__anchorShift', '__position', '__direction', '__ctx')
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, slotId, uid, position, direction):
        super(Anchor, self).__init__()
        self.__slotId = slotId
        self.__uid = uid
        self._state = AnchorState(self)
        self.__anchorShift = getAnchorShift(self.slotId, direction)
        self.__ctx = self.__service.getCtx()
        self.__position = position
        self.__direction = direction

    @property
    def position(self):
        return self.__position

    @property
    def direction(self):
        return self.__direction

    @property
    def state(self):
        return self._state

    @property
    def slotId(self):
        return self.__slotId

    @property
    def uid(self):
        return self.__uid

    @property
    def stateID(self):
        return self._state.stateID

    @property
    def shift(self):
        return self.__anchorShift

    @property
    def updater(self):
        return self.__ctx.vehicleAnchorsUpdater

    def changeState(self, newState):
        super(Anchor, self).changeState(newState)
        self.__ctx.vehicleAnchorsUpdater.onAnchorStateChanged(self.uid, self.stateID)

    def updateState(self):
        outfit = self.__ctx.mode.getModifiedOutfit(self.__ctx.season)
        lock = isItemsQuantityLimitReached(outfit, self.slotId.slotType)
        if isSlotFilled(outfit, self.slotId):
            newState = UnselectedFilledState(self)
        elif lock:
            newState = LockedState(self)
        else:
            newState = UnselectedEmptyState(self)
        if self.stateID != newState.stateID:
            self.changeState(newState)

    def setup(self):
        if self.slotId.slotType in REGIONS_SLOTS and self.shift is not None:
            self.__ctx.vehicleAnchorsUpdater.setAnchorShift(self.slotId, self.shift)
        self.updateState()
        return

    def destroy(self):
        super(Anchor, self).destroy()
        self.__ctx = None
        return

    def setShift(self, shift):
        self.__anchorShift = shift
        self.__ctx.vehicleAnchorsUpdater.setAnchorShift(self.slotId, self.shift)


class BaseState(object):
    __slots__ = ('_context',)

    def __init__(self, context):
        self._context = context

    def changeState(self, newState):
        self._context.changeState(newState)
        self._context = None
        return

    def onEnterState(self):
        pass

    def onExitState(self):
        pass


class AnchorState(BaseState):
    __slots__ = ('_service', 'stateID', '_ctx')
    _service = dependency.descriptor(ICustomizationService)
    stateID = None

    def __init__(self, anchor):
        super(AnchorState, self).__init__(anchor)
        self._ctx = self._service.getCtx()

    @property
    def anchor(self):
        return self._context

    @property
    def updater(self):
        return self.anchor.updater

    def onItemInstalled(self):
        pass

    def onItemRemoved(self):
        pass

    def onItemSelected(self):
        pass

    def onItemUnselected(self):
        pass

    def onHovered(self):
        pass

    def onUnhovered(self):
        pass

    def onSelected(self):
        pass

    def onUnselected(self):
        pass

    def onLocked(self):
        pass

    def onUnlocked(self):
        pass


class UnselectedEmptyState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_UNSELECTED_EMPTY

    def onItemInstalled(self):
        newState = UnselectedFilledState(self.anchor)
        self.changeState(newState)

    def onHovered(self):
        newState = PreviewState(self.anchor)
        self.changeState(newState)

    def onSelected(self):
        newState = SelectedEmptyState(self.anchor)
        self.changeState(newState)

    def onLocked(self):
        newState = LockedState(self.anchor)
        self.changeState(newState)


class UnselectedFilledState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_UNSELECTED_FILLED

    def onHovered(self):
        newState = RemoveState(self.anchor)
        self.changeState(newState)

    def onSelected(self):
        newState = SelectedFilledState(self.anchor)
        self.changeState(newState)

    def onEnterState(self):
        if self.anchor.slotId.slotType in _ANCHOR_SHIFT and self.anchor.shift is not None:
            self.updater.setAnchorShift(self.anchor.slotId, self.anchor.shift)
        return

    def onExitState(self):
        if self.anchor.slotId.slotType in _ANCHOR_SHIFT:
            self.updater.setAnchorShift(self.anchor.slotId, Vector3())


class SelectedEmptyState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_SELECTED_EMPTY

    def onItemInstalled(self):
        newState = SelectedFilledState(self.anchor)
        self.changeState(newState)

    def onUnselected(self):
        newState = UnselectedEmptyState(self.anchor)
        self.changeState(newState)


class SelectedFilledState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_SELECTED_FILLED

    def onUnselected(self):
        newState = UnselectedFilledState(self.anchor)
        self.changeState(newState)

    def onEnterState(self):
        if self.anchor.slotId.slotType == GUI_ITEM_TYPE.EMBLEM:
            self.updater.setAnchorShift(self.anchor.slotId, Vector3())

    def onExitState(self):
        if self.anchor.slotId.slotType == GUI_ITEM_TYPE.EMBLEM and self.anchor.shift is not None:
            self.updater.setAnchorShift(self.anchor.slotId, self.anchor.shift)
        return


class PreviewState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_PREVIEW

    def onItemInstalled(self):
        newState = UnselectedFilledState(self.anchor)
        self.changeState(newState)

    def onUnhovered(self):
        newState = UnselectedEmptyState(self.anchor)
        self.changeState(newState)

    def onItemUnselected(self):
        newState = UnselectedEmptyState(self.anchor)
        self.changeState(newState)

    def onEnterState(self):
        item = self._ctx.mode.selectedItem
        if item is None:
            _logger.warning('no item selected')
            return
        else:
            self._ctx.mode.previewItem(item.intCD, self.anchor.slotId)
            return

    def onExitState(self):
        self._ctx.mode.removeItemPreview(self.anchor.slotId)


class LockedState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_LOCKED

    def onUnlocked(self):
        newState = UnselectedEmptyState(self.anchor)
        self.changeState(newState)


class RemoveState(AnchorState):
    stateID = CUSTOMIZATION_ALIASES.ANCHOR_STATE_REMOVED

    def onItemRemoved(self):
        newState = UnselectedEmptyState(self.anchor)
        self.changeState(newState)

    def onUnhovered(self):
        newState = UnselectedFilledState(self.anchor)
        self.changeState(newState)

    def onItemUnselected(self):
        newState = UnselectedFilledState(self.anchor)
        self.changeState(newState)


@dependency.replace_none_kwargs(service=ICustomizationService)
def getAnchorShift(slotId, direction, service=None):
    if slotId.slotType in REGIONS_SLOTS:
        if slotId.areaId != Area.GUN:
            return -direction * _REGION_ANCHOR_SHIFT
    elif slotId.slotType in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
        anchorParams = service.getAnchorParams(slotId.areaId, slotId.slotType, slotId.regionIdx)
        slotWidth = anchorParams.descriptor.size
        slotHeight = slotWidth * SLOT_ASPECT_RATIO.get(slotId.slotType, 0)
        shift = slotHeight * _ANCHOR_SHIFT.get(slotId.slotType, 0)
        return anchorParams.location.up * shift
    return None

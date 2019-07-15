# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/vehicle_anchor_states.py
from helpers import dependency
from Math import Vector3
from skeletons.gui.customization import ICustomizationService
from gui.Scaleform.daapi.view.lobby.customization.shared import REGIONS_SLOTS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
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
    __slots__ = ('customizationService', '__anchorId', '__uid', '__anchorShift', '__customizationContext', '__position', '__direction')
    customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, anchorId, uid, position, direction):
        super(Anchor, self).__init__()
        self.__anchorId = anchorId
        self.__uid = uid
        self._state = AnchorState(self)
        self.__anchorShift = getAnchorShift(self.anchorId)
        self.__customizationContext = self.customizationService.getCtx()
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
    def anchorId(self):
        return self.__anchorId

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
        return self.__customizationContext.vehicleAnchorsUpdater

    def changeState(self, newState):
        super(Anchor, self).changeState(newState)
        self.__customizationContext.vehicleAnchorsUpdater.onAnchorStateChanged(self.uid, self.stateID)

    def updateState(self):
        outfit = self.__customizationContext.getModifiedOutfit(self.__customizationContext.currentSeason)
        lock = self.__customizationContext.isC11nItemsQuantityLimitReached(outfit, self.anchorId.slotType)
        if self.__customizationContext.isSlotFilled(self.anchorId):
            newState = UnselectedFilledState(self)
        elif lock:
            newState = LockedState(self)
        else:
            newState = UnselectedEmptyState(self)
        if self.stateID != newState.stateID:
            self.changeState(newState)

    def setup(self):
        if self.anchorId.slotType in REGIONS_SLOTS or self.anchorId.slotType == GUI_ITEM_TYPE.EMBLEM:
            if self.shift is not None:
                self.__customizationContext.vehicleAnchorsUpdater.setAnchorShift(self.anchorId, self.shift)
        self.updateState()
        return

    def destroy(self):
        super(Anchor, self).destroy()
        self.__customizationContext = None
        return

    def setShift(self, shift):
        self.__anchorShift = shift
        self.__customizationContext.vehicleAnchorsUpdater.setAnchorShift(self.anchorId, self.shift)


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
    __slots__ = ('customizationService', 'stateID', '_customizationContext')
    customizationService = dependency.descriptor(ICustomizationService)
    stateID = None

    def __init__(self, anchor):
        super(AnchorState, self).__init__(anchor)
        self._customizationContext = self.customizationService.getCtx()

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
        if self.anchor.anchorId.slotType == GUI_ITEM_TYPE.INSCRIPTION and self.anchor.shift is not None:
            self.updater.setAnchorShift(self.anchor.anchorId, self.anchor.shift)
        return

    def onExitState(self):
        if self.anchor.anchorId.slotType == GUI_ITEM_TYPE.INSCRIPTION:
            self.updater.setAnchorShift(self.anchor.anchorId, Vector3())


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
        if self.anchor.anchorId.slotType == GUI_ITEM_TYPE.EMBLEM:
            self.updater.setAnchorShift(self.anchor.anchorId, Vector3())

    def onExitState(self):
        if self.anchor.anchorId.slotType == GUI_ITEM_TYPE.EMBLEM and self.anchor.shift is not None:
            self.updater.setAnchorShift(self.anchor.anchorId, self.anchor.shift)
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
        self._customizationContext.previewSelectedDecal(self.anchor.anchorId)

    def onExitState(self):
        self._customizationContext.removeDecalPreview(self.anchor.anchorId)


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
def getAnchorShift(anchorId, service=None):
    if anchorId.slotType in REGIONS_SLOTS:
        if anchorId.areaId != Area.GUN:
            anchorParams = service.getAnchorParams(anchorId.areaId, anchorId.slotType, anchorId.regionIdx)
            return -anchorParams.location.normal * _REGION_ANCHOR_SHIFT
    elif anchorId.slotType in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
        anchorParams = service.getAnchorParams(anchorId.areaId, anchorId.slotType, anchorId.regionIdx)
        slotWidth = anchorParams.descriptor.size
        slotHeight = slotWidth * SLOT_ASPECT_RATIO.get(anchorId.slotType, 0)
        shift = slotHeight * _ANCHOR_SHIFT.get(anchorId.slotType, 0)
        return anchorParams.location.up * shift
    return None

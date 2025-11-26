# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/pet_object_tooltip_presenter.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.pet_object_tooltip_model import PetObjectTooltipModel
from gui.impl.lobby.pet_system.tooltips.pet_storage_tooltip import PetStorageTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.pet_system.constants import EVENT_NAME_FORMAT
from gui.pet_system.pet_item_helper import PetItem
from gui.pet_system.requester import INVALID_EVENT_ID, INVALID_PET_ID
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import PetObjectHoverEvent, PetSystemEvent
from helpers import dependency
from pet_system_common.pet_constants import PetHangarObject, PetStateBehavior
from gui.impl.gen import R
from skeletons.gui.pet_system import IPetSystemController

class _Tooltips(object):
    NONE = ''
    STORAGE = 'storageTooltip'
    EVENT = 'eventTooltip'


class PetObjectTooltipPresenter(ViewComponent[PetObjectTooltipModel]):
    __petController = dependency.descriptor(IPetSystemController)

    def __init__(self):
        super(PetObjectTooltipPresenter, self).__init__(model=PetObjectTooltipModel)

    @property
    def viewModel(self):
        return super(PetObjectTooltipPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return PetStorageTooltip() if contentID == R.views.mono.pet_system.tooltips.pet_storage_tooltip() else super(PetObjectTooltipPresenter, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent():
            eventID = self.__petController.getActiveEvent()
            petName = PetItem.getPetName(PetItem.getCurrentNameId())
            return createSimpleTooltip(self.getParentWindow(), event, backport.text(R.strings.pet_events.title.dyn(EVENT_NAME_FORMAT.format(eventID))()), backport.text(R.strings.pet_system.petEventTooltip.body(), petName=petName))
        return super(PetObjectTooltipPresenter, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(PetObjectTooltipPresenter, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(PetSystemEvent(PetSystemEvent.PET_OBJECT_PRESENTER_LOADING), scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        g_eventBus.handleEvent(PetSystemEvent(PetSystemEvent.PET_OBJECT_PRESENTER_CLOSING), scope=EVENT_BUS_SCOPE.LOBBY)
        super(PetObjectTooltipPresenter, self)._finalize()

    def _getListeners(self):
        return ((PetObjectHoverEvent.HOVER_IN, self.__onHoverInEvent), (PetObjectHoverEvent.HOVER_OUT, self.__onHoverOutEvent))

    def __onHoverInEvent(self, event):
        if PetItem.getActivePetID() == INVALID_PET_ID:
            return
        tooltip = self.__getTooltipToShow(event.ctx.get('objectName'))
        if tooltip == _Tooltips.NONE:
            return
        with self.getViewModel().transaction() as model:
            model.setIsStorageTooltipVisible(tooltip == _Tooltips.STORAGE)
            model.setIs3dObjectTooltipVisible(tooltip == _Tooltips.EVENT)

    def __getTooltipToShow(self, hoveredObj):
        hasActiveEvent = self.__petController.getActiveEvent() != INVALID_EVENT_ID
        isPetHidden = self.__petController.getStateBehavior() == PetStateBehavior.HIDDEN
        if hoveredObj == PetHangarObject.STORAGE:
            if hasActiveEvent and isPetHidden:
                return _Tooltips.EVENT
            return _Tooltips.STORAGE
        if hoveredObj == PetHangarObject.PET:
            if hasActiveEvent and not isPetHidden:
                return _Tooltips.EVENT
        return _Tooltips.NONE

    def __onHoverOutEvent(self, _):
        with self.getViewModel().transaction() as model:
            model.setIsStorageTooltipVisible(False)
            model.setIs3dObjectTooltipVisible(False)

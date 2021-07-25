# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/detachment_view.py
from gui.Scaleform.daapi.view.meta.DetachmentViewMeta import DetachmentViewMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import DetachmentViewEvent
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl.lobby.detachment.sound_constants import BARRACKS_SOUND_SPACE
from uilogging.detachment.loggers import setTTCAdapterGroup

class DetachmentView(DetachmentViewMeta):
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __itemsCache = descriptor(IItemsCache)

    def __init__(self, ctx):
        super(DetachmentView, self).__init__()
        self.__parametersView = None
        self.__injectView = None
        self.__ctx = ctx
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == HANGAR_ALIASES.DETACHMENT_VIEW_INJECT:
            super(DetachmentView, self).registerFlashComponent(component, alias, self.__ctx)
        else:
            super(DetachmentView, self).registerFlashComponent(component, alias)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(DetachmentView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.DETACHMENT_VIEW_VEHICLE_PARAMS:
            self.__parametersView = viewPy
        if alias == HANGAR_ALIASES.DETACHMENT_VIEW_INJECT:
            self.__injectView = viewPy.injectView
        setTTCAdapterGroup(self.__parametersView, self.__injectView)

    def _populate(self):
        super(DetachmentView, self)._populate()
        self.__addListeners()

    def _dispose(self):
        self.__parametersView = None
        self.__injectView = None
        super(DetachmentView, self)._dispose()
        self.__removeListeners()
        return

    def __addListeners(self):
        g_eventBus.addListener(DetachmentViewEvent.UPDATE_TTC_DISPLAY_PROPS, self.__onUpdateTTCDisplayProps, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(DetachmentViewEvent.UPDATE_TTC_VEHICLE, self.__onUpdateTTCVehicle, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(DetachmentViewEvent.UPDATE_TTC_CURRENT_DETACHMENT, self.__onUpdateTTCCurrentDetachment, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(DetachmentViewEvent.UPDATE_TTC_BONUS_DETACHMENT, self.__onUpdateTTCBonusDetachment, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(DetachmentViewEvent.UPDATE_TTC_PERKS, self.__onUpdateTTCPerks, EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged

    def __removeListeners(self):
        g_eventBus.removeListener(DetachmentViewEvent.UPDATE_TTC_DISPLAY_PROPS, self.__onUpdateTTCDisplayProps, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(DetachmentViewEvent.UPDATE_TTC_VEHICLE, self.__onUpdateTTCVehicle, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(DetachmentViewEvent.UPDATE_TTC_CURRENT_DETACHMENT, self.__onUpdateTTCCurrentDetachment, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(DetachmentViewEvent.UPDATE_TTC_BONUS_DETACHMENT, self.__onUpdateTTCBonusDetachment, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(DetachmentViewEvent.UPDATE_TTC_PERKS, self.__onUpdateTTCPerks, EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def onEscapePress(self):
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.ESCAPE), EVENT_BUS_SCOPE.LOBBY)

    def __onCurrentVehicleChanged(self):
        g_detachmentTankSetupVehicle.updateVehicle()
        self.__parametersView.update()

    def __onUpdateTTCDisplayProps(self, event):
        ctx = event.ctx
        self.as_updateTTCDisplayPropsS(ctx.get('posX'), ctx.get('posY'), ctx.get('height'), ctx.get('isVisible', True))
        self.__parametersView.update()

    def __onUpdateTTCVehicle(self, event):
        vehicleItem = event.ctx.get('vehicleItem', None)
        g_detachmentTankSetupVehicle.setVehicle(vehicleItem)
        self.__parametersView.update()
        return

    def __onUpdateTTCCurrentDetachment(self, event):
        detachmentID = event.ctx.get('detachmentID', None)
        g_detachmentTankSetupVehicle.setCurrentDetachment(detachmentID)
        return

    def __onUpdateTTCBonusDetachment(self, event):
        detachmentID = event.ctx.get('detachmentID', None)
        g_detachmentTankSetupVehicle.setBonusDetachment(detachmentID)
        self.__parametersView.update()
        return

    def __onUpdateTTCPerks(self, event):
        bonusPerks = event.ctx.get('bonusPerks', {})
        comparableInstructor = event.ctx.get('comparableInstructor', False)
        g_detachmentTankSetupVehicle.setVehicleBonusPerks(bonusPerks, comparableInstructor=comparableInstructor)
        self.__parametersView.update()

    def __onReturnBack(self, event):
        self.destroy()

    def __onCloseInjectView(self, event):
        self.destroy()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/ammunition_setup_view.py
from functools import partial
import BigWorld
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.Scaleform.daapi.view.meta.AmmunitionSetupViewMeta import AmmunitionSetupViewMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.events import AmmunitionSetupViewEvent
from helpers import dependency
from items import ITEM_TYPES
from skeletons.gui.shared import IItemsCache

class AmmunitionSetupView(AmmunitionSetupViewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(AmmunitionSetupView, self).__init__()
        self.__ctx = ctx
        self.__updateTTCCallback = None
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT:
            super(AmmunitionSetupView, self).registerFlashComponent(component, alias, self.__ctx)
        else:
            super(AmmunitionSetupView, self).registerFlashComponent(component, alias)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(AmmunitionSetupView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_VEHICLE_PARAMS:
            self.__parametersView = viewPy
        elif alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT:
            viewPy.getInjectView().onClose += self.__onCloseInjectView
            viewPy.getInjectView().onAnimationEnd += self.__onAnimationEnd

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(AmmunitionSetupView, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT:
            viewPy.getInjectView().onClose -= self.__onCloseInjectView
            viewPy.getInjectView().onAnimationEnd -= self.__onAnimationEnd

    def _populate(self):
        super(AmmunitionSetupView, self)._populate()
        g_eventBus.addListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.vehicle): self.__onClientUpdate})

    def __onClientUpdate(self, diff):
        g_detachmentTankSetupVehicle.restoreCurrentVehicle()

    def _dispose(self):
        self.__parametersView = None
        g_detachmentTankSetupVehicle.restoreCurrentVehicle()
        super(AmmunitionSetupView, self)._dispose()
        g_eventBus.removeListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__updateTTCCallback is not None:
            BigWorld.cancelCallback(self.__updateTTCCallback)
            self.__updateTTCCallback = None
        return

    def onClose(self):
        self.destroy()

    def onEscapePress(self):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def __onAmmunitionSetupViewResized(self, event):
        self.as_gfSizeUpdatedS(event.ctx.get('width'), event.ctx.get('x'))

    def __onUpdateTTC(self, event):
        vehicleItem = event.ctx.get('vehicleItem')
        defaultItem = g_detachmentTankSetupVehicle.defaultItem
        if defaultItem:
            defaultPerksController = defaultItem.getPerksController()
            if defaultPerksController:
                defaultPerksController.setOnStartCallback(partial(self.__updateTTCPerks, vehicleItem))
            else:
                self.__updateTTCCallback = BigWorld.callback(0.0, partial(self.__onUpdateTTC, event))

    def __updateTTCPerks(self, vehicle):
        g_detachmentTankSetupVehicle.setCompareVehicle(vehicle, runPerks=True)
        self.__parametersView.update()
        self.__updateTTCCallback = None
        return

    def __onCloseInjectView(self):
        self.as_showCloseAnimS()

    def __onAnimationEnd(self):
        self.as_onAnimationEndS()

    def __onChangeView(self, _):
        self.destroy()

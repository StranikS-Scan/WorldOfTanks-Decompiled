# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/ammunition_setup_view.py
from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_vehicle import g_tankSetupVehicle
from gui.Scaleform.daapi.view.meta.AmmunitionSetupViewMeta import AmmunitionSetupViewMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class AmmunitionSetupView(AmmunitionSetupViewMeta):
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, ctx):
        super(AmmunitionSetupView, self).__init__()
        self.__ctx = ctx

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
        if alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT and viewPy.getInjectView():
            viewPy.getInjectView().onClose -= self.__onCloseInjectView
            viewPy.getInjectView().onAnimationEnd -= self.__onAnimationEnd

    def _populate(self):
        super(AmmunitionSetupView, self)._populate()
        g_eventBus.addListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.__parametersView = None
        g_tankSetupVehicle.dispose()
        super(AmmunitionSetupView, self)._dispose()
        g_eventBus.removeListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)
        return

    def onClose(self):
        self.destroy()

    def onEscapePress(self):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def __onAmmunitionSetupViewResized(self, event):
        self.as_gfSizeUpdatedS(event.ctx.get('offsetX'), event.ctx.get('width'), event.ctx.get('bottomMargin'))

    def __onUpdateTTC(self, event):
        vehicleItem = event.ctx.get('vehicleItem')
        sectionName = event.ctx.get('sectionName')
        g_tankSetupVehicle.setVehicle(vehicleItem)
        self.__parametersView.update()
        if sectionName is not None:
            self.as_toggleParamsS(sectionName != TankSetupConstants.BATTLE_ABILITIES)
        return

    def __onCloseInjectView(self):
        self.as_showCloseAnimS()

    def __onAnimationEnd(self):
        self.as_onAnimationEndS()

    def __onChangeView(self, _):
        self.destroy()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/ammunition_setup_view.py
from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_vehicle import g_tankSetupVehicle
from gui.Scaleform.daapi.view.meta.AmmunitionSetupViewMeta import AmmunitionSetupViewMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class AmmunitionSetupView(AmmunitionSetupViewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _ENABLED_GF_HINTS = frozenset([TutorialHintConsts.AMMUNITION_FILTER_HINT_MC,
     TutorialHintConsts.APPLY_HANGAR_EQUIPMENT_MC,
     TutorialHintConsts.APPLY_HANGAR_OPT_DEVICE_MC,
     TutorialHintConsts.SETUP_VIEW_CARDS_EQUIPMENT_MC,
     TutorialHintConsts.SETUP_VIEW_CARDS_OPT_DEVICE_MC,
     TutorialHintConsts.SETUP_VIEW_SLOTS_OPT_DEVICE_MC,
     TutorialHintConsts.OPT_DEV_DRAG_AND_DROP_MC])

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
        if alias == HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT:
            viewPy.getInjectView().onClose -= self.__onCloseInjectView
            viewPy.getInjectView().onAnimationEnd -= self.__onAnimationEnd

    def _populate(self):
        super(AmmunitionSetupView, self)._populate()
        g_eventBus.addListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.HINT_ZONE_ADD, self.__onHintZoneAdded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, self.__onHintZoneHide, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.__parametersView = None
        g_tankSetupVehicle.dispose()
        super(AmmunitionSetupView, self)._dispose()
        g_eventBus.removeListener(AmmunitionSetupViewEvent.UPDATE_TTC, self.__onUpdateTTC, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.GF_RESIZED, self.__onAmmunitionSetupViewResized, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.HINT_ZONE_ADD, self.__onHintZoneAdded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, self.__onHintZoneHide, EVENT_BUS_SCOPE.LOBBY)
        return

    def onClose(self):
        self.destroy()

    def onEscapePress(self):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def __onAmmunitionSetupViewResized(self, event):
        self.as_gfSizeUpdatedS(event.ctx.get('width'), event.ctx.get('x'))

    def __onUpdateTTC(self, event):
        vehicleItem = event.ctx.get('vehicleItem')
        g_tankSetupVehicle.setVehicle(vehicleItem)
        self.__parametersView.update()

    def __onCloseInjectView(self):
        self.as_showCloseAnimS()

    def __onHintZoneAdded(self, event):
        ctx = event.ctx
        if ctx.get('hintName') in self._ENABLED_GF_HINTS:
            self.as_createHintAreaInComponentS(TutorialHintConsts.AMMUNITION_SETUP_VIEW_COMPONENT, ctx.get('hintName'), ctx.get('posX'), ctx.get('posY'), ctx.get('width'), ctx.get('height'))

    def __onHintZoneHide(self, event):
        ctx = event.ctx
        if ctx.get('hintName') in self._ENABLED_GF_HINTS:
            self.as_removeHintAreaS(ctx.get('hintName'))

    def __onAnimationEnd(self):
        self.as_onAnimationEndS()

    def __onChangeView(self, _):
        self.destroy()

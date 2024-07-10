# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ammunition_panel_inject.py
import BigWorld
from shared_utils import nextTick
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.AmmunitionPanelInjectMeta import AmmunitionPanelInjectMeta
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.system_factory import collectAmmunitionPanelView
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController

class AmmunitionPanelInject(AmmunitionPanelInjectMeta, IGlobalListener):
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def onPrbEntitySwitching(self):
        self.getInjectView().setPrbSwitching(True)

    def onPrbEntitySwitched(self):
        self.__invalidateInjectView()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        self.getInjectView().update()

    def onHangarSwitchAnimComplete(self, isComplete):
        self.getInjectView().setHangarSwitchAnimState(isComplete)

    def _populate(self):
        super(AmmunitionPanelInject, self)._populate()
        self.addListener(events.AmmunitionInjectEvent.INVALIDATE_INJECT_VIEW, self.__invalidateInjectView, EVENT_BUS_SCOPE.LOBBY)

    def _onPopulate(self):
        self._createInjectView()

    def _dispose(self):
        self.removeListener(events.AmmunitionInjectEvent.INVALIDATE_INJECT_VIEW, self.__invalidateInjectView, EVENT_BUS_SCOPE.LOBBY)
        super(AmmunitionPanelInject, self)._dispose()

    def _makeInjectView(self):
        viewClass = self.__getInjectViewClass()
        return viewClass(flags=ViewFlags.VIEW)

    def _addInjectContentListeners(self):
        super(AmmunitionPanelInject, self)._addInjectContentListeners()
        self.startGlobalListening()
        self.getInjectView().onPanelSectionResized += self.__onPanelSectionResized
        self.getInjectView().onVehicleChanged += self.__onVehicleChanged

    def _removeInjectContentListeners(self):
        super(AmmunitionPanelInject, self)._removeInjectContentListeners()
        self.stopGlobalListening()
        self.getInjectView().onVehicleChanged -= self.__onVehicleChanged

    def __onPanelSectionResized(self, sectionType, offsetX, offsetY, width, height):
        self.as_setHelpLayoutS({'sectionType': sectionType,
         'offsetX': offsetX,
         'offsetY': offsetY,
         'width': width,
         'height': height})

    def __onVehicleChanged(self):
        self.as_clearHelpLayoutS()

    def __getInjectViewClass(self):
        ammunitionPanelViewCls = collectAmmunitionPanelView(self.__hangarGuiCtrl.getAmmoInjectViewAlias())
        return ammunitionPanelViewCls if ammunitionPanelViewCls is not None else HangarAmmunitionPanelView

    def __invalidateInjectView(self, *_):
        injectView = self.getInjectView()
        if type(injectView) is self.__getInjectViewClass():
            injectView.update()
        else:
            nextTick(self.__recreateInjectView)()

    def __recreateInjectView(self):
        self._destroyInjected()
        player = BigWorld.player()
        if player is not None:
            self._createInjectView()
        return

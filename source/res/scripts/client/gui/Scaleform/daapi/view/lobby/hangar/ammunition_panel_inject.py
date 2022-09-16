# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ammunition_panel_inject.py
from shared_utils import nextTick
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.AmmunitionPanelInjectMeta import AmmunitionPanelInjectMeta
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from gui.impl.lobby.tank_setup.bootcamp.ammunition_panel import BootcampAmmunitionPanelView
from gui.impl.lobby.tank_setup.comp7.ammunition_panel import Comp7AmmunitionPanelView
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBootcampController, IComp7Controller

class AmmunitionPanelInject(AmmunitionPanelInjectMeta, IGlobalListener):
    __bootcampController = dependency.descriptor(IBootcampController)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def onPrbEntitySwitching(self):
        self.getInjectView().setPrbSwitching(True)

    def onPrbEntitySwitched(self):
        injectView = self.getInjectView()
        if type(injectView) is self.__getInjectViewClass():
            injectView.update()
        else:
            nextTick(self.__recreateInjectView)()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        self.getInjectView().update()

    def onHangarSwitchAnimComplete(self, isComplete):
        self.getInjectView().setHangarSwitchAnimState(isComplete)

    def _makeInjectView(self):
        viewClass = self.__getInjectViewClass()
        return viewClass(flags=ViewFlags.COMPONENT)

    def _addInjectContentListeners(self):
        super(AmmunitionPanelInject, self)._addInjectContentListeners()
        self.startGlobalListening()
        self.getInjectView().onSizeChanged += self.__onSizeChanged
        self.getInjectView().onPanelSectionResized += self.__onPanelSectionResized
        self.getInjectView().onVehicleChanged += self.__onVehicleChanged

    def _removeInjectContentListeners(self):
        super(AmmunitionPanelInject, self)._removeInjectContentListeners()
        self.stopGlobalListening()
        self.getInjectView().onSizeChanged -= self.__onSizeChanged
        self.getInjectView().onVehicleChanged -= self.__onVehicleChanged

    def __onSizeChanged(self, width, height, offsetY):
        self.as_setPanelSizeS(width, height, offsetY)

    def __onPanelSectionResized(self, sectionType, offsetX, offsetY, width, height):
        self.as_setHelpLayoutS({'sectionType': sectionType,
         'offsetX': offsetX,
         'offsetY': offsetY,
         'width': width,
         'height': height})

    def __onVehicleChanged(self):
        self.as_clearHelpLayoutS()

    def __getInjectViewClass(self):
        if self.__bootcampController.isInBootcamp():
            return BootcampAmmunitionPanelView
        return Comp7AmmunitionPanelView if self.__comp7Controller.isComp7PrbActive() else HangarAmmunitionPanelView

    def __recreateInjectView(self):
        self._destroyInjected()
        self._createInjectView()

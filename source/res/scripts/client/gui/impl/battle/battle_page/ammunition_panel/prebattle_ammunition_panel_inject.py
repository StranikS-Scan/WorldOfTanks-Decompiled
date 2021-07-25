# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_inject.py
from gui.battle_control.controllers.consumables.ammo_ctrl import IAmmoListener
from gui.battle_control.controllers.prebattle_setups_ctrl import IPrebattleSetupsListener
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView
from gui.Scaleform.daapi.view.meta.PrebattleAmmunitionPanelViewMeta import PrebattleAmmunitionPanelViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import hasAliveInject
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class PrebattleAmmunitionPanelInject(PrebattleAmmunitionPanelViewMeta, IPrebattleSetupsListener, IAmmoListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__currShellCD', '__nextShellCD')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PrebattleAmmunitionPanelInject, self).__init__()
        self.__currShellCD = None
        self.__nextShellCD = None
        return

    def onViewIsHidden(self):
        self._destroyInjected()

    @hasAliveInject()
    def setCurrentShellCD(self, shellCD):
        self._injectView.setCurrentShellCD(shellCD)

    @hasAliveInject()
    def setNextShellCD(self, shellCD):
        self._injectView.setNextShellCD(shellCD)

    def setSetupsVehicle(self, vehicle):
        self.as_showS()
        self._createInjectView(vehicle, self.__currShellCD, self.__nextShellCD)

    @hasAliveInject(deadUnexpected=True)
    def updateVehicleSetups(self, vehicle):
        self._injectView.updateViewVehicle(vehicle)

    @hasAliveInject(deadUnexpected=True)
    def stopSetupsSelection(self):
        self._injectView.updateViewActive(False)
        self.as_hideS(True)

    def _onPopulate(self):
        pass

    def _makeInjectView(self, vehicle, *args):
        return PrebattleAmmunitionPanelView(vehicle, *args)

    def _addInjectContentListeners(self):
        self._injectView.onSwitchLayout += self.__onSwitchLayout

    def _removeInjectContentListeners(self):
        self._injectView.onSwitchLayout -= self.__onSwitchLayout

    def __onSwitchLayout(self, groupID, layoutIdx):
        self.__sessionProvider.shared.prebattleSetups.switchLayout(groupID, layoutIdx)

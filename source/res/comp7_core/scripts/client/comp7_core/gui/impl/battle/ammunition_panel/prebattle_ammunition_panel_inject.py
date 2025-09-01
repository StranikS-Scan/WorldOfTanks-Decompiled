# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/battle/ammunition_panel/prebattle_ammunition_panel_inject.py
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_inject import PrebattleAmmunitionPanelInject
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import State
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from post_progression_common import TANK_SETUP_GROUPS
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class Comp7CorePrebattleAmmunitionPanelInject(PrebattleAmmunitionPanelInject):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        super(Comp7CorePrebattleAmmunitionPanelInject, self).__init__()
        self.__delayedNextShell, self.__delayedCurrShell = (None, None)
        self.__isFullStatsShown = False
        self.__closeOnFullStatsClose = False
        return None

    def setNextShellCD(self, shellCD):
        if self._state == State.PREBATTLE:
            super(Comp7CorePrebattleAmmunitionPanelInject, self).setNextShellCD(shellCD)
        else:
            self.__delayedNextShell = shellCD

    def setCurrentShellCD(self, shellCD):
        if self._state == State.PREBATTLE:
            super(Comp7CorePrebattleAmmunitionPanelInject, self).setCurrentShellCD(shellCD)
        else:
            self.__delayedCurrShell = shellCD

    def showSetupsView(self, vehicle, isArenaLoaded=False):
        if not isArenaLoaded:
            return
        super(Comp7CorePrebattleAmmunitionPanelInject, self).showSetupsView(vehicle, isArenaLoaded)

    def hideSetupsView(self):
        pass

    def stopSetupsSelection(self):
        pass

    def _populate(self):
        super(Comp7CorePrebattleAmmunitionPanelInject, self)._populate()
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        prbController = self.__sessionProvider.dynamic.prebattleSetup
        if prbController:
            prbController.onSelectionConfirmed += self.__onSelectionConfirmed
            prbController.onBattleStarted += self.__onBattleStarted
            prbController.onVehicleChanged += self.__onVehicleUpdated

    def _dispose(self):
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        prbController = self.__sessionProvider.dynamic.prebattleSetup
        if prbController:
            prbController.onSelectionConfirmed -= self.__onSelectionConfirmed
            prbController.onBattleStarted -= self.__onBattleStarted
            prbController.onVehicleChanged -= self.__onVehicleUpdated
        super(Comp7CorePrebattleAmmunitionPanelInject, self)._dispose()

    def _makeInjectView(self, vehicle, *args):
        raise NotImplementedError

    def _getShowShadows(self):
        return False

    def _switchLayout(self, groupID, layoutIdx):
        self.__sessionProvider.dynamic.prebattleSetup.switchPrebattleSetup(groupID, layoutIdx)

    def _updateCurrentState(self, isArenaLoaded):
        super(Comp7CorePrebattleAmmunitionPanelInject, self)._updateCurrentState(isArenaLoaded)
        if self._state == State.PREBATTLE:
            if not self.__sessionProvider.dynamic.prebattleSetup.isSelectionConfirmed():
                self._state = State.PREBATTLENOTCONFIRMED

    def _handleToggleFullStats(self, event):
        isFullStatsShown = event.ctx['isDown']
        self.__isFullStatsShown = isFullStatsShown
        if not isFullStatsShown and self.__closeOnFullStatsClose:
            self._hideSetupsView(useAnim=False)
            self.__closeOnFullStatsClose = False

    def __onSelectionConfirmed(self):
        self._state = State.PREBATTLE
        self.as_showShadowsS(True)
        if self.__isPrebattleSetupPossible():
            if self._injectView is not None:
                self._injectView.updateState(self._state)
                if self.__delayedNextShell:
                    self.setNextShellCD(self.__delayedNextShell)
                if self.__delayedCurrShell:
                    self.setCurrentShellCD(self.__delayedCurrShell)
        else:
            self._hideSetupsView()
        return

    def __onBattleStarted(self):
        if self.__isFullStatsShown:
            self.__closeOnFullStatsClose = True
        else:
            self._hideSetupsView()

    def __onVehicleUpdated(self, vehicle):
        if self.isActive:
            self._injectView.updateViewVehicle(vehicle, fullUpdate=False)
        elif self.__isPrebattleSetupPossible() or not self.__sessionProvider.dynamic.prebattleSetup.isSelectionConfirmed():
            self.showSetupsView(vehicle, True)

    def __isPrebattleSetupPossible(self):
        vehicle = self.__sessionProvider.dynamic.prebattleSetup.getCurrentGUIVehicle()
        if vehicle is None:
            return False
        else:
            for groupID in TANK_SETUP_GROUPS.iterkeys():
                if vehicle.isSetupSwitchActive(groupID) and not vehicle.postProgression.isPrebattleSwitchDisabled(groupID):
                    return True

            return False

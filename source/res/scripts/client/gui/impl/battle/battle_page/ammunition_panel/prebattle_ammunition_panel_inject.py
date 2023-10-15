# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_inject.py
import BigWorld
import constants
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.consumables.ammo_ctrl import IAmmoListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.prebattle_setups_ctrl import IPrebattleSetupsListener
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView, Comp7PrebattleAmmunitionPanelView
from gui.Scaleform.daapi.view.meta.PrebattleAmmunitionPanelViewMeta import PrebattleAmmunitionPanelViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import hasAliveInject
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import State
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from post_progression_common import TANK_SETUP_GROUPS
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class PrebattleAmmunitionPanelInject(MethodsRules, PrebattleAmmunitionPanelViewMeta, IPrebattleSetupsListener, IAmmoListener, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('_state', '__currShellCD', '__nextShellCD', '__timeLeft', '__isViewLoaded', '__isViewActive')

    def __init__(self):
        super(PrebattleAmmunitionPanelInject, self).__init__()
        self._state = State.BATTLELOADING
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__timeLeft = -1
        self.__isViewLoaded = False
        self.__isViewActive = False
        return

    @property
    def isActive(self):
        return self.__isViewActive and self.__isViewLoaded

    def onViewIsHidden(self):
        self.__isViewActive = False
        self._destroyInjected()

    @hasAliveInject()
    def onArenaLoaded(self):
        self._updateCurrentState(True)
        self._injectView.setTimer(-1)
        self._injectView.updateState(self._state)
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)

    @MethodsRules.delayable('showSetupsView')
    @hasAliveInject()
    def setCurrentShellCD(self, shellCD):
        self._injectView.setCurrentShellCD(shellCD)

    @MethodsRules.delayable('showSetupsView')
    @hasAliveInject()
    def setNextShellCD(self, shellCD):
        self._injectView.setNextShellCD(shellCD)

    @MethodsRules.delayable()
    def showSetupsView(self, vehicle, isArenaLoaded=False):
        if BigWorld.player().arena.guiType == constants.ARENA_GUI_TYPE.HALLOWEEN_BATTLES:
            return
        if self.__isViewActive:
            self._injectView.updateViewVehicle(vehicle, fullUpdate=False)
            return
        self.as_showS()
        self.as_showShadowsS(self._getShowShadows())
        self._updateCurrentState(isArenaLoaded)
        if self._state == State.BATTLELOADING:
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, enableAiming=False)
        self._createInjectView(vehicle, self.__currShellCD, self.__nextShellCD, self._state)
        if self.__timeLeft and self._state == State.BATTLELOADING:
            self._injectView.setTimer(self.__timeLeft)
        self.__isViewActive = True

    @hasAliveInject(deadUnexpected=True)
    def updateVehicleSetups(self, vehicle):
        self._injectView.updateViewVehicle(vehicle, False)

    @hasAliveInject(deadUnexpected=True)
    def stopSetupsSelection(self):
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)
        self._injectView.updateViewActive(False)

    @hasAliveInject(deadUnexpected=True)
    def hideSetupsView(self):
        self._hideSetupsView()

    def setCountdown(self, state, timeLeft):
        if state in (COUNTDOWN_STATE.START, COUNTDOWN_STATE.STOP) and timeLeft is not None:
            self.__timeLeft = timeLeft
        else:
            self.__timeLeft = -1
        if self._state == State.BATTLELOADING and self._injectView is not None:
            self._injectView.setTimer(self.__timeLeft)
        return

    def hideCountdown(self, state, _):
        self.__timeLeft = 0
        if self._state == State.BATTLELOADING and self._injectView is not None:
            self._injectView.setTimer(self.__timeLeft)
        return

    def _dispose(self):
        self._destroyInjected()
        self.clear()
        self.__isViewActive = False
        super(PrebattleAmmunitionPanelInject, self)._dispose()

    def _onPopulate(self):
        pass

    def _hideSetupsView(self, useAnim=True):
        self.__isViewActive = False
        self.as_hideS(useAnim)

    def _makeInjectView(self, vehicle, *args):
        return PrebattleAmmunitionPanelView(vehicle, *args)

    def _addInjectContentListeners(self):
        self._injectView.onViewLoaded += self.__onViewLoaded
        self._injectView.onSwitchLayout += self.__onSwitchLayout

    def _removeInjectContentListeners(self):
        self._injectView.onSwitchLayout -= self.__onSwitchLayout
        self._injectView.onViewLoaded -= self.__onViewLoaded

    def _getShowShadows(self):
        return True

    def _switchLayout(self, groupID, layoutIdx):
        self.__sessionProvider.shared.prebattleSetups.switchLayout(groupID, layoutIdx)

    def _updateCurrentState(self, isArenaLoaded):
        self._state = State.PREBATTLE if isArenaLoaded else State.BATTLELOADING
        self.as_setIsInLoadingS(self._state == State.BATTLELOADING)

    def __onViewLoaded(self):
        self.__isViewLoaded = True

    def __onSwitchLayout(self, groupID, layoutIdx):
        self._switchLayout(groupID, layoutIdx)


class Comp7PrebattleAmmunitionPanelInject(PrebattleAmmunitionPanelInject):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        super(Comp7PrebattleAmmunitionPanelInject, self).__init__()
        self.__delayedNextShell, self.__delayedCurrShell = (None, None)
        self.__isFullStatsShown = False
        self.__closeOnFullStatsClose = False
        return None

    def setNextShellCD(self, shellCD):
        if self._state == State.PREBATTLE:
            super(Comp7PrebattleAmmunitionPanelInject, self).setNextShellCD(shellCD)
        else:
            self.__delayedNextShell = shellCD

    def setCurrentShellCD(self, shellCD):
        if self._state == State.PREBATTLE:
            super(Comp7PrebattleAmmunitionPanelInject, self).setCurrentShellCD(shellCD)
        else:
            self.__delayedCurrShell = shellCD

    def showSetupsView(self, vehicle, isArenaLoaded=False):
        if not isArenaLoaded:
            return
        super(Comp7PrebattleAmmunitionPanelInject, self).showSetupsView(vehicle, isArenaLoaded)

    def hideSetupsView(self):
        pass

    def stopSetupsSelection(self):
        pass

    def _populate(self):
        super(Comp7PrebattleAmmunitionPanelInject, self)._populate()
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        prbController = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prbController:
            prbController.onSelectionConfirmed += self.__onSelectionConfirmed
            prbController.onBattleStarted += self.__onBattleStarted
            prbController.onVehicleChanged += self.__onVehicleUpdated

    def _dispose(self):
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        prbController = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prbController:
            prbController.onSelectionConfirmed -= self.__onSelectionConfirmed
            prbController.onBattleStarted -= self.__onBattleStarted
            prbController.onVehicleChanged -= self.__onVehicleUpdated
        super(Comp7PrebattleAmmunitionPanelInject, self)._dispose()

    def _makeInjectView(self, vehicle, *args):
        return Comp7PrebattleAmmunitionPanelView(vehicle, *args)

    def _getShowShadows(self):
        return False

    def _switchLayout(self, groupID, layoutIdx):
        self.__sessionProvider.dynamic.comp7PrebattleSetup.switchPrebattleSetup(groupID, layoutIdx)

    def _updateCurrentState(self, isArenaLoaded):
        super(Comp7PrebattleAmmunitionPanelInject, self)._updateCurrentState(isArenaLoaded)
        if self._state == State.PREBATTLE:
            if not self.__sessionProvider.dynamic.comp7PrebattleSetup.isSelectionConfirmed():
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
        elif self.__isPrebattleSetupPossible() or not self.__sessionProvider.dynamic.comp7PrebattleSetup.isSelectionConfirmed():
            self.showSetupsView(vehicle, True)

    def __isPrebattleSetupPossible(self):
        vehicle = self.__sessionProvider.dynamic.comp7PrebattleSetup.getCurrentGUIVehicle()
        if vehicle is None:
            return False
        else:
            for groupID in TANK_SETUP_GROUPS.iterkeys():
                if vehicle.isSetupSwitchActive(groupID) and not vehicle.postProgression.isPrebattleSwitchDisabled(groupID):
                    return True

            return False

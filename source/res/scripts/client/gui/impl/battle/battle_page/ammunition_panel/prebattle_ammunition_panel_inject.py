# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_panel_inject.py
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.consumables.ammo_ctrl import IAmmoListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.prebattle_setups_ctrl import IPrebattleSetupsListener
from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_view import PrebattleAmmunitionPanelView
from gui.Scaleform.daapi.view.meta.PrebattleAmmunitionPanelViewMeta import PrebattleAmmunitionPanelViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import hasAliveInject
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_panel_view_model import State
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class PrebattleAmmunitionPanelInject(PrebattleAmmunitionPanelViewMeta, IPrebattleSetupsListener, IAmmoListener, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__currShellCD', '__nextShellCD', '__state', '__timeLeft')

    def __init__(self):
        super(PrebattleAmmunitionPanelInject, self).__init__()
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__state = State.BATTLELOADING
        self.__timeLeft = -1
        return

    def onViewIsHidden(self):
        self._destroyInjected()

    @hasAliveInject()
    def onArenaLoaded(self):
        self.__updateCurrentState(True)
        self._injectView.setTimer(-1)
        self._injectView.updateState(self.__state)
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)

    @hasAliveInject()
    def setCurrentShellCD(self, shellCD):
        self._injectView.setCurrentShellCD(shellCD)

    @hasAliveInject()
    def setNextShellCD(self, shellCD):
        self._injectView.setNextShellCD(shellCD)

    def showSetupsView(self, vehicle, isArenaLoaded=False):
        self.as_showS()
        self.__updateCurrentState(isArenaLoaded)
        if self.__state == State.BATTLELOADING:
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, enableAiming=False)
        self._createInjectView(vehicle, self.__currShellCD, self.__nextShellCD, self.__state)
        if self.__timeLeft and self.__state == State.BATTLELOADING:
            self._injectView.setTimer(self.__timeLeft)

    @hasAliveInject(deadUnexpected=True)
    def updateVehicleSetups(self, vehicle):
        self._injectView.updateViewVehicle(vehicle, False)

    @hasAliveInject(deadUnexpected=True)
    def stopSetupsSelection(self):
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)
        self._injectView.updateViewActive(False)

    @hasAliveInject(deadUnexpected=True)
    def hideSetupsView(self):
        self.as_hideS(True)

    def setCountdown(self, state, timeLeft):
        if state in (COUNTDOWN_STATE.START, COUNTDOWN_STATE.STOP) and timeLeft is not None:
            self.__timeLeft = timeLeft
        else:
            self.__timeLeft = -1
        if self.__state == State.BATTLELOADING and self._injectView is not None:
            self._injectView.setTimer(self.__timeLeft)
        return

    def hideCountdown(self, state, _):
        self.__timeLeft = 0
        if self.__state == State.BATTLELOADING and self._injectView is not None:
            self._injectView.setTimer(self.__timeLeft)
        return

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

    def __updateCurrentState(self, isArenaLoaded):
        if isArenaLoaded:
            self.__state = State.PREBATTLE
        else:
            self.__state = State.BATTLELOADING
        self.as_setIsInLoadingS(self.__state == State.BATTLELOADING)

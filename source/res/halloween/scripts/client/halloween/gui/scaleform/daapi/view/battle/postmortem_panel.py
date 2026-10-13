# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/postmortem_panel.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from halloween.gui.scaleform.daapi.view.meta.PostmortemPanelMeta import PostmortemPanelMeta
from HWArenaPhasesComponent import HWArenaPhasesComponent
from helpers.CallbackDelayer import CallbackDelayer
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.gui.hw_vehicle_role_helper import getVehicleRole
_ATTACK_REASON_MSG_TO_EVENT = {'DEATH_FROM_SHOT': 'HW_DEATH_FROM_SHOT',
 'DEATH_FROM_FIRE': 'HW_DEATH_FROM_FIRE',
 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT': 'HW_DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT'}

class HWPostmortemPanel(PostmortemPanelMeta):
    PHASE_DEATH_REASON = 'DEATH_FROM_PHASE_TIMER_SELF_SUICIDE'
    PHASE_DEATH_REASON_LATE = 'DEATH_FROM_PHASE_TIMER_SELF_SUICIDE_LATE'
    PHASE_DEATH_REASON_FINAL = 'DEATH_FROM_PHASE_TIMER_SELF_SUICIDE_FINAL'
    TICK_RATE = 1
    __slots__ = ('_callbacks', '__collectorIsFull')

    def __init__(self):
        super(HWPostmortemPanel, self).__init__()
        self.__collectorIsFull = None
        self._callbacks = CallbackDelayer()
        return

    @property
    def _isRespawnEnabledOnServer(self):
        arenaPhasesComponent = HWArenaPhasesComponent.getInstance()
        return arenaPhasesComponent and arenaPhasesComponent.isRespawnEnabled

    @property
    def _isLastPhase(self):
        arenaPhasesComponent = HWArenaPhasesComponent.getInstance()
        return arenaPhasesComponent.isLastPhase()

    def _populate(self):
        super(HWPostmortemPanel, self)._populate()
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSoulCollectorProgress += self.__onSoulCollectorProgress

    def _dispose(self):
        self._callbacks.destroy()
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSoulCollectorProgress -= self.__onSoulCollectorProgress
        super(HWPostmortemPanel, self)._dispose()

    def _showOwnDeathInfo(self):
        super(HWPostmortemPanel, self)._showOwnDeathInfo()
        self._callbacks.delayCallback(0, self._updateDeathInfo)

    def _showPlayerInfo(self):
        super(HWPostmortemPanel, self)._showPlayerInfo()
        self._callbacks.clearCallbacks()
        self.as_showRespawnIconS(False)
        self.as_setHintTitleS('')
        self.as_setHintDescrS('')

    def _updateDeathInfo(self):
        postmortemPanel = R.strings.halloween_battle.postmortemPanel
        canRespawn = self.__canRespawn()
        aliveTeamates = self.__hasAliveTeammate()
        showSpectatorPanel = True
        canExit = False
        if not canRespawn:
            self.as_showDeadReasonS()
            self.as_setHintDescrS('')
            if not self._isRespawnEnabledOnServer and aliveTeamates:
                self.as_setHintTitleS(backport.text(postmortemPanel.lastPhase.title()), False)
                canExit = True
            else:
                self.as_setHintTitleS('', False)
                self.as_setCanExitS(False)
                showSpectatorPanel = False
        else:
            self.as_setHintTitleS(backport.text(postmortemPanel.doNotLeaveGame.title()), True)
            self.as_setHintDescrS(backport.text(postmortemPanel.doNotLeaveGame.desc()))
        self.as_showSpectatorPanelS(showSpectatorPanel)
        if showSpectatorPanel:
            self.as_setCanExitS(canExit)
        self.as_showRespawnIconS(canRespawn)
        isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
        return self.TICK_RATE if isInPostmortem else None

    def _prepareMessage(self, code, killerVehID, device=None):
        code = _ATTACK_REASON_MSG_TO_EVENT.get(code, code)
        if code == self.PHASE_DEATH_REASON:
            if self._isLastPhase:
                code = self.PHASE_DEATH_REASON_FINAL
            elif not self.__collectorIsFull:
                code = self.PHASE_DEATH_REASON_LATE
        super(HWPostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def _makeKillerVO(self, vInfoVO):
        vo = super(HWPostmortemPanel, self)._makeKillerVO(vInfoVO)
        del vo['userName']
        return vo

    def _setDeadReasonInfo(self, vInfoVO, reason, showVehicle, vehLvl, vehImg, vehClass, vehName, killerUserVO):
        if vInfoVO is not None:
            role = getVehicleRole(vInfoVO.vehicleType)
            if role is not None:
                vehClass = backport.image(R.images.halloween.gui.maps.icons.vehicleTypes.white.dyn(role)())
            if vInfoVO.isEnemy():
                vehName = vInfoVO.vehicleType.name
        super(HWPostmortemPanel, self)._setDeadReasonInfo(vInfoVO, reason, showVehicle, vehLvl, vehImg, vehClass, vehName, killerUserVO)
        return

    def __canRespawn(self):
        isAliveAnyPlayer = self.__hasAliveTeammate()
        return isAliveAnyPlayer and self._isRespawnEnabledOnServer

    def __hasAliveTeammate(self):
        arenaDP = self.sessionProvider.getArenaDP()
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        return any((vInfo.isAlive() for vInfo in arenaDP.getVehiclesInfoIterator() if vInfo.vehicleID != playerVehicleID and vInfo.player.accountDBID > 0 and vInfo.team == arenaDP.getAllyTeams()[0]))

    def __onSoulCollectorProgress(self, collected, capacity, isFull, isCampActivated):
        self.__collectorIsFull = isFull

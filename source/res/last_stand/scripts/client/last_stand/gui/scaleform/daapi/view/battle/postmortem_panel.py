# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/postmortem_panel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from last_stand.gui.scaleform.daapi.view.meta.PostmortemPanelMeta import PostmortemPanelMeta
from LSArenaPhasesComponent import LSArenaPhasesComponent
from helpers.CallbackDelayer import CallbackDelayer
from last_stand.gui.ls_vehicle_role_helper import getVehicleRole
_ATTACK_REASON_MSG_TO_EVENT = {'DEATH_FROM_SHOT': 'DEATH_FROM_LS_SHOT',
 'DEATH_FROM_FIRE': 'DEATH_FROM_LS_FIRE',
 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT': 'DEATH_FROM_LS_DEVICE_EXPLOSION_AT_SHOT'}

class LSPostmortemPanel(PostmortemPanelMeta):
    TICK_RATE = 1
    RESPAWN_TITLE = R.strings.last_stand_battle.postmortemPanel.doNotLeaveGame.title()
    RESPAWN_INFO = R.strings.last_stand_battle.postmortemPanel.doNotLeaveGame.desc()
    __slots__ = ('_callbacks',)

    def __init__(self):
        super(LSPostmortemPanel, self).__init__()
        self._callbacks = CallbackDelayer()

    @property
    def _isRespawnEnabledOnServer(self):
        arenaPhasesComponent = LSArenaPhasesComponent.getInstance()
        return arenaPhasesComponent and arenaPhasesComponent.isRespawnEnabled

    @property
    def _isLastPhase(self):
        arenaPhasesComponent = LSArenaPhasesComponent.getInstance()
        return arenaPhasesComponent.isLastPhase()

    def _dispose(self):
        self._callbacks.destroy()
        super(LSPostmortemPanel, self)._dispose()

    def _showOwnDeathInfo(self):
        super(LSPostmortemPanel, self)._showOwnDeathInfo()
        self._callbacks.delayCallback(0, self._updateDeathInfo)

    def _showPlayerInfo(self):
        super(LSPostmortemPanel, self)._showPlayerInfo()
        self._callbacks.clearCallbacks()
        self.as_showRespawnIconS(False)
        self.as_setHintTitleS('')
        self.as_setHintDescrS('')

    def _updateDeathInfo(self):
        postmortemPanel = R.strings.last_stand_battle.postmortemPanel
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
            self.as_setHintTitleS(backport.text(self.RESPAWN_TITLE), True)
            self.as_setHintDescrS(backport.text(self.RESPAWN_INFO))
        self.as_showSpectatorPanelS(showSpectatorPanel)
        if showSpectatorPanel:
            self.as_setCanExitS(canExit)
        self.as_showRespawnIconS(canRespawn)
        isInPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
        return self.TICK_RATE if isInPostmortem else None

    def _prepareMessage(self, code, killerVehID, device=None):
        code = _ATTACK_REASON_MSG_TO_EVENT.get(code) or code
        super(LSPostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def _makeKillerVO(self, vInfoVO):
        vo = super(LSPostmortemPanel, self)._makeKillerVO(vInfoVO)
        del vo['userName']
        return vo

    def _setDeadReasonInfo(self, vInfoVO, reason, showVehicle, vehLvl, vehImg, vehClass, vehName, killerUserVO):
        if vInfoVO is not None:
            role = getVehicleRole(vInfoVO.vehicleType)
            if role is not None:
                vehClass = backport.image(R.images.last_stand.gui.maps.icons.vehicleTypes.white.dyn(role)())
            if vInfoVO.isEnemy():
                vehName = vInfoVO.vehicleType.name
        super(LSPostmortemPanel, self)._setDeadReasonInfo(vInfoVO, reason, showVehicle, vehLvl, vehImg, vehClass, vehName, killerUserVO)
        return

    def __canRespawn(self):
        isAliveAnyPlayer = self.__hasAliveTeammate()
        return isAliveAnyPlayer and self._isRespawnEnabledOnServer

    def __hasAliveTeammate(self):
        arenaDP = self.sessionProvider.getArenaDP()
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        return any((vInfo.isAlive() for vInfo in arenaDP.getVehiclesInfoIterator() if vInfo.vehicleID != playerVehicleID and vInfo.player.accountDBID > 0 and vInfo.team == arenaDP.getAllyTeams()[0]))

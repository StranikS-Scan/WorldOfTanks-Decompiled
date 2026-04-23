# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/postmortem_panel.py
import BigWorld
from constants import ARENA_PERIOD
from gui.doc_loaders import messages_panel_reader
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import Vehicle
from historical_battles.gui.Scaleform.daapi.view.meta.HBPostmortemPanelMeta import HBPostmortemPanelMeta
from HBAvatarRespawnComponent import HBAvatarRespawnComponent
_POSTMORTEM_PANEL_SETTINGS_PATH = 'historical_battles/gui/postmortem_panel.xml'
_ATTACK_REASON_MSG_TO_EVENT = {'DEATH_FROM_SHOT': 'EVENT_DEATH_FROM_SHOT',
 'DEATH_FROM_DEATH_ZONE_SELF_SUICIDE': 'EVENT_DEATH_FROM_DEATH_ZONE_SELF_SUICIDE',
 'DEATH_FROM_DEATH_ZONE_ENEMY_SELF': 'EVENT_DEATH_FROM_DEATH_ZONE_ENEMY_SELF',
 'DEATH_FROM_DEATH_ZONE_ALLY_SELF': 'EVENT_DEATH_FROM_DEATH_ZONE_ALLY_SELF',
 'DEATH_FROM_FIRE': 'EVENT_DEATH_FROM_FIRE',
 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT': 'EVENT_DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT'}

class HBPostmortemPanel(HBPostmortemPanelMeta):

    def _populate(self):
        super(HBPostmortemPanel, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_POSTMORTEM_PANEL_SETTINGS_PATH)
        self._messages.update(messages)

    def _addGameListeners(self):
        super(HBPostmortemPanel, self)._addGameListeners()
        HBAvatarRespawnComponent.onDeath += self._onDeath
        HBAvatarRespawnComponent.onRespawnExhausted += self.__onPlayerLifecycleDataUpdated
        self.__onPlayerLifecycleDataUpdated()

    def _onDeath(self, spawnTime):
        secondsUntilRespawn = spawnTime - BigWorld.serverTime()
        self.as_setTimerS(secondsUntilRespawn)

    def _prepareMessage(self, code, killerVehID, device=None):
        code = _ATTACK_REASON_MSG_TO_EVENT.get(code, code)
        super(HBPostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def _deathInfoReceived(self):
        self.__onPlayerLifecycleDataUpdated()
        super(HBPostmortemPanel, self)._deathInfoReceived()

    def __onPlayerLifecycleDataUpdated(self):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE:
            return
        messagesAcc = R.strings.hb_battle.postmortem_panel
        if not self._hasAvailableVehicles():
            self.as_setHintTitleS(backport.text(messagesAcc.no_respawns_message_title()))
            self.as_setHintDescrS(backport.text(messagesAcc.no_respawns_message_descr()))
            self.as_setCanExitS(True)
            self.as_setIsLockedS(True)
        else:
            self.as_setHintTitleS(backport.text(messagesAcc.respawn_timer_title()))
            self.as_setHintDescrS('')
            self.as_setCanExitS(False)
            self.as_setIsLockedS(False)

    def _hasAvailableVehicles(self):
        tankSetMask = BigWorld.player().HBAvatarRespawnComponent.tankSetMask
        return any(tankSetMask)

    def _removeGameListeners(self):
        HBAvatarRespawnComponent.onDeath -= self._onDeath
        HBAvatarRespawnComponent.onRespawnExhausted -= self.__onPlayerLifecycleDataUpdated
        super(HBPostmortemPanel, self)._removeGameListeners()

    @staticmethod
    def getVehClass(vInfoVO, killerVehID):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            role = arena.arenaInfo.vehicleRoleArenaComponent.getRole(killerVehID)
            if role:
                return arena.arenaInfo.vehicleRoleArenaComponent.getPostmortemIcon(killerVehID)
        return Vehicle.getTypeBigIconPath(vInfoVO.classTag)

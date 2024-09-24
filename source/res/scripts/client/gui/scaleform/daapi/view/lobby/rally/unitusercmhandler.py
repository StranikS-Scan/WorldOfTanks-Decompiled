# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/UnitUserCMHandler.py
from account_helpers import getAccountDatabaseID
from adisp import adisp_process
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.entities.base.unit.ctx import KickPlayerUnitCtx, GiveLeadershipUnitCtx
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.stronghold.unit.ctx import GiveEquipmentCommanderCtx
from gui.prb_control.items.stronghold_items import BOOST_TYPE, SUPPORT_TYPE, ARTILLERY_COMMANDER, INSPIRE_COMMANDER
from gui.shared.system_factory import registerLobbyContexMenuHandler
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
KICK_FROM_UNIT = 'kickPlayerFromUnit'
GIVE_LEADERSHIP = 'giveLeadership'
TAKE_LEADERSHIP = 'takeLeadership'
TAKE_ARTILLERY_EQUIPMENT_COMMANDER = 'takeArtilleryEquipmentCommander'
GIVE_ARTILLERY_EQUIPMENT_COMMANDER = 'giveArtilleryEquipmentCommander'
TAKE_INSPIRE_EQUIPMENT_COMMANDER = 'takeInspireEquipmentCommander'
GIVE_INSPIRE_EQUIPMENT_COMMANDER = 'giveInspireEquipmentCommander'

def giveLeadership(cm):
    cm.giveLeadership(cm.databaseID)


def takeLeadership(cm):
    cm.takeLeadership()


def kickPlayerFromUnit(cm):
    cm.kickPlayerFromUnit(cm.databaseID)


def giveArtilleryEquipmentCommander(cm):
    cm.giveEquipmentCommander(cm.databaseID, ARTILLERY_COMMANDER)


def takeArtilleryEquipmentCommander(cm):
    cm.giveEquipmentCommander(None, ARTILLERY_COMMANDER)
    return


def giveInspireEquipmentCommander(cm):
    cm.giveEquipmentCommander(cm.databaseID, INSPIRE_COMMANDER)


def takeInspireEquipmentCommander(cm):
    cm.giveEquipmentCommander(None, INSPIRE_COMMANDER)
    return


registerLobbyContexMenuHandler(KICK_FROM_UNIT, kickPlayerFromUnit)
registerLobbyContexMenuHandler(GIVE_LEADERSHIP, giveLeadership)
registerLobbyContexMenuHandler(TAKE_LEADERSHIP, takeLeadership)
registerLobbyContexMenuHandler(TAKE_ARTILLERY_EQUIPMENT_COMMANDER, takeArtilleryEquipmentCommander)
registerLobbyContexMenuHandler(GIVE_ARTILLERY_EQUIPMENT_COMMANDER, giveArtilleryEquipmentCommander)
registerLobbyContexMenuHandler(TAKE_INSPIRE_EQUIPMENT_COMMANDER, takeInspireEquipmentCommander)
registerLobbyContexMenuHandler(GIVE_INSPIRE_EQUIPMENT_COMMANDER, giveInspireEquipmentCommander)

class UnitUserCMHandler(BaseUserCMHandler, IGlobalListener):

    def __init__(self, cmProxy, ctx=None):
        super(UnitUserCMHandler, self).__init__(cmProxy, ctx)
        self.startPrbListening()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def isSquadCreator(self):
        return self.prbEntity.isCommander()

    def fini(self):
        self.stopPrbListening()
        super(UnitUserCMHandler, self).fini()

    def onUnitPlayerRemoved(self, pInfo):
        self.onContextMenuHide()

    def onUnitMembersListChanged(self):
        self.onContextMenuHide()

    def onCommanderIsReady(self, isReady):
        self.onContextMenuHide()

    @adisp_process
    def kickPlayerFromUnit(self, databaseID):
        yield self.prbDispatcher.sendPrbRequest(KickPlayerUnitCtx(databaseID, 'prebattle/kick'))

    @adisp_process
    def giveLeadership(self, databaseID):
        yield self.prbDispatcher.sendPrbRequest(GiveLeadershipUnitCtx(databaseID, 'prebattle/giveLeadership'))

    @adisp_process
    def takeLeadership(self):
        yield self.prbDispatcher.sendPrbRequest(GiveLeadershipUnitCtx(getAccountDatabaseID(), 'prebattle/takeLeadership'))

    @adisp_process
    def giveEquipmentCommander(self, databaseID, role):
        yield self.prbDispatcher.sendPrbRequest(GiveEquipmentCommanderCtx(databaseID, role, 'prebattle/giveEquipmentCommander'))

    def _addMutedInfo(self, option, userCMInfo):
        muted = USER.UNSET_MUTED if userCMInfo.isMuted else USER.SET_MUTED
        if not userCMInfo.isIgnored:
            if self.bwProto.voipController.isVOIPEnabled():
                option.append(self._makeItem(muted, MENU.contextmenu(muted)))
        return option

    def _addSquadInfo(self, options, userCMInfo):
        return super(UnitUserCMHandler, self)._addSquadInfo(options, userCMInfo) if self.prbEntity.getEntityType() not in PREBATTLE_TYPE.SQUAD_PREBATTLES else options

    def _addStrongholdsInfo(self, userCMInfo):
        if self.prbEntity.getEntityType() != PREBATTLE_TYPE.STRONGHOLD:
            return []
        options = []
        if self._canTakeEquipmentCommander(SUPPORT_TYPE):
            options.append(self._makeItem(TAKE_ARTILLERY_EQUIPMENT_COMMANDER, MENU.contextmenu(TAKE_ARTILLERY_EQUIPMENT_COMMANDER)))
        if self._canGiveEquipmentCommander(SUPPORT_TYPE):
            options.append(self._makeItem(GIVE_ARTILLERY_EQUIPMENT_COMMANDER, MENU.contextmenu(GIVE_ARTILLERY_EQUIPMENT_COMMANDER)))
        if self._canTakeEquipmentCommander(BOOST_TYPE):
            options.append(self._makeItem(TAKE_INSPIRE_EQUIPMENT_COMMANDER, MENU.contextmenu(TAKE_INSPIRE_EQUIPMENT_COMMANDER)))
        if self._canGiveEquipmentCommander(BOOST_TYPE):
            options.append(self._makeItem(GIVE_INSPIRE_EQUIPMENT_COMMANDER, MENU.contextmenu(GIVE_INSPIRE_EQUIPMENT_COMMANDER)))
        return options

    def _addPrebattleInfo(self, options, userCMInfo):
        if self._canKick():
            options.append(self._makeItem(KICK_FROM_UNIT, MENU.contextmenu(KICK_FROM_UNIT)))
        if self._canGiveLeadership():
            options.append(self._makeItem(GIVE_LEADERSHIP, MENU.contextmenu(GIVE_LEADERSHIP)))
        if self._canTakeLeadership():
            options.append(self._makeItem(TAKE_LEADERSHIP, MENU.contextmenu(TAKE_LEADERSHIP)))
        if self.prbEntity.getEntityType() == PREBATTLE_TYPE.STRONGHOLD:
            options.extend(self._addStrongholdsInfo(userCMInfo))
        return options

    def _canKick(self):
        return self.prbEntity.getPermissions().canKick()

    def _canGiveEquipmentCommander(self, equipmentType):
        unitEntity = self.prbEntity
        myPermissions = unitEntity.getPermissions()
        if not myPermissions.canChangeExtraEquipmentRole():
            return False
        permissions = unitEntity.getPermissions(dbID=self.databaseID)
        pInfo = unitEntity.getPlayerInfo(dbID=self.databaseID)
        return pInfo.isInSlot and not permissions.isEquipmentCommander(equipmentType)

    def _canTakeEquipmentCommander(self, equipmentType):
        unitEntity = self.prbEntity
        myPermissions = unitEntity.getPermissions()
        pInfo = unitEntity.getPlayerInfo(dbID=self.databaseID)
        permissions = unitEntity.getPermissions(dbID=self.databaseID)
        return myPermissions.canChangeExtraEquipmentRole() and pInfo.isInSlot and permissions.isEquipmentCommander(equipmentType)

    def _canGiveLeadership(self):
        unitEntity = self.prbEntity
        myPermissions = unitEntity.getPermissions()
        myPInfo = unitEntity.getPlayerInfo()
        permissions = unitEntity.getPermissions(dbID=self.databaseID)
        pInfo = unitEntity.getPlayerInfo(dbID=self.databaseID)
        return myPInfo.isCommander() and pInfo.isInSlot and myPermissions.canChangeLeadership() and permissions.canLead() and not pInfo.isLegionary()

    def _canTakeLeadership(self):
        unitEntity = self.prbEntity
        myPermissions = unitEntity.getPermissions()
        pInfo = unitEntity.getPlayerInfo(dbID=self.databaseID)
        return pInfo.isCommander() and myPermissions.canStealLeadership() and myPermissions.canLead()

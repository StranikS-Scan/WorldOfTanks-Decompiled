# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/UnitUserCMHandler.py
from account_helpers import getAccountDatabaseID
from adisp import process
from constants import PREBATTLE_TYPE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler, USER
from gui.prb_control.context import unit_ctx
from gui.prb_control.prb_helpers import UnitListener
KICK_FROM_UNIT = 'kickPlayerFromUnit'
GIVE_LEADERSHIP = 'giveLeadership'
TAKE_LEADERSHIP = 'takeLeadership'

class UnitUserCMHandler(BaseUserCMHandler, UnitListener):

    def __init__(self, cmProxy, ctx = None):
        super(UnitUserCMHandler, self).__init__(cmProxy, ctx)
        self.startUnitListening()

    def fini(self):
        self.stopUnitListening()
        super(UnitUserCMHandler, self).fini()

    def onUnitPlayerRemoved(self, pInfo):
        self.onContextMenuHide()

    def onUnitMembersListChanged(self):
        self.onContextMenuHide()

    def giveLeadership(self):
        self._giveLeadership(self.databaseID)

    def takeLeadership(self):
        self._takeLeadership()

    def kickPlayerFromUnit(self):
        self._kickPlayerFromUnit(self.databaseID)

    def _addMutedInfo(self, option, userCMInfo):
        muted = USER.UNSET_MUTED if userCMInfo.isMuted else USER.SET_MUTED
        if not userCMInfo.isIgnored and self.app.voiceChatManager.isVOIPEnabled():
            option.append(self._makeItem(muted, MENU.contextmenu(muted)))
        return option

    def _addSquadInfo(self, options, isIgnored):
        if self.unitFunctional.getEntityType() != PREBATTLE_TYPE.SQUAD or not self.unitFunctional.isCreator():
            return super(UnitUserCMHandler, self)._addSquadInfo(options, isIgnored)
        return options

    def _addPrebattleInfo(self, options, userCMInfo):
        if self.unitFunctional.getPermissions().canKick():
            options.append(self._makeItem(KICK_FROM_UNIT, MENU.contextmenu(KICK_FROM_UNIT)))
        if self._canGiveLeadership():
            options.append(self._makeItem(GIVE_LEADERSHIP, MENU.contextmenu(GIVE_LEADERSHIP)))
        if self._canTakeLeadership():
            options.append(self._makeItem(TAKE_LEADERSHIP, MENU.contextmenu(TAKE_LEADERSHIP)))
        return options

    def _canGiveLeadership(self):
        unitFunctional = self.unitFunctional
        myPermissions = unitFunctional.getPermissions()
        myPInfo = unitFunctional.getPlayerInfo()
        permissions = unitFunctional.getPermissions(dbID=self.databaseID)
        pInfo = unitFunctional.getPlayerInfo(dbID=self.databaseID)
        return myPInfo.isCreator() and pInfo.isInSlot and myPermissions.canChangeLeadership() and permissions.canLead()

    def _canTakeLeadership(self):
        unitFunctional = self.unitFunctional
        myPermissions = unitFunctional.getPermissions()
        pInfo = unitFunctional.getPlayerInfo(dbID=self.databaseID)
        return pInfo.isCreator() and myPermissions.canStealLeadership() and myPermissions.canLead()

    def _getHandlers(self):
        handlers = super(UnitUserCMHandler, self)._getHandlers()
        handlers.update({KICK_FROM_UNIT: 'kickPlayerFromUnit',
         GIVE_LEADERSHIP: 'giveLeadership',
         TAKE_LEADERSHIP: 'takeLeadership'})
        return handlers

    @process
    def _kickPlayerFromUnit(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.KickPlayerCtx(databaseID, 'prebattle/kick'))

    @process
    def _giveLeadership(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.GiveLeadershipCtx(databaseID, 'prebattle/giveLeadership'))

    @process
    def _takeLeadership(self):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.GiveLeadershipCtx(getAccountDatabaseID(), 'prebattle/takeLeadership'))

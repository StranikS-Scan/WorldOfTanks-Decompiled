# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/UnitUserCMHandler.py
from adisp import process
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler, USER
from gui.prb_control.context import unit_ctx
from gui.prb_control.prb_helpers import unitFunctionalProperty, UnitListener
KICK_FROM_UNIT = 'kickPlayerFromUnit'
GIVE_LEADERSHIP = 'giveLeadership'

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

    def kickPlayerFromUnit(self):
        self._kickPlayerFromUnit(self.databaseID)

    def _addMutedInfo(self, option, userCMInfo):
        muted = USER.UNSET_MUTED if userCMInfo.isMuted else USER.SET_MUTED
        if not userCMInfo.isIgnored and self.app.voiceChatManager.isVOIPEnabled():
            option.append(self._makeItem(muted, MENU.contextmenu(muted)))
        return option

    def _addPrebattleInfo(self, options, userCMInfo):
        if self.unitFunctional.getPermissions().canKick():
            options.append(self._makeItem(KICK_FROM_UNIT, MENU.contextmenu(KICK_FROM_UNIT)))
        if self._canGiveLeadership():
            options.append(self._makeItem(GIVE_LEADERSHIP, MENU.contextmenu(GIVE_LEADERSHIP)))
        return options

    def _canGiveLeadership(self):
        pInfo = self.unitFunctional.getPlayerInfo(dbID=self.databaseID)
        return not pInfo.isLegionary() and not pInfo.isCreator() and pInfo.isInSlot and self.unitFunctional.getPermissions().canChangeLeadership()

    def _getHandlers(self):
        handlers = super(UnitUserCMHandler, self)._getHandlers()
        handlers.update({KICK_FROM_UNIT: 'kickPlayerFromUnit',
         GIVE_LEADERSHIP: 'giveLeadership'})
        return handlers

    @process
    def _kickPlayerFromUnit(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.KickPlayerCtx(databaseID, 'prebattle/kick'))

    @process
    def _giveLeadership(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.GiveLeadershipCtx(databaseID, 'prebattle/giveLeadership'))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/stats_exchage/player.py
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS
from gui.battle_control.arena_info.settings import PLAYER_STATUS

class PlayerStatusComponent(broker.StatusComponent):

    def __init__(self):
        super(PlayerStatusComponent, self).__init__(status=PLAYER_STATUS.DEFAULT)


class InvitationStatusComponent(broker.StatusComponent):

    def __init__(self):
        super(InvitationStatusComponent, self).__init__(status=INVITATION_DELIVERY_STATUS.NONE)


class InvitationsExchangeBlock(broker.ExchangeBlock):

    def __init__(self):
        super(InvitationsExchangeBlock, self).__init__(InvitationStatusComponent())

    def addSortIDs(self, arenaDP, *flags):
        raise UserWarning('This method should not be reached in this context')

    def addTotalStats(self, stats):
        raise UserWarning('This method should not be reached in this context')


class UserTagsItemData(broker.VehicleComponent):
    __slots__ = ('_ctx', '_accountDBID', '_igrType', '_tags')

    def __init__(self, ctx):
        super(UserTagsItemData, self).__init__()
        self._ctx = ctx
        self._accountDBID = 0
        self._igrType = 0
        self._tags = None
        return

    def clear(self):
        self._accountDBID = 0
        self._igrType = 0
        self._tags = None
        super(UserTagsItemData, self).clear()
        return

    def destroy(self):
        self._ctx = None
        super(UserTagsItemData, self).destroy()
        return

    def get(self, forced=False):
        if self._tags is None:
            tags = self._ctx.getUserTags(self._accountDBID, self._igrType)
        else:
            tags = self._ctx.addTagByIGRType(self._tags, self._igrType)
        return {'isEnemy': self._isEnemy,
         'vehicleID': self._vehicleID,
         'userTags': tags} if forced or tags else {}

    def addVehicleInfo(self, vInfoVO):
        playerVO = vInfoVO.player
        self._accountDBID = playerVO.accountDBID
        self._igrType = playerVO.igrType
        self._vehicleID = vInfoVO.vehicleID

    def addUserTags(self, tags):
        self._tags = tags


class UsersTagsListExchangeData(broker.ExchangeBlock):

    def __init__(self, ctx):
        super(UsersTagsListExchangeData, self).__init__(UserTagsItemData(ctx))

    def addSortIDs(self, arenaDP, *flags):
        raise UserWarning('This method should not be reached in this context')

    def addTotalStats(self, stats):
        raise UserWarning('This method should not be reached in this context')

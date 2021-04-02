# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale_tournament/legacy/entity.py
from helpers import dependency
from gui.prb_control import prb_getters
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.entities.base.legacy.entity import LegacyEntryPoint
from skeletons.gui.game_control import IBattleRoyaleTournamentController
from gui.prb_control.items import prb_seqs

class BattleRoyaleTournamentEntryPoint(LegacyEntryPoint):
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)

    def __init__(self):
        super(BattleRoyaleTournamentEntryPoint, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE)

    def join(self, ctx, callback=None):
        prbID = int(ctx.getID())
        item = prb_seqs.AutoInviteItem(prbID, **prb_getters.getPrebattleAutoInvites().get(prbID, {}))
        self.__battleRoyaleTournamentController.join(item.addInfo)

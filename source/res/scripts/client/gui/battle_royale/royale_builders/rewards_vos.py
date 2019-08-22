# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/rewards_vos.py
import typing
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_models import Title

def getTitleRewardsVO(title, bonuses, maxTitleID):
    if title.getID() == maxTitleID:
        awardState = BATTLEROYALE_CONSTS.REWARDS_TITLE_CURRENT
    elif title.getID() == maxTitleID + 1:
        awardState = BATTLEROYALE_CONSTS.REWARDS_TITLE_NEXT
    elif title.getID() < maxTitleID:
        awardState = BATTLEROYALE_CONSTS.REWARDS_TITLE_RECEIVED
    else:
        awardState = BATTLEROYALE_CONSTS.REWARDS_TITLE_LOCKED
    return {'state': awardState,
     'titleID': title.getID(),
     'levelStr': str(title.getID()),
     'bonuses': bonuses}

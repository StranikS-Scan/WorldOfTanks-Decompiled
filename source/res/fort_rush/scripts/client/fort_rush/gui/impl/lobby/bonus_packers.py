# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/bonus_packers.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.shared.missions.packers.bonus import BonusUIPacker, TokenBonusUIPacker, getDailyMissionsMapping
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from fort_rush.skeletons.battle_controller import IFortRushBattleController
if TYPE_CHECKING:
    from gui.impl.backport.backport_tooltip import TooltipData
    from gui.server_events.bonuses import TokensBonus
    from typing import Any
_logger = logging.getLogger(__name__)

class FortRushTokenBonusUIPacker(TokenBonusUIPacker):
    _FORT_RUSH_PROGRESSION_TOKEN_SOURCE = 'fort_rush_points'
    __ctrl = dependency.descriptor(IFortRushBattleController)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        progressionToken = cls.__ctrl.getConfig().baseProgressionToken
        return progressionToken if tokenID.startswith(progressionToken) else super(FortRushTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(FortRushTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers[cls.__ctrl.getConfig().baseProgressionToken] = cls.__packProgressionToken
        return packers

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(FortRushTokenBonusUIPacker, cls)._getTooltipsPackers()
        packers[cls.__ctrl.getConfig().baseProgressionToken] = cls.__getProgressionTokenTooltip
        return packers

    @classmethod
    def __packProgressionToken(cls, model, bonus, complexToken, token):
        model.setValue(str(token.count))
        iconPath = R.images.fort_rush.gui.maps.icons.progression_view.quest_icons.dyn(cls._FORT_RUSH_PROGRESSION_TOKEN_SOURCE)()
        model.setIconSmall(backport.image(iconPath))
        model.setIconBig(backport.image(iconPath))
        return model

    @classmethod
    def __getProgressionTokenTooltip(cls, *_):
        return createTooltipData(makeTooltip(header=backport.text(R.strings.fort_rush.tooltips.eventPoints.header()), body=backport.text(R.strings.fort_rush.tooltips.eventPoints.body())))


def getFortRushMissionBonusPacker():
    mapping = getDailyMissionsMapping()
    mapping['battleToken'] = FortRushTokenBonusUIPacker()
    return BonusUIPacker(mapping)

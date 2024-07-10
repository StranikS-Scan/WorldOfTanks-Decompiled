# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/squad_bonus_tooltip_content.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.squad_bonus_tooltip_content_model import SquadBonusTooltipContentModel, SquadBonusTooltipType
from gui.impl.lobby.platoon.platoon_helpers import BonusState
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

def _floatToPercents(value):
    return int(value * 100)


def _getHeaderInfoTooltipType(bonusState):
    tooltipType = SquadBonusTooltipType.SIMPLE
    if BonusState.hasAnyBitSet(bonusState, BonusState.SQUAD_CREDITS_BONUS | BonusState.PREM_CREDITS_BONUS):
        tooltipType = SquadBonusTooltipType.COMMON
    elif BonusState.hasAnyBitSet(bonusState, BonusState.XP_BONUS):
        tooltipType = SquadBonusTooltipType.SIMPLEWITHBONUS
    return tooltipType


class SquadBonusTooltipContent(ViewImpl):
    __slots__ = ()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.premacc.tooltips.SquadBonusTooltip(), model=SquadBonusTooltipContentModel(), args=args, kwargs=kwargs)
        super(SquadBonusTooltipContent, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return super(SquadBonusTooltipContent, self).getViewModel()

    def _onLoading(self, battleType='', bonusState=BonusState.NO_BONUS, *args, **kwargs):
        tooltipType = _getHeaderInfoTooltipType(bonusState)
        isCommon = tooltipType == SquadBonusTooltipType.COMMON
        with self.viewModel.transaction() as model:
            if battleType:
                model.setBattleType(battleType)
            model.setType(tooltipType)
            if isCommon:
                creditsBonuses = self.__lobbyContext.getServerSettings().squadPremiumBonus
                model.setCreditsBonusWithPremium(_floatToPercents(creditsBonuses.ownCredits))
                model.setCreditsBonusWithoutPremium(_floatToPercents(creditsBonuses.mateCredits))
            if BonusState.hasAnyBitSet(bonusState, BonusState.XP_BONUS):
                model.setExperienceBonus(_floatToPercents(self.__eventsCache.getSquadXPFactor()))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/squad_bonus_tooltip_content.py
from frameworks.wulf import ViewFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.squad_bonus_tooltip_content_model import SquadBonusTooltipContentModel
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

def _floatToPercents(value):
    return int(value * 100)


class SquadBonusTooltipContent(View):
    __slots__ = ()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.premacc.squad_bonus_tooltip_content.SquadBonusTooltipContent())
        settings.flags = ViewFlags.COMPONENT
        settings.model = SquadBonusTooltipContentModel()
        super(SquadBonusTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SquadBonusTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SquadBonusTooltipContent, self)._initialize(*args, **kwargs)
        creditsBonuses = self.__lobbyContext.getServerSettings().squadPremiumBonus
        with self.viewModel.transaction() as model:
            model.setCreditsBonusWithPremium(_floatToPercents(creditsBonuses.ownCredits))
            model.setCreditsBonusWithoutPremium(_floatToPercents(creditsBonuses.mateCredits))
            model.setExperienceBonus(_floatToPercents(self.__eventsCache.getSquadXPFactor()))


class Comp7SquadBonusTooltipContent(SquadBonusTooltipContent):

    def __init__(self, battleType=None):
        self.__battleType = battleType
        super(Comp7SquadBonusTooltipContent, self).__init__()

    def _initialize(self, *args, **kwargs):
        super(Comp7SquadBonusTooltipContent, self)._initialize(*args, **kwargs)
        with self.viewModel.transaction() as model:
            if self.__battleType:
                model.setBattleType(self.__battleType)

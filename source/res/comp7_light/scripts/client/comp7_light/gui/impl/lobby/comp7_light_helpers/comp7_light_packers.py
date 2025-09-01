# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/comp7_light_helpers/comp7_light_packers.py
import typing
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from constants import EVENT_TYPE
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.formatters import COMPLEX_TOKEN
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, TokenBonusUIPacker, getLocalizedBonusName
from gui.shared.missions.packers.events import DailyQuestUIDataPacker, packQuestBonusModelAndTooltipData
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.server_events.bonuses import CurrenciesBonus

def getComp7LightBonusPacker():
    packer = getBattlePassBonusPacker()
    packer.getPackers().update({'battleToken': Comp7LightTokenBonusUIPacker(),
     'token': Comp7LightTokenBonusUIPacker(),
     Currency.CREDITS: _CurrencyBonusUIPacker(),
     Currency.GOLD: _CurrencyBonusUIPacker(),
     Currency.CRYSTAL: _CurrencyBonusUIPacker(),
     Currency.EQUIP_COIN: _CurrencyBonusUIPacker()})
    return packer


def getComp7LightEventUIDataPacker(event):
    return Comp7LightDailyQuestUIDataPacker(event) if event.getType() in EVENT_TYPE.LIKE_BATTLE_QUESTS else None


class Comp7LightDailyQuestUIDataPacker(DailyQuestUIDataPacker):

    def _packBonuses(self, model):
        packer = getComp7LightBonusPacker()
        self._tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self._tooltipData)


class Comp7LightTokenBonusUIPacker(TokenBonusUIPacker):
    _comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionController)
    _COMP7_LIGHT_PROGRESSION_TOKEN = 'Comp7LightProgressionToken'

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._comp7LightProgressionController.progressionToken):
            return cls._COMP7_LIGHT_PROGRESSION_TOKEN
        super(Comp7LightTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(Comp7LightTokenBonusUIPacker, cls)._getTooltipsPackers()
        packers.update({cls._COMP7_LIGHT_PROGRESSION_TOKEN: cls.__getComp7LightProgressionTooltip})
        return packers

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(Comp7LightTokenBonusUIPacker, cls)._getTokenBonusPackers()
        complexPaker = tokenBonusPackers.get(COMPLEX_TOKEN)
        tokenBonusPackers.update({cls._COMP7_LIGHT_PROGRESSION_TOKEN: complexPaker})
        return tokenBonusPackers

    @classmethod
    def __getComp7LightProgressionTooltip(cls, *_):
        return createTooltipData(makeTooltip(backport.text(R.strings.comp7_light.quests.bonuses.progressionToken.header()), backport.text(R.strings.comp7_light.quests.bonuses.progressionToken.body())))


class _CurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setBigIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setUserName(getLocalizedBonusName(bonus.getName()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

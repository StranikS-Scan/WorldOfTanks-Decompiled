# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/bonus_packer.py
import typing
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from battle_royale.gui.constants import STP_COIN
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.formatters import COMPLEX_TOKEN
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, getLocalizedBonusName, TokenBonusUIPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from constants import LOOTBOX_TOKEN_PREFIX
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CurrenciesBonus

class ExtendedCurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setUserName(getLocalizedBonusName(bonus.getName()))
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class CurrenciesBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getCode())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getCode())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        model.setUserName(label)
        model.setBigIcon(bonus.getName())
        model.setTooltipContentId(str(cls.getContentId(bonus)[0]))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.battle_royale.lobby.tooltips.ProxyCurrencyTooltipView()] if bonus.getCode() == STP_COIN else super(CurrenciesBonusUIPacker, cls)._getContentId(bonus)


class BRLootBoxPacker(SimpleBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        lootbox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(bonus.getTokens().keys()[0])
        count = bonus.getCount()
        if lootbox is None or count <= 0:
            return
        else:
            model = cls._getBonusModel()
            model.setIsCompensation(bonus.isCompensation())
            model.setName(LOOTBOX_TOKEN_PREFIX.split(':')[0])
            model.setUserName(lootbox.getUserName())
            model.setValue(str(count))
            model.setIcon(lootbox.getType())
            model.setBigIcon(lootbox.getType())
            model.setOverlayType(lootbox.getCategory())
            model.setLabel(lootbox.getUserName())
            return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.event_lootboxes.lobby.event_lootboxes.tooltips.EntryPointTooltip()]


BR_PROGRESSION_TOKEN = 'BRProgressionToken'
BR_LOOTBOX_TOKEN = 'BRLootboxToken'

class BRTokenBonusUIPacker(TokenBonusUIPacker):
    _brProgressionController = dependency.descriptor(IBRProgressionOnTokensController)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._brProgressionController.progressionToken):
            return BR_PROGRESSION_TOKEN
        if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
            return BR_LOOTBOX_TOKEN
        super(BRTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        pakers = super(BRTokenBonusUIPacker, cls)._getTooltipsPackers()
        pakers.update({BR_PROGRESSION_TOKEN: cls.__getBRProgressionTooltip})
        return pakers

    @classmethod
    def _getContentId(cls, bonus):
        bonusTokens = bonus.getTokens()
        for token in bonusTokens:
            if token.startswith(LOOTBOX_TOKEN_PREFIX):
                return BRLootBoxPacker.getContentId(bonus)

        return super(BRTokenBonusUIPacker, cls)._getContentId(bonus)

    @classmethod
    def __getBRProgressionTooltip(cls, *_):
        tokenBase = R.strings.battle_royale_progression.quests.bonuses.progressionToken
        return createTooltipData(makeTooltip(backport.text(tokenBase.header()), backport.text(tokenBase.body())))

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(BRTokenBonusUIPacker, cls)._getTokenBonusPackers()
        complexPaker = tokenBonusPackers.get(COMPLEX_TOKEN)
        tokenBonusPackers.update({BR_PROGRESSION_TOKEN: complexPaker,
         BR_LOOTBOX_TOKEN: BRLootBoxPacker()})
        return tokenBonusPackers

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        return bonusPacker.pack(bonus)[0] if isinstance(bonusPacker, BRLootBoxPacker) else super(BRTokenBonusUIPacker, cls)._packToken(bonusPacker, bonus, *args)


def getBonusPacker():
    packer = getBattlePassBonusPacker()
    currencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    tokenBonusPacker = BRTokenBonusUIPacker()
    packer.getPackers().update({'currencies': CurrenciesBonusUIPacker(),
     Currency.CREDITS: currencyBonusUIPacker,
     Currency.CRYSTAL: currencyBonusUIPacker,
     'token': tokenBonusPacker,
     'battleToken': tokenBonusPacker})
    return packer

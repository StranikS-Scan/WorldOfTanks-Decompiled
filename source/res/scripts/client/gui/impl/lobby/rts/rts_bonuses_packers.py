# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/rts_bonuses_packers.py
import typing
import logging
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, TokenBonusUIPacker, ItemBonusUIPacker, GroupsBonusUIPacker
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import CurrencyTypeEnum
from gui.impl.lobby.rts.model_helpers import ARENA_BONUS_TYPE_TO_CURRENCY_TYPE_ENUM
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
_logger = logging.getLogger(__name__)
_COLLECTION_STR_PATH = 'COLLECTION_STR_PATH'

def getRTSBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'items': RTSItemBonusUIPacker(),
     'rtsCurrencyToken': RTSTicketTokenBonusPacker(),
     'groups': RtsCollectionGroupsBonusUIPacker(),
     'tmanToken': RTSTmanTemplateBonusPacker()})
    return BonusUIPacker(mapping)


class RTSTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _getIcon(cls, recruitInfo):
        return recruitInfo.getSmallIcon()


class RTSItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(RTSItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        model.setName(item.getGUIEmblemID())
        return model


class RTSTicketTokenBonusPacker(TokenBonusUIPacker):
    _rtsController = dependency.descriptor(IRTSBattlesController)

    @classmethod
    def _pack(cls, bonus):
        result = super(RTSTicketTokenBonusPacker, cls)._pack(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                model = cls._getBonusModel()
                cls._packToken(token, model)
                result.append(model)

        return result

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(RTSTicketTokenBonusPacker, cls)._getToolTip(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                result.append(cls._packTokenTooltip(token))

        return result

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID in cls._rtsController.getAvailableCurrencies()

    @classmethod
    def _toEnum(cls, token):
        for arenaBonusType in cls._rtsController.bonusTypesWithCurrency:
            currencyName = cls._rtsController.getSettings().getCurrencyTokenName(arenaBonusType)
            if currencyName == token.id:
                return ARENA_BONUS_TYPE_TO_CURRENCY_TYPE_ENUM[arenaBonusType]

        return None

    @classmethod
    def _packToken(cls, token, model):
        model.setValue(str(token.count))
        currencyEnum = cls._toEnum(token)
        if currencyEnum:
            model.setName(currencyEnum.value)

    @classmethod
    def _packTokenTooltip(cls, token):
        return createTooltipData(specialArgs=[cls._toEnum(token)])

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for _ in bonusTokens:
            result.append(R.views.lobby.rts.StrategistCurrencyTooltip())

        return result


class RtsCollectionGroupsBonusUIPacker(GroupsBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon('rtsCollection')
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = R.strings.rts_battles.metaQuests.tooltips.collectionItem
        return [createTooltipData(makeTooltip(backport.text(tooltipData.title()), backport.text(tooltipData.descr())))]

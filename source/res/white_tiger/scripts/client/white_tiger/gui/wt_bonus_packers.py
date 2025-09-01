# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_bonus_packers.py
import logging
import typing
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.server_events.awards_formatters import TokenBonusFormatter
from gui.shared.missions.packers.bonus import BonusUIPacker, GroupsBonusUIPacker, TokenBonusUIPacker, getDefaultBonusPackersMap, SimpleBonusUIPacker
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.white_tiger_gui_constants import WHITE_TIGER_BATTLES_TICKET, WHITE_TIGER_STAMP, TICKET_ICON_FILE_NAME
from white_tiger.gui.server_events.bonuses import WtCustomizationsBonus, TicketTokensBonus, StampTokensBonus
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.server_events.bonuses import TokensBonus, SimpleBonus
    from gui.server_events.formatters import TokenComplex
_logger = logging.getLogger(__name__)

def mergeWtProgressionBonuses(bonuses):
    progBonus = []
    for bonus in bonuses:
        if bonus.getName() == 'customizations':
            progBonus.append(WtCustomizationsBonus(bonus.getName(), bonus.getValue()))
            continue
        progBonus.append(bonus)

    return progBonus


def getWTEventBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'ticket': WTTokenBonusPacker(),
     'stamp': WTTokenBonusPacker(),
     'lootBox': WTLootBoxPacker(),
     'groups': WTGroupBonusPacker()})
    return mapping


def getWTEventBonusPacker():
    mapping = getWTEventBonusPackerMap()
    return BonusUIPacker(mapping)


def isStyle3D(customizationItem):
    return customizationItem.itemTypeName == 'style' and customizationItem.modelsSet


class WTTokenBonusPacker(TokenBonusUIPacker):
    _economicsCtrl = dependency.descriptor(IEconomicsController)

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = BonusModel()
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return tokenID

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(WTTokenBonusPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({cls._economicsCtrl.getTicketTokenName(): cls.__packTicketToken,
         cls._economicsCtrl.getStampTokenName(): cls.__packStampToken})
        return tokenBonusPackers

    @classmethod
    def _getTooltipsPackers(cls):
        toolTipPackers = super(WTTokenBonusPacker, cls)._getTooltipsPackers()
        toolTipPackers.update({cls._economicsCtrl.getTicketTokenName(): cls._packTicketTokenTooltip,
         cls._economicsCtrl.getStampTokenName(): cls._packStampTokenTooltip})
        return toolTipPackers

    @classmethod
    def __packTicketToken(cls, model, bonus, *args):
        model.setName(TICKET_ICON_FILE_NAME)
        model.setLabel(backport.text(R.strings.white_tiger_lobby.ticketTooltip.title()))
        model.setValue(str(bonus.formatValue()))
        return model

    @classmethod
    def __packStampToken(cls, model, bonus, *args):
        token = args[1]
        model.setValue(str(token.count))
        stampNameArray = token.id.split(':')
        model.setName(stampNameArray[1] if len(stampNameArray) > 1 else token.id)
        return model

    @classmethod
    def _packTicketTokenTooltip(cls, complexToken, token):
        return createTooltipData(tooltip=WHITE_TIGER_BATTLES_TICKET, isWulfTooltip=True, specialAlias=None, specialArgs=[])

    @classmethod
    def _packStampTokenTooltip(cls, complexToken, token):
        return createTooltipData(tooltip=WHITE_TIGER_STAMP, isWulfTooltip=True, specialAlias=None, specialArgs=[])


class WTLootBoxPacker(SimpleBonusUIPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        result = []
        model = cls._packSingleBonus(bonus, '')
        if model is not None:
            result.append(model)
        return result

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        lootboxID = first(bonus.getTokens().keys())
        lootbox = cls._itemsCache.items.tokens.getLootBoxByTokenID(lootboxID)
        count = bonus.getCount()
        if lootbox is None or count < 0:
            _logger.error('Unknown lootbox %s or invalid count %d', lootboxID, count)
            return
        else:
            icon = '{}_{}'.format(bonus.getName(), lootbox.getCategory())
            model = cls._getBonusModel()
            model.setIsCompensation(bonus.isCompensation())
            model.setName(icon)
            model.setValue(str(count))
            model.setIcon(icon)
            model.setLabel(lootbox.getUserName())
            return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class WTTokenFormatter(TokenBonusFormatter):

    def _getFormattedBonus(self, tokenID, token, bonus):
        formatted = self._formatBonusToken(TICKET_ICON_FILE_NAME, token, bonus)
        return formatted

    @staticmethod
    def getBonusFactorTooltip(name):
        return makeTooltip(header=backport.text(R.strings.white_tiger_lobby.ticketTooltip.title()), body=backport.text(R.strings.white_tiger_lobby.ticketTooltip.description()))


class WTGroupBonusPacker(GroupsBonusUIPacker):

    @classmethod
    def _getIcon(cls, bonus):
        pass

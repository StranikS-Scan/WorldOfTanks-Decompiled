# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/debut_boxes.py
import constants
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.missions.packers.bonus import TokenBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, SimpleBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap

class DebutBoxesTokensBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = super(DebutBoxesTokensBonusUIPacker, cls)._pack(bonus)
        for tokenID, _ in bonus.getTokens().iteritems():
            if tokenID.startswith('lootBox:'):
                packer = DebutLootBoxesBonusUIPacker()
                result.extend(packer.pack(bonus))

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(DebutBoxesTokensBonusUIPacker, cls)._getToolTip(bonus)
        for tokenID, _ in bonus.getTokens().iteritems():
            if tokenID.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                result.append(None)

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for _ in bonus.getTokens().iterkeys():
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class DebutLootBoxesBonusUIPacker(SimpleBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        model.setName(bonus.getName())
        model.setLabel(label)
        lootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(cls._getTokenID(bonus))
        if lootBox is not None:
            model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(lootBox.getIconName())()))
            model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(lootBox.getIconName())()))
        return model

    @classmethod
    def _getTokenID(cls, bonus):
        return findFirst(None, bonus.getTokens().keys())

    @classmethod
    def _getBonusModel(cls):
        return TokenBonusModel()


def getDebutBoxesBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': DebutBoxesTokensBonusUIPacker()})
    return BonusUIPacker(mapping)

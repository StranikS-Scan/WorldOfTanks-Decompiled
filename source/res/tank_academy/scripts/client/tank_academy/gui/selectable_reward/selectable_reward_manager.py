# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/selectable_reward/selectable_reward_manager.py
from helpers import dependency
from gui.selectable_reward.common import SelectableRewardManager
from skeletons.gui.game_control import ITankAcademyController
from tank_academy.gui.shared.gui_items.processors.offers import TankAcademyOfferProcessor

class TankAcademySelectableRewardManager(SelectableRewardManager):
    _tankAcademyController = dependency.descriptor(ITankAcademyController)
    _SINGLE_GIFT_PROCESSOR = TankAcademyOfferProcessor

    @classmethod
    def isFeatureReward(cls, tokenID):
        return cls._tankAcademyController.isTAOfferToken(tokenID)

    @classmethod
    def getTabTooltipData(cls, selectableBonus):
        return None

    @classmethod
    def getBonusOffer(cls, bonus):
        return cls._getBonusOffer(bonus)

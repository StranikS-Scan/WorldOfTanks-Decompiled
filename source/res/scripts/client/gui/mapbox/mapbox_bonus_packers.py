# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/mapbox/mapbox_bonus_packers.py
from constants import PREMIUM_ENTITLEMENTS
from gui.impl.backport import TooltipData, text
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.mapbox.crew_book_reward_option_model import CrewBookRewardOptionModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.server_events.bonuses import PlusPremiumDaysBonus
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, SimpleBonusUIPacker, BonusUIPacker, GoodiesBonusUIPacker, CustomizationBonusUIPacker, getLocalizedBonusName, BaseBonusUIPacker, CrewBookBonusUIPacker, ItemBonusUIPacker

def getMapboxBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'goodies': MapboxGoodiesPacker(),
     PREMIUM_ENTITLEMENTS.PLUS: MapboxPremiumDaysPacker(),
     'customizations': MapboxCustomizationPacker(),
     'items': MapboxItemPacker(),
     'selectableCrewbook': MapboxSelectablePacker(),
     'crewBooks': MapboxCrewBookPacker(),
     'randomCrewbook': MapboxRandomCrewbookPacker()})
    return BonusUIPacker(mapping)


class MapboxPremiumDaysPacker(SimpleBonusUIPacker):
    _ICONS_AVAILABLE = (1,)

    @classmethod
    def _packSingleBonus(cls, bonus, label=''):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        model.setIsOpenable(False)
        days = bonus.getValue()
        if days in cls._ICONS_AVAILABLE:
            model.setIcon('{}_{}'.format(bonus.getName(), days))
        else:
            model.setIcon('premium_universal')
        return model


class MapboxGoodiesPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(booster.boosterGuiType)
        model.setLabel(booster.fullUserName)
        model.setIsOpenable(False)
        return model


class MapboxItemPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(item.name)
        model.setLabel(item.userName)
        return model


class MapboxCustomizationPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setLabel(label)
        model.setIsOpenable(False)
        return model


class MapboxSelectablePacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item) for item in bonus.getItems() ]

    @classmethod
    def _packSingleItem(cls, item):
        model = RewardItemModel()
        model.setName(item.name)
        model.setValue(str(item.count))
        label = getLocalizedBonusName(item.name) or ''
        model.setLabel(label)
        model.setIcon(item.name)
        model.setIsOpenable(True)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SELECTABLE_CREWBOOK, specialArgs=[item]) for item in bonus.getItems() ]


class MapboxCrewBookPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = CrewBookRewardOptionModel()
        cls._packCommon(bonus, model)
        model.setIcon(book.getBonusIconName())
        model.setValue(str(count))
        model.setLabel(text(R.strings.nations.dyn(book.getNation())()))
        description = text(R.strings.mapbox.rewardDescription.dyn(book.itemTypeName)(), exp=book.getXP(), nation=text(R.strings.nations.dyn(book.getNation()).genetiveCase()))
        model.setDescription(description)
        model.setItemID(book.intCD)
        return model


class MapboxRandomCrewbookPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item) for item in bonus.getItems() ]

    @classmethod
    def _packSingleItem(cls, item):
        model = RewardItemModel()
        model.setName(item.name)
        model.setValue(str(item.count))
        model.setIcon(item.name)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [ TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.RANDOM_CREWBOOK, specialArgs=[item]) for item in sorted(bonus.getItems()) ]

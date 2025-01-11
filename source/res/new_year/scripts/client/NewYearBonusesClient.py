# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/NewYearBonusesClient.py
import copy
from new_year_common.items.new_year import g_cache
from new_year_common.new_year_bonuses import NewYearBonuses
from new_year_common.items.components.ny_constants import TOY_TYPE_IDS_BY_NAME, YEARS_INFO
from new_year_common.items.components.ny_constants import CurrentNYConstants, TOKEN_NY25_MANDARIN
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import __mergeDicts as mergeDicts, SimpleBonus, CountableIntegralBonus, TokensBonus, mergeSimpleBonuses

class NewYearBonusesClient(NewYearBonuses):

    def _getClientBonuses(self):
        return {CurrentNYConstants.TOYS: ToyBonus,
         CurrentNYConstants.ANY_OF: ToyBonus,
         CurrentNYConstants.NEW_TOYS: ToyBonus,
         CurrentNYConstants.TOY_FRAGMENTS: SimpleBonus,
         CurrentNYConstants.FILLERS: CountableIntegralBonus,
         CurrentNYConstants.ATMOSPHERE_POINTS: SimpleBonus,
         CurrentNYConstants.ALL_OF: AllOfToyBonus,
         CurrentNYConstants.MANDARINS: MandarinsTokenBonus,
         CurrentNYConstants.TOY_COMPENSATION: toyCompensationFactory}

    def _getClientMergers(self):
        return [(NewYearBonusesClient.__toyPredicate, NewYearBonusesClient.__mergeNYToyBonuses), (NewYearBonusesClient.__mandarinsPredicate, NewYearBonusesClient.__mergeMandarinsBonuses), (NewYearBonusesClient.__fakeMandarinsPredicate, None)]

    @staticmethod
    def __toyPredicate(lhv, rhv):
        return isinstance(lhv, ToyBonus) and isinstance(rhv, ToyBonus) and type(lhv) is type(rhv)

    @staticmethod
    def __mergeNYToyBonuses(lhv, rhv):
        merged = copy.deepcopy(lhv)
        value = merged.getValue()
        if merged.getName() == CurrentNYConstants.TOYS:
            merged.setValue(mergeDicts(value, rhv.getValue()))
            merged.setNewToys(set(merged.getNewToys()).union(set(rhv.getNewToys())))
        else:
            merged.setValue(value.extend(rhv.getValue()))
        return (merged, True)

    @staticmethod
    def __mandarinsPredicate(lhv, rhv):
        return isinstance(lhv, MandarinsTokenBonus) and isinstance(rhv, MandarinsTokenBonus) and lhv.isCompensation() == rhv.isCompensation()

    @staticmethod
    def __fakeMandarinsPredicate(lhv, rhv):
        return isinstance(lhv, MandarinsTokenBonus) and isinstance(rhv, MandarinsTokenBonus) and lhv.isCompensation() != rhv.isCompensation()

    @staticmethod
    def __mergeMandarinsBonuses(lhv, rhv):
        return mergeSimpleBonuses(lhv, rhv)


class ToyBonus(SimpleBonus):

    @staticmethod
    def createEmptyToy():
        return ToyBonus(CurrentNYConstants.TOYS, {})

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        self.__newToys = set()
        if name == CurrentNYConstants.NEW_TOYS:
            self.__newToys = value
            name = CurrentNYConstants.TOYS
            value = {}
        super(ToyBonus, self).__init__(name, value, isCompensation, ctx, compensationReason)
        self.__toyBonusValues = {CurrentNYConstants.TOYS: [],
         CurrentNYConstants.ANY_OF: []}
        self.aggregateToy(self)

    def setValue(self, value):
        super(ToyBonus, self).setValue(value)
        self.__toyBonusValues = {CurrentNYConstants.TOYS: [],
         CurrentNYConstants.ANY_OF: []}
        self.aggregateToy(self)

    def getToyBonusValues(self):
        return self.__toyBonusValues

    def getNewToys(self):
        return self.__newToys

    def setNewToys(self, newToys):
        self.__newToys = newToys

    def aggregateToy(self, toy):
        if toy.getName() == CurrentNYConstants.TOYS:
            if toy.getValue():
                self.__toyBonusValues[CurrentNYConstants.TOYS].append(toy.getValue())
        elif toy.getName() == CurrentNYConstants.MANDARINS:
            self.__toyBonusValues[CurrentNYConstants.MANDARINS] = self.__toyBonusValues.get(CurrentNYConstants.MANDARINS, 0) + toy.getCount()
        else:
            self.__toyBonusValues[CurrentNYConstants.ANY_OF].extend(toy.getValue())


class AllOfToyBonus(ToyBonus):

    def __new__(cls, name, value, isCompensation=False, ctx=None, compensationReason=None):
        bonuses = []
        for toyDescr in g_cache.toys.values():
            toyDetails = (TOY_TYPE_IDS_BY_NAME.get(toyDescr.type), YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME.get(toyDescr.setting), toyDescr.rank)
            for toy, _ in value.items():
                toyDetails = tuple(((toyDetail if toy[index] != -1 else -1) for index, toyDetail in enumerate(toyDetails)))
                if toyDetails == toy:
                    bonus = ToyBonus(CurrentNYConstants.TOYS, toyDetails, isCompensation=isCompensation, ctx=ctx, compensationReason=compensationReason)
                    bonuses.append(bonus)

        return bonuses


class MandarinsTokenBonus(TokensBonus):

    def __init__(self, _, value, isCompensation=False, ctx=None, compensationReason=None):
        super(MandarinsTokenBonus, self).__init__(CurrentNYConstants.MANDARINS, value, isCompensation, ctx, compensationReason)

    def isShowInGUI(self):
        return True

    def _getWrappedBonusList(self):
        return [{'id': 0,
          'type': CurrentNYConstants.IP_TYPE_CUSTOM_MANDATINS,
          'value': 1,
          'icon': {AWARDS_SIZES.SMALL: self.getIconBySize(AWARDS_SIZES.SMALL),
                   AWARDS_SIZES.BIG: self.getIconBySize(AWARDS_SIZES.BIG)}}]


def mandarinPredicate(tokenID):
    return tokenID == TOKEN_NY25_MANDARIN


def mandarinFactory(value, _, __):
    for tokenID, tokenValue in value.iteritems():
        return MandarinsTokenBonus(CurrentNYConstants.MANDARINS, {tokenID: tokenValue}, isCompensation=False)


def toyCompensationPredicate(tokenID):
    tokenPrefix = 'lb_comp:' + TOKEN_NY25_MANDARIN
    return tokenID.startswith(tokenPrefix)


def toyCompensationTokenFactory(value, _, __):
    for tokenID, tokenValue in value.iteritems():
        amount = int(tokenID.split(':')[2])
        count = tokenValue['count']
        bonusValue = copy.deepcopy(tokenValue)
        bonusValue['count'] = amount * count
        return MandarinsTokenBonus(CurrentNYConstants.MANDARINS, {TOKEN_NY25_MANDARIN: bonusValue}, True)


def toyCompensationFactory(_, value, *__, **___):
    result = []
    for tokenID, tokenValue in value.iteritems():
        amount = int(tokenID.split(':')[2])
        count = tokenValue['count']
        bonusValue = copy.deepcopy(tokenValue)
        bonusValue['count'] = amount * count
        result.append(MandarinsTokenBonus(CurrentNYConstants.MANDARINS, {TOKEN_NY25_MANDARIN: bonusValue}, isCompensation=True))

    return result

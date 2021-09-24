# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/premium_benefits.py
from collections import namedtuple
from operator import methodcaller
import typing
from frameworks.wulf import Array
from gui.battle_results.presenter.getter.common import Field
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.premium_benefit_model import PremiumBenefitModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.benefit_value_model import BenefitValueModel
from shared_utils import CONST_CONTAINER
if typing.TYPE_CHECKING:
    from gui.server_events import EventsCache
    from helpers.server_settings import ServerSettings

class _PremiumBenefitSubstitutionIDs(CONST_CONTAINER):
    MULTIPLIER_PERCENT = 'multiplier_percent'
    MULTIPLIER = 'multiplier'
    COUNT = 'count'


_PREMIUM_BENEFIT_STRINGS = R.strings.postbattle_screen.premiumBenefits
PremiumBenefits = namedtuple('premiumBenefits', ('xpBonus', 'creditsBonus', 'tmenXPBonus', 'additionalBonus', 'piggyBank', 'premQuests', 'preferredMaps', 'squadBonus'))

class PremiumBenefitFieldBase(Field):
    __slots__ = ('__types', '__substitutionIDs', '__settingNames', '_isAlwaysEnabled', '_settingsGetter')

    def __init__(self, stringID, types, substitutionIDs, settingsGetter, isAlwaysEnabled=False):
        super(PremiumBenefitFieldBase, self).__init__(stringID)
        self.__types = types
        self.__substitutionIDs = substitutionIDs
        self._isAlwaysEnabled = isAlwaysEnabled
        self._settingsGetter = settingsGetter

    def getFieldValues(self, serverSettings, eventsCache):
        return self._getRecord(self._getValue(serverSettings)) if self._isEnabled(serverSettings) else None

    def _getRecord(self, values):
        record = Array()
        for value, valueType, substitutionID in zip(values, self.__types, self.__substitutionIDs):
            benefitValue = BenefitValueModel()
            benefitValue.setValue(value)
            benefitValue.setSubstitutionID(substitutionID)
            benefitValue.setValueType(valueType)
            record.addViewModel(benefitValue)

        return record

    def _isEnabled(self, serverSettings):
        return self._isAlwaysEnabled or methodcaller(self._settingsGetter)(serverSettings).get('enabled', False)


class PremiumBenefitField(PremiumBenefitFieldBase):
    __slots__ = ('__settingNames', '_isAlwaysEnabled')

    def __init__(self, stringID, types, substitutionIDs, settingsGetter, settingNames, isAlwaysEnabled=False):
        super(PremiumBenefitField, self).__init__(stringID, types, substitutionIDs, settingsGetter, isAlwaysEnabled)
        self.__settingNames = settingNames

    def _getValue(self, serverSettings):
        for name in self.__settingNames:
            yield methodcaller(self._settingsGetter)(serverSettings).get(name, 0)


class PremiumBattleBonusField(PremiumBenefitFieldBase):
    __slots__ = ()

    def _getValue(self, serverSettings):
        return (methodcaller(self._settingsGetter)(serverSettings) % 1,)

    def _isEnabled(self, serverSettings):
        return True


class PremiumQuestsField(PremiumBenefitFieldBase):
    __slots__ = ()

    def getFieldValues(self, serverSettings, eventsCache):
        return self._getRecord(self._getValue(eventsCache)) if self._isEnabled(serverSettings) else None

    def _getValue(self, eventsCache):
        return (len(eventsCache.getPremiumQuests()),)


class SquadBonusField(PremiumBenefitFieldBase):
    __slots__ = ()

    def _getValue(self, serverSettings):
        return (getattr(serverSettings, self._settingsGetter).ownCredits,)

    def _isEnabled(self, serverSettings):
        return self._isAlwaysEnabled or getattr(serverSettings, self._settingsGetter).isEnabled


def getPremiumBenefits():
    return PremiumBenefits(xpBonus=PremiumBattleBonusField(stringID=_PREMIUM_BENEFIT_STRINGS.xpBonus(), types=(PremiumBenefitModel.PERCENT_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER_PERCENT,), settingsGetter='getPremiumPlusXPBonus'), creditsBonus=PremiumBattleBonusField(stringID=_PREMIUM_BENEFIT_STRINGS.creditsBonus(), types=(PremiumBenefitModel.PERCENT_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER_PERCENT,), settingsGetter='getPremiumPlusCreditsBonus'), tmenXPBonus=PremiumBattleBonusField(stringID=_PREMIUM_BENEFIT_STRINGS.tmenXpBonus(), types=(PremiumBenefitModel.PERCENT_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER_PERCENT,), settingsGetter='getPremiumPlusTmenXPBonus'), additionalBonus=PremiumBenefitField(stringID=_PREMIUM_BENEFIT_STRINGS.additionalBonus(), types=(PremiumBenefitModel.NUMBER_VALUE, PremiumBenefitModel.NUMBER_VALUE), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER, _PremiumBenefitSubstitutionIDs.COUNT), settingsGetter='getAdditionalBonusConfig', settingNames=('bonusFactor', 'applyCount')), piggyBank=PremiumBenefitField(stringID=_PREMIUM_BENEFIT_STRINGS.piggyBank(), types=(PremiumBenefitModel.PERCENT_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER_PERCENT,), settingsGetter='getPiggyBankConfig', settingNames=('multiplier',)), premQuests=PremiumQuestsField(stringID=_PREMIUM_BENEFIT_STRINGS.premQuests(), types=(PremiumBenefitModel.NUMBER_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.COUNT,), settingsGetter='getPremQuestsConfig'), preferredMaps=PremiumBenefitField(stringID=_PREMIUM_BENEFIT_STRINGS.preferredMaps(), types=(PremiumBenefitModel.NUMBER_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.COUNT,), settingsGetter='getPreferredMapsConfig', settingNames=('premiumSlots',), isAlwaysEnabled=True), squadBonus=SquadBonusField(stringID=_PREMIUM_BENEFIT_STRINGS.squadBonus(), types=(PremiumBenefitModel.PERCENT_VALUE,), substitutionIDs=(_PremiumBenefitSubstitutionIDs.MULTIPLIER_PERCENT,), settingsGetter='squadPremiumBonus'))

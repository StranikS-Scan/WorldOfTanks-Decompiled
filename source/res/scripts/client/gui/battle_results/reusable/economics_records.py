# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/economics_records.py
import itertools
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from constants import PREMIUM_TYPE
from ValueReplay import ValueReplay, ValueReplayConnector
from debug_utils import LOG_ERROR
from dossiers2.custom.records import RECORD_DB_IDS
from gui.battle_results.reusable import records
from gui.battle_results.settings import FACTOR_VALUE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_DEFAULT_FACTORS = {_CAPS.PREM_CREDITS: FACTOR_VALUE.BASE_CREDITS_FACTOR,
 _CAPS.PREM_XP: FACTOR_VALUE.BASE_XP_FACTOR,
 _CAPS.PREM_TMEN_XP: FACTOR_VALUE.BASE_TMEN_XP_FACTOR}

def _getPremiumBonusFactor(factor, bonusCaps, isPremBonusEnabled):
    return factor if isPremBonusEnabled else _DEFAULT_FACTORS[bonusCaps]


def _updateAdditionalFactorFromReplay(replay, results, setDefault=False):
    if 'additionalXPFactor10' not in replay:
        return
    if setDefault:
        if 'dailyXPFactor10' in replay:
            replay['additionalXPFactor10'] = FACTOR_VALUE.ADDITIONAL_BONUS_ZERO_FACTOR
        else:
            replay['additionalXPFactor10'] = FACTOR_VALUE.ADDITIONAL_BONUS_ONE_FACTOR
    else:
        replay['additionalXPFactor10'] = results['additionalXPFactor10']


class _AdditionalRecords(records.RawRecords):
    __slots__ = ()

    def __init__(self, results):
        rawRecords = {}
        if 'autoRepairCost' in results:
            cost = results['autoRepairCost']
            if cost is not None:
                rawRecords['autoRepairCost'] = -cost
        if 'autoLoadCost' in results:
            cost = results['autoLoadCost']
            if cost is not None:
                rawRecords['autoLoadCredits'] = -cost[0]
                rawRecords['autoLoadGold'] = -cost[1]
        if 'autoEquipCost' in results:
            cost = results['autoEquipCost']
            if cost is not None:
                rawRecords['autoEquipCredits'] = -cost[0]
                rawRecords['autoEquipGold'] = -cost[1]
                rawRecords['autoEquipCrystals'] = -cost[2]
        if 'piggyBank' in results:
            cost = results['piggyBank']
            if cost is not None:
                rawRecords['piggyBank'] = cost
        super(_AdditionalRecords, self).__init__(rawRecords)
        return


class _CrystalRecords(records.RawRecords):
    __slots__ = ()

    def __init__(self, replay, results):
        rawRecords = {}
        eventToken = 'eventCrystalList_'
        eventsCrystals = 0
        for _, (appliedName, appliedValue), (_, _) in replay:
            if appliedName == 'originalCrystal' and appliedValue:
                rawRecords[appliedName] = appliedValue
            if appliedName.startswith(eventToken):
                eventsCrystals += appliedValue

        if eventsCrystals:
            rawRecords['events'] = eventsCrystals
        if 'autoEquipCost' in results:
            cost = results['autoEquipCost']
            if cost is not None:
                rawRecords['autoEquipCrystals'] = -cost[2]
        super(_CrystalRecords, self).__init__(rawRecords)
        return


class _CreditsReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, results, squadCreditsFactor=0):
        super(_CreditsReplayRecords, self).__init__(replay, 'credits')
        self._addRecord(ValueReplay.SUB, 'originalCreditsToDraw', results['originalCreditsToDraw'], 0)
        self._addRecord(ValueReplay.SET, 'achievementCredits', results['achievementCredits'], 0)
        self._addRecord(ValueReplay.FACTOR, 'premSquadCreditsFactor100', squadCreditsFactor, 0)
        self._addRecord(ValueReplay.SUBCOEFF, 'originalCreditsToDrawSquad', results['originalCreditsToDrawSquad'], results['originalCreditsToDrawSquad'] * self.getFactor('premSquadCreditsFactor100') * -1)

    def _getRecord(self, name):
        value = super(_CreditsReplayRecords, self)._getRecord(name)
        if name in ('originalCreditsToDraw', 'achievementCredits'):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumCreditsFactor100'))
        return value


class _XPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, isHighScope, achievementXP):
        super(_XPReplayRecords, self).__init__(replay, 'xp')
        if isHighScope:
            self._addRecord(ValueReplay.SET, 'isHighScope', 1, 0)
        self._addRecord(ValueReplay.SET, 'achievementXP', achievementXP, 0)
        self._addRecord(ValueReplay.SET, 'xpToShow', max(0, self.getRecord('xp')), 0)

    def _getRecord(self, name):
        value = super(_XPReplayRecords, self)._getRecord(name)
        if name in ('achievementXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor100'))
        return value


class _FreeXPReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, achievementFreeXP):
        super(_FreeXPReplayRecords, self).__init__(replay, 'freeXP')
        self._addRecord(ValueReplay.SET, 'achievementFreeXP', achievementFreeXP, 0)

    def _getRecord(self, name):
        value = super(_FreeXPReplayRecords, self)._getRecord(name)
        if name in ('achievementFreeXP',):
            value = records.makeReplayValueRound(value * self.getFactor('appliedPremiumXPFactor100'))
        return value


class _TmenXPRecordsChains(object):
    __slots__ = ('__baseTmenXP', '__premiumTmenXP', '__premiumPlusTmenXP', '__baseTmenXPAdd', '__premiumTmenXPAdd', '__premiumPlusTmenXPAdd', '__isPremTmenXpBonuxEnabled')

    def __init__(self, bonusType, bonusCapsOverrides):
        super(_TmenXPRecordsChains, self).__init__()
        self.__baseTmenXP = records.RecordsIterator()
        self.__premiumTmenXP = records.RecordsIterator()
        self.__premiumPlusTmenXP = records.RecordsIterator()
        self.__baseTmenXPAdd = records.RecordsIterator()
        self.__premiumTmenXPAdd = records.RecordsIterator()
        self.__premiumPlusTmenXPAdd = records.RecordsIterator()
        self.__isPremTmenXpBonuxEnabled = _CAPS.checkAny(bonusType, _CAPS.PREM_TMEN_XP, specificOverrides=bonusCapsOverrides)

    def addResults(self, connector, results):
        premiumType = results.get('premMask', PREMIUM_TYPE.NONE)
        hasPremiumPlus = bool(premiumType & PREMIUM_TYPE.PLUS)
        if 'tmenXPReplay' in results and results['tmenXPReplay'] is not None:
            replay = ValueReplay(connector, recordName='tmenXP', replay=results['tmenXPReplay'])
            _updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self.__baseTmenXP.addRecords(records.ReplayRecords(replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self.__premiumTmenXP.addRecords(records.ReplayRecords(replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self.__premiumPlusTmenXP.addRecords(records.ReplayRecords(replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=hasPremiumPlus)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self.__baseTmenXPAdd.addRecords(records.ReplayRecords(replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self.__premiumTmenXPAdd.addRecords(records.ReplayRecords(replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self.__premiumPlusTmenXPAdd.addRecords(records.ReplayRecords(replay))
        else:
            LOG_ERROR('TmenXP replay is not found', results)
        return

    def getRecords(self, premiumType, addBonusApplied):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            secondTmenXPData = self.__premiumPlusTmenXPAdd if addBonusApplied else self.__premiumPlusTmenXP
        else:
            secondTmenXPData = self.__premiumTmenXPAdd if addBonusApplied else self.__premiumTmenXP
        firstTmenXPData = self.__baseTmenXPAdd if addBonusApplied else self.__baseTmenXP
        return itertools.izip(firstTmenXPData, secondTmenXPData)

    def __updatePremiumXPFactor(self, replay, results, premType=PREMIUM_TYPE.NONE):
        if 'appliedPremiumTmenXPFactor100' not in replay:
            return
        if premType == PREMIUM_TYPE.PLUS:
            replay['appliedPremiumTmenXPFactor100'] = _getPremiumBonusFactor(results['premiumPlusTmenXPFactor100'], _CAPS.PREM_TMEN_XP, self.__isPremTmenXpBonuxEnabled)
        elif premType == PREMIUM_TYPE.BASIC:
            replay['appliedPremiumTmenXPFactor100'] = _getPremiumBonusFactor(results['premiumTmenXPFactor100'], _CAPS.PREM_TMEN_XP, self.__isPremTmenXpBonuxEnabled)
        else:
            replay['appliedPremiumTmenXPFactor100'] = FACTOR_VALUE.BASE_XP_FACTOR


class EconomicsRecordsChains(object):
    __slots__ = ('_baseCredits', '_premiumCredits', '_premiumPlusCredits', '_baseCreditsWithWotPlus', '_premiumCreditsWithWotPlus', '_premiumPlusCreditsWithWotPlus', '_goldRecords', '_additionalRecords', '_baseXP', '_premiumXP', '_premiumPlusXP', '_baseXPWithWotPlus', '_premiumXPWithWotPlus', '_premiumPlusXPWithWotPlus', '_baseXPAdd', '_premiumXPAdd', '_premiumPlusXPAdd', '_baseXPAddWithWotPlus', '_premiumXPAddWithWotPlus', '_premiumPlusXPAddWithWotPlus', '_baseFreeXP', '_premiumFreeXP', '_premiumPlusFreeXP', '_baseFreeXPWithWotPlus', '_premiumFreeXPWithWotPlus', '_premiumPlusFreeXPWithWotPlus', '_baseFreeXPAdd', '_premiumFreeXPAdd', '_premiumPlusFreeXPAdd', '_baseFreeXPAddWithWotPlus', '_premiumFreeXPAddWithWotPlus', '_premiumPlusFreeXPAddWithWotPlus', '_crystal', '_crystalDetails', '_tmenXPRecordsChains', '__isPremCreditsBonusEnabled', '__isPremXpBonusEnabled')

    def __init__(self, bonusType, bonusCapsOverrides):
        super(EconomicsRecordsChains, self).__init__()
        self._baseCredits = records.RecordsIterator()
        self._premiumCredits = records.RecordsIterator()
        self._premiumPlusCredits = records.RecordsIterator()
        self._baseCreditsWithWotPlus = records.RecordsIterator()
        self._premiumCreditsWithWotPlus = records.RecordsIterator()
        self._premiumPlusCreditsWithWotPlus = records.RecordsIterator()
        self._goldRecords = records.RecordsIterator()
        self._additionalRecords = records.RecordsIterator()
        self._baseXP = records.RecordsIterator()
        self._premiumXP = records.RecordsIterator()
        self._premiumPlusXP = records.RecordsIterator()
        self._baseXPWithWotPlus = records.RecordsIterator()
        self._premiumXPWithWotPlus = records.RecordsIterator()
        self._premiumPlusXPWithWotPlus = records.RecordsIterator()
        self._baseXPAdd = records.RecordsIterator()
        self._premiumXPAdd = records.RecordsIterator()
        self._premiumPlusXPAdd = records.RecordsIterator()
        self._baseXPAddWithWotPlus = records.RecordsIterator()
        self._premiumXPAddWithWotPlus = records.RecordsIterator()
        self._premiumPlusXPAddWithWotPlus = records.RecordsIterator()
        self._baseFreeXP = records.RecordsIterator()
        self._premiumFreeXP = records.RecordsIterator()
        self._premiumPlusFreeXP = records.RecordsIterator()
        self._baseFreeXPWithWotPlus = records.RecordsIterator()
        self._premiumFreeXPWithWotPlus = records.RecordsIterator()
        self._premiumPlusFreeXPWithWotPlus = records.RecordsIterator()
        self._baseFreeXPAdd = records.RecordsIterator()
        self._premiumFreeXPAdd = records.RecordsIterator()
        self._premiumPlusFreeXPAdd = records.RecordsIterator()
        self._baseFreeXPAddWithWotPlus = records.RecordsIterator()
        self._premiumFreeXPAddWithWotPlus = records.RecordsIterator()
        self._premiumPlusFreeXPAddWithWotPlus = records.RecordsIterator()
        self._tmenXPRecordsChains = _TmenXPRecordsChains(bonusType, bonusCapsOverrides)
        self._crystal = records.RecordsIterator()
        self._crystalDetails = records.RecordsIterator()
        self.__isPremCreditsBonusEnabled = _CAPS.checkAny(bonusType, _CAPS.PREM_CREDITS, specificOverrides=bonusCapsOverrides)
        self.__isPremXpBonusEnabled = _CAPS.checkAny(bonusType, _CAPS.PREM_XP, specificOverrides=bonusCapsOverrides)

    def getBaseCreditsRecords(self):
        return self._baseCredits

    def getPremiumCreditsRecords(self):
        return self._premiumCredits

    def getCreditsDiff(self):
        return self._premiumCredits.getRecord('credits', 'originalCreditsToDraw') - self._baseCredits.getRecord('credits', 'originalCreditsToDraw')

    def getBaseXPRecords(self):
        return self._baseXP

    def getPremiumXPRecords(self):
        return self._premiumXP

    def getPremiumXPAddRecords(self):
        return self._premiumXPAdd

    def getXPToShow(self, isDiffShow=False):
        values = []
        for xpRecords in self.getXPRecords():
            baseXP, premiumXP = xpRecords[:2]
            xp = premiumXP.getRecord('xpToShow')
            value = xp - baseXP.getRecord('xpToShow') if isDiffShow else xp
            values.append(value)

        return values

    def getCreditsToShow(self, isDiffShow=False):
        values = []
        for creditRecords in self.getMoneyRecords():
            baseCredits, premiumCredits = creditRecords[:2]
            value = premiumCredits.getRecord('credits', 'originalCreditsToDraw')
            if isDiffShow and value > 0:
                value -= baseCredits.getRecord('credits', 'originalCreditsToDraw')
            values.append(value)

        return values

    def getMoneyRecords(self, premiumType=PREMIUM_TYPE.NONE):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            resultPremiumData = self._premiumPlusCredits
            resultPremiumDataWithWotPlus = self._premiumPlusCreditsWithWotPlus
        else:
            resultPremiumData = self._premiumCredits
            resultPremiumDataWithWotPlus = self._premiumCreditsWithWotPlus
        return itertools.izip(self._baseCredits, resultPremiumData, self._goldRecords, self._additionalRecords, self._baseCreditsWithWotPlus, resultPremiumDataWithWotPlus)

    def getCrystalRecords(self):
        return itertools.izip(self._crystal, self._crystal)

    def getUnpackedCrystalRecords(self):
        return self._crystal

    def getCrystalDetails(self):
        return self._crystalDetails

    def haveCrystalsChanged(self):
        spent = self._additionalRecords.getRecord('autoBoostersCrystal')
        received = self._crystal.getRecord('originalCrystal')
        return any((spent, received)) or self._crystalDetails

    def getXPRecords(self, premiumType=PREMIUM_TYPE.NONE, addBonusApplied=False):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            if addBonusApplied:
                secondXPData = self._premiumPlusXPAdd
                secondFreeXPData = self._premiumPlusFreeXPAdd
                secondXPDataWithWotPlus = self._premiumPlusXPAddWithWotPlus
                secondFreeXPDataWithWotPlus = self._premiumPlusFreeXPAddWithWotPlus
            else:
                secondXPData = self._premiumPlusXP
                secondFreeXPData = self._premiumPlusFreeXP
                secondXPDataWithWotPlus = self._premiumPlusXPWithWotPlus
                secondFreeXPDataWithWotPlus = self._premiumPlusFreeXPWithWotPlus
        elif addBonusApplied:
            secondXPData = self._premiumXPAdd
            secondFreeXPData = self._premiumFreeXPAdd
            secondXPDataWithWotPlus = self._premiumXPAddWithWotPlus
            secondFreeXPDataWithWotPlus = self._premiumFreeXPAddWithWotPlus
        else:
            secondXPData = self._premiumXP
            secondFreeXPData = self._premiumFreeXP
            secondXPDataWithWotPlus = self._premiumXPWithWotPlus
            secondFreeXPDataWithWotPlus = self._premiumFreeXPWithWotPlus
        if addBonusApplied:
            firstXPData = self._baseXPAdd
            firstFreeXPData = self._baseFreeXPAdd
            firstXPDataWithWotPlus = self._baseXPAddWithWotPlus
            firstFreeXPDataWithWotPlus = self._baseFreeXPAddWithWotPlus
        else:
            firstXPData = self._baseXP
            firstFreeXPData = self._baseFreeXP
            firstXPDataWithWotPlus = self._baseXPWithWotPlus
            firstFreeXPDataWithWotPlus = self._baseFreeXPWithWotPlus
        return itertools.izip(firstXPData, secondXPData, firstFreeXPData, secondFreeXPData, firstXPDataWithWotPlus, secondXPDataWithWotPlus, firstFreeXPDataWithWotPlus, secondFreeXPDataWithWotPlus)

    def getXPDiff(self):
        return self._premiumXP.getRecord('xp') - self._baseXP.getRecord('xp')

    def getTmenXPRecords(self, premiumType=PREMIUM_TYPE.NONE, addBonusApplied=False):
        return self._tmenXPRecordsChains.getRecords(premiumType, addBonusApplied)

    def addResults(self, _, results):
        connector = ValueReplayConnector(results)
        self._addMoneyResults(connector, results)
        self._addXPResults(connector, results)
        self._addCrystalResults(connector, results)
        self._tmenXPRecordsChains.addResults(connector, results)

    def _addMoneyResults(self, connector, results):
        if 'creditsReplay' in results and results['creditsReplay'] is not None:
            replay = ValueReplay(connector, recordName='credits', replay=results['creditsReplay'])
            appliedPremiumCreditsFactor100Exists = 'appliedPremiumCreditsFactor100' in replay
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = FACTOR_VALUE.BASE_CREDITS_FACTOR
            self._baseCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.NONE, results, replay))
            self._baseCreditsWithWotPlus.addRecords(self.__buildCreditsReplayForWotPlus(PREMIUM_TYPE.NONE, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = _getPremiumBonusFactor(results['premiumCreditsFactor100'], _CAPS.PREM_CREDITS, self.__isPremCreditsBonusEnabled)
            self._premiumCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.BASIC, results, replay))
            self._premiumCreditsWithWotPlus.addRecords(self.__buildCreditsReplayForWotPlus(PREMIUM_TYPE.BASIC, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = _getPremiumBonusFactor(results['premiumPlusCreditsFactor100'], _CAPS.PREM_CREDITS, self.__isPremCreditsBonusEnabled)
            self._premiumPlusCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.PLUS, results, replay))
            self._premiumPlusCreditsWithWotPlus.addRecords(self.__buildCreditsReplayForWotPlus(PREMIUM_TYPE.PLUS, results, replay))
        else:
            LOG_ERROR('Credits replay is not found', results)
        if 'goldReplay' in results and results['goldReplay'] is not None:
            replay = ValueReplay(connector, recordName='gold', replay=results['goldReplay'])
            self._goldRecords.addRecords(records.ReplayRecords(replay, 'gold'))
        else:
            LOG_ERROR('Gold replay is not found', results)
        self._additionalRecords.addRecords(_AdditionalRecords(results))
        return

    def _addXPResults(self, connector, results):
        premiumType = results.get('premMask', PREMIUM_TYPE.NONE)
        hasPremiumPlus = bool(premiumType & PREMIUM_TYPE.PLUS)
        if 'xpReplay' in results and results['xpReplay'] is not None:
            replay = ValueReplay(connector, recordName='xp', replay=results['xpReplay'])
            _updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            isHighScope = RECORD_DB_IDS[('max15x15', 'maxXP')] in [ recordID for recordID, _ in results.get('dossierPopUps', []) ]
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._baseXPWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._premiumXPWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._premiumPlusXPWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=hasPremiumPlus)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._baseXPAddWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._premiumXPAddWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self._premiumPlusXPAddWithWotPlus.addRecords(self.__buildXPReplayForWotPlus(isHighScope, results, replay))
        else:
            LOG_ERROR('XP replay is not found', results)
        if 'freeXPReplay' in results and results['freeXPReplay'] is not None:
            replay = ValueReplay(connector, recordName='freeXP', replay=results['freeXPReplay'])
            _updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._baseFreeXPWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._premiumFreeXPWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._premiumPlusFreeXPWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=hasPremiumPlus)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._baseFreeXPAddWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._premiumFreeXPAddWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
            _updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self._premiumPlusFreeXPAddWithWotPlus.addRecords(self.__buildFreeXPReplayForWotPlus(results, replay))
        else:
            LOG_ERROR('Free XP replay is not found', results)
        return

    def _addCrystalResults(self, connector, results):
        if 'crystalReplay' in results and results['crystalReplay'] is not None:
            replay = ValueReplay(connector, recordName=Currency.CRYSTAL, replay=results['crystalReplay'])
            self._crystal.addRecords(records.ReplayRecords(replay, Currency.CRYSTAL))
            self._crystalDetails.addRecords(_CrystalRecords(replay, results))
        else:
            LOG_ERROR('crystalReplay is not found', results)
        return

    def __buildCreditsReplayForPremType(self, targetPremiumType, results, replay):
        initialSquadFactor = results['premSquadCreditsFactor100']
        squadCreditsFactor = self.__getPremiumSquadCreditsFactor(results, targetPremiumType)
        results['premSquadCreditsFactor100'] = squadCreditsFactor
        creditsReplayToUse = _CreditsReplayRecords(replay, results, squadCreditsFactor)
        results['premSquadCreditsFactor100'] = initialSquadFactor
        return creditsReplayToUse

    def __buildCreditsReplayForWotPlus(self, targetPremiumType, results, replay):
        initialWotPlusCreditsFactor = results['wotPlusCreditsFactor100']
        results['wotPlusCreditsFactor100'] = self.__getWotPlusFactor('creditsFactor')
        creditsReplayToUse = self.__buildCreditsReplayForPremType(targetPremiumType, results, replay)
        results['wotPlusCreditsFactor100'] = initialWotPlusCreditsFactor
        return creditsReplayToUse

    def __buildXPReplayForWotPlus(self, isHighScope, results, replay):
        initialWotPlusXPFactor = results['wotPlusXPFactor100']
        results['wotPlusXPFactor100'] = self.__getWotPlusFactor('xpFactor')
        xpReplayToUse = _XPReplayRecords(replay, isHighScope, results['achievementXP'])
        results['wotPlusXPFactor100'] = initialWotPlusXPFactor
        return xpReplayToUse

    def __buildFreeXPReplayForWotPlus(self, results, replay):
        initialWotPlusFreeXPFactor = results['wotPlusFreeXPFactor100']
        results['wotPlusFreeXPFactor100'] = self.__getWotPlusFactor('freeXPFactor')
        freeXPReplayToUse = _FreeXPReplayRecords(replay, results['achievementFreeXP'])
        results['wotPlusFreeXPFactor100'] = initialWotPlusFreeXPFactor
        return freeXPReplayToUse

    def __updatePremiumXPFactor(self, replay, results, premType=PREMIUM_TYPE.NONE):
        if 'appliedPremiumXPFactor100' not in replay:
            return
        if premType == PREMIUM_TYPE.PLUS:
            replay['appliedPremiumXPFactor100'] = _getPremiumBonusFactor(results['premiumPlusXPFactor100'], _CAPS.PREM_XP, self.__isPremXpBonusEnabled)
        elif premType == PREMIUM_TYPE.BASIC:
            replay['appliedPremiumXPFactor100'] = _getPremiumBonusFactor(results['premiumXPFactor100'], _CAPS.PREM_XP, self.__isPremXpBonusEnabled)
        else:
            replay['appliedPremiumXPFactor100'] = FACTOR_VALUE.BASE_XP_FACTOR

    @staticmethod
    @dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
    def __getPremiumSquadCreditsFactor(results, targetPremiumType, lobbyContext=None):
        premiumType = PREMIUM_TYPE.activePremium(results.get('premMask', PREMIUM_TYPE.NONE))
        if targetPremiumType > premiumType:
            return lobbyContext.getServerSettings().squadPremiumBonus.ownCredits * 100
        return 0 if targetPremiumType < premiumType else results.get('premSquadCreditsFactor100', 0)

    @staticmethod
    @dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
    def __getWotPlusFactor(factorName, lobbyContext=None):
        return lobbyContext.getServerSettings().getWotPlusBattleBonusesConfig().get(factorName, 0.0) * 100 if lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled() else 0.0

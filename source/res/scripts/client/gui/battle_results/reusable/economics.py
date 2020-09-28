# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/economics.py
import typing
import itertools
from collections import namedtuple
from battle_results_shared import VEH_FULL_RESULTS
from constants import PREMIUM_TYPE, ARENA_BONUS_TYPE
from gui.battle_results.reusable import shared
from gui.battle_results.reusable import records
from gui.battle_results.br_constants import PremiumState, FactorValue
from gui.shared.money import Currency
from debug_utils import LOG_ERROR
from dossiers2.custom.records import RECORD_DB_IDS
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from ValueReplay import ValueReplay, ValueReplayConnector
_CrystalDetails = namedtuple('_CrystalDetails', ('earned', 'expenses'))

def _createCrystalDetails(earned=None, expenses=0):
    earned = earned if earned is not None else []
    return _CrystalDetails(earned=earned, expenses=expenses)


class _AdditionalRecords(records.RawRecords):
    __slots__ = ()

    def __init__(self, results):
        rawRecords = {}
        repairCost = results.get('autoRepairCost')
        if repairCost is not None:
            rawRecords['autoRepairCost'] = -repairCost
        autoLoadCost = results.get('autoLoadCost')
        if autoLoadCost is not None:
            rawRecords['autoLoadCredits'] = -autoLoadCost[0]
            rawRecords['autoLoadGold'] = -autoLoadCost[1]
        boostersCost = results.get('autoEquipBoostersCost')
        if boostersCost is not None:
            rawRecords['autoBoostersCredits'] = -boostersCost[0]
            rawRecords['autoBoostersGold'] = -boostersCost[1]
            rawRecords['autoBoostersCrystal'] = -boostersCost[2]
        equipCost = results.get('autoEquipCost')
        if equipCost is not None:
            rawRecords['autoEquipCredits'] = self.__getAutoEquipCost(equipCost, boostersCost, 0)
            rawRecords['autoEquipGold'] = self.__getAutoEquipCost(equipCost, boostersCost, 1)
        if 'piggyBank' in results:
            cost = results['piggyBank']
            if cost is not None:
                rawRecords['piggyBank'] = cost
        super(_AdditionalRecords, self).__init__(rawRecords)
        return

    @classmethod
    def __getAutoEquipCost(cls, equipCost, boosterCost, idx):
        return -equipCost[idx] if boosterCost is None else -equipCost[idx] + boosterCost[idx]


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


class _EconomicsRecordsChains(object):
    __slots__ = ('_baseCredits', '_premiumCredits', '_premiumPlusCredits', '_goldRecords', '_additionalRecords', '_baseXP', '_premiumXP', '_premiumPlusXP', '_baseXPAdd', '_premiumXPAdd', '_premiumPlusXPAdd', '_baseFreeXP', '_premiumFreeXP', '_premiumPlusFreeXP', '_baseFreeXPAdd', '_premiumFreeXPAdd', '_premiumPlusFreeXPAdd', '_crystal', '_crystalDetails')

    def __init__(self):
        super(_EconomicsRecordsChains, self).__init__()
        self._baseCredits = records.RecordsIterator()
        self._premiumCredits = records.RecordsIterator()
        self._premiumPlusCredits = records.RecordsIterator()
        self._goldRecords = records.RecordsIterator()
        self._additionalRecords = records.RecordsIterator()
        self._baseXP = records.RecordsIterator()
        self._premiumXP = records.RecordsIterator()
        self._premiumPlusXP = records.RecordsIterator()
        self._baseXPAdd = records.RecordsIterator()
        self._premiumXPAdd = records.RecordsIterator()
        self._premiumPlusXPAdd = records.RecordsIterator()
        self._baseFreeXP = records.RecordsIterator()
        self._premiumFreeXP = records.RecordsIterator()
        self._premiumPlusFreeXP = records.RecordsIterator()
        self._baseFreeXPAdd = records.RecordsIterator()
        self._premiumFreeXPAdd = records.RecordsIterator()
        self._premiumPlusFreeXPAdd = records.RecordsIterator()
        self._crystal = records.RecordsIterator()
        self._crystalDetails = _createCrystalDetails()

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

    def getMoneyRecords(self, premiumType=PREMIUM_TYPE.NONE):
        if premiumType == PREMIUM_TYPE.NONE or premiumType & (PREMIUM_TYPE.VIP | PREMIUM_TYPE.PLUS):
            resultPremiumData = self._premiumPlusCredits
        else:
            resultPremiumData = self._premiumCredits
        return itertools.izip(self._baseCredits, resultPremiumData, self._goldRecords, self._additionalRecords)

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
            else:
                secondXPData = self._premiumPlusXP
                secondFreeXPData = self._premiumPlusFreeXP
        elif addBonusApplied:
            secondXPData = self._premiumXPAdd
            secondFreeXPData = self._premiumFreeXPAdd
        else:
            secondXPData = self._premiumXP
            secondFreeXPData = self._premiumFreeXP
        if addBonusApplied:
            firstXPData = self._baseXPAdd
            firstFreeXPData = self._baseFreeXPAdd
        else:
            firstXPData = self._baseXP
            firstFreeXPData = self._baseFreeXP
        return itertools.izip(firstXPData, secondXPData, firstFreeXPData, secondFreeXPData)

    def getXPDiff(self):
        return self._premiumXP.getRecord('xp') - self._baseXP.getRecord('xp')

    def addResults(self, _, results):
        connector = ValueReplayConnector(VEH_FULL_RESULTS, results)
        self._addMoneyResults(connector, results)
        self._addXPResults(connector, results)
        self._addCrystalResults(connector, results)

    def _addMoneyResults(self, connector, results):
        if 'creditsReplay' in results and results['creditsReplay'] is not None:
            replay = ValueReplay(connector, recordName='credits', replay=results['creditsReplay'])
            appliedPremiumCreditsFactor100Exists = 'appliedPremiumCreditsFactor100' in replay
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = FactorValue.BASE_CREDITS_FACTOR
            self._baseCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.NONE, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = results['premiumCreditsFactor100']
            self._premiumCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.BASIC, results, replay))
            if appliedPremiumCreditsFactor100Exists:
                replay['appliedPremiumCreditsFactor100'] = results['premiumPlusCreditsFactor100']
            self._premiumPlusCredits.addRecords(self.__buildCreditsReplayForPremType(PREMIUM_TYPE.PLUS, results, replay))
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
        if 'xpReplay' in results and results['xpReplay'] is not None:
            replay = ValueReplay(connector, recordName='xp', replay=results['xpReplay'])
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            isHighScope = RECORD_DB_IDS[('max15x15', 'maxXP')] in [ recordID for recordID, _ in results.get('dossierPopUps', []) ]
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXP.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusXPAdd.addRecords(_XPReplayRecords(replay, isHighScope, results['achievementXP']))
        else:
            LOG_ERROR('XP replay is not found', results)
        if 'freeXPReplay' in results and results['freeXPReplay'] is not None:
            replay = ValueReplay(connector, recordName='freeXP', replay=results['freeXPReplay'])
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=True)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXP.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updateAdditionalFactorFromReplay(replay, results, setDefault=False)
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE)
            self._baseFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.BASIC)
            self._premiumFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
            self.__updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.PLUS)
            self._premiumPlusFreeXPAdd.addRecords(_FreeXPReplayRecords(replay, results['achievementFreeXP']))
        else:
            LOG_ERROR('Free XP replay is not found', results)
        return

    def _addCrystalResults(self, connector, results):
        if 'crystalReplay' in results and results['crystalReplay'] is not None:
            replay = ValueReplay(connector, recordName=Currency.CRYSTAL, replay=results['crystalReplay'])
            self._crystal.addRecords(records.ReplayRecords(replay, Currency.CRYSTAL))
            self._addCrystalDetails(replay)
        else:
            LOG_ERROR('crystal replay is not found', results)
        return

    def _addCrystalDetails(self, replay):
        medalToken = 'eventCrystalList_'
        crystalDetails = []
        for _, (appliedName, appliedValue), (_, _) in replay:
            if appliedName == 'originalCrystal' and appliedValue:
                crystalDetails.insert(0, (appliedName, appliedValue))
            if appliedName.startswith(medalToken):
                achievementName = appliedName.split(medalToken)[1]
                crystalDetails.append((achievementName, appliedValue))

        autoBoosters = self._additionalRecords.getRecord('autoBoostersCrystal', 0)
        self._crystalDetails = _createCrystalDetails(crystalDetails, autoBoosters)

    def __buildCreditsReplayForPremType(self, targetPremiumType, results, replay):
        initialSquadFactor = results['premSquadCreditsFactor100']
        squadCreditsFactor = self.__getPremiumSquadCreditsFactor(results, targetPremiumType)
        results['premSquadCreditsFactor100'] = squadCreditsFactor
        creditsReplayToUse = _CreditsReplayRecords(replay, results, squadCreditsFactor)
        results['premSquadCreditsFactor100'] = initialSquadFactor
        return creditsReplayToUse

    @staticmethod
    def __updateAdditionalFactorFromReplay(replay, results, setDefault=False):
        if 'additionalXPFactor10' not in replay:
            return
        if setDefault:
            if 'dailyXPFactor10' in replay:
                replay['additionalXPFactor10'] = FactorValue.ADDITIONAL_BONUS_ZERO_FACTOR
            else:
                replay['additionalXPFactor10'] = FactorValue.ADDITIONAL_BONUS_ONE_FACTOR
        else:
            replay['additionalXPFactor10'] = results['additionalXPFactor10']

    @staticmethod
    def __updatePremiumXPFactor(replay, results, premType=PREMIUM_TYPE.NONE):
        if 'appliedPremiumXPFactor100' not in replay:
            return
        if premType == PREMIUM_TYPE.PLUS:
            replay['appliedPremiumXPFactor100'] = results['premiumPlusXPFactor100']
        elif premType == PREMIUM_TYPE.BASIC:
            replay['appliedPremiumXPFactor100'] = results['premiumXPFactor100']
        else:
            replay['appliedPremiumXPFactor100'] = FactorValue.BASE_XP_FACTOR

    @staticmethod
    @dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
    def __getPremiumSquadCreditsFactor(results, targetPremiumType, lobbyContext=None):
        premiumType = PREMIUM_TYPE.activePremium(results.get('premMask', PREMIUM_TYPE.NONE))
        if targetPremiumType > premiumType:
            return lobbyContext.getServerSettings().squadPremiumBonus.ownCredits * 100
        return 0 if targetPremiumType < premiumType else results.get('premSquadCreditsFactor100', 0)


class EconomicsInfo(shared.UnpackedInfo):
    __slots__ = ('__isAddXPBonusApplied', '__premiumMask', '__premiumState', '__premiumPlusState', '_economicsRecords')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, personal):
        super(EconomicsInfo, self).__init__()
        self.__isAddXPBonusApplied = False
        self.__premiumMask = 0
        self.__premiumState = PremiumState.NONE
        self.__premiumPlusState = PremiumState.NONE
        self._economicsRecords = _EconomicsRecordsChains()
        if not self.hasUnpackedItems():
            self.__collectRequiredData(personal)

    @property
    def hasAnyPremium(self):
        return bool(self.__premiumMask & PREMIUM_TYPE.ANY)

    @property
    def isPremium(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.BASIC)

    @property
    def isPremiumPlus(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.PLUS)

    @property
    def isPremiumVIP(self):
        return bool(PREMIUM_TYPE.activePremium(self.__premiumMask) & PREMIUM_TYPE.VIP)

    @property
    def isAddXPBonusApplied(self):
        return self.__isAddXPBonusApplied

    @isAddXPBonusApplied.setter
    def isAddXPBonusApplied(self, state):
        self.__isAddXPBonusApplied = state

    @property
    def premiumState(self):
        return self.__premiumState

    @premiumState.setter
    def premiumState(self, state):
        self.__premiumState = state

    @property
    def premiumPlusState(self):
        return self.__premiumPlusState

    @premiumPlusState.setter
    def premiumPlusState(self, state):
        self.__premiumPlusState = state

    @property
    def isPremiumBought(self):
        return self.__premiumState & PremiumState.BOUGHT > 0

    @property
    def isPremiumPlusBought(self):
        return self.__premiumPlusState & PremiumState.BOUGHT > 0

    @property
    def isPostBattlePremium(self):
        return self.isPremium or self.isPremiumBought

    @property
    def isPostBattlePremiumPlus(self):
        return self.isPremiumPlus or self.isPremiumPlusBought

    def isActivePremiumPlus(self):
        return self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)

    def getAppliedAdditionalCount(self):
        return self.__itemsCache.items.stats.applyAdditionalXPCount

    def canUpgradeToPremium(self, arenaBonusType):
        return self.__premiumState & PremiumState.BUY_ENABLED > 0 and self.__premiumState & PremiumState.HAS_ALREADY == 0 and not self.isPostBattlePremium and arenaBonusType in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.EPIC_BATTLE)

    def canUpgradeToPremiumPlus(self, arenaBonusType):
        return self.__premiumPlusState & PremiumState.BUY_ENABLED > 0 and self.__premiumPlusState & PremiumState.HAS_ALREADY == 0 and not self.isPostBattlePremiumPlus and arenaBonusType in (ARENA_BONUS_TYPE.REGULAR, ARENA_BONUS_TYPE.EPIC_RANDOM, ARENA_BONUS_TYPE.EPIC_BATTLE)

    def getPremiumType(self):
        premiumType = PREMIUM_TYPE.NONE
        if self.isPremiumPlus:
            premiumType = PREMIUM_TYPE.PLUS
        elif self.isPremium:
            premiumType = PREMIUM_TYPE.BASIC
        return premiumType

    def getActivePremiumType(self):
        hasPremiumPlus = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        hasBasicPremium = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.BASIC)
        premiumType = PREMIUM_TYPE.NONE
        if hasPremiumPlus:
            premiumType = PREMIUM_TYPE.PLUS
        elif hasBasicPremium:
            premiumType = PREMIUM_TYPE.BASIC
        return premiumType

    def getBaseCreditsRecords(self):
        return self._economicsRecords.getBaseCreditsRecords()

    def getPremiumCreditsRecords(self):
        return self._economicsRecords.getPremiumCreditsRecords()

    def getCreditsDiff(self):
        return self._economicsRecords.getCreditsDiff()

    def getMoneyRecords(self):
        return self._economicsRecords.getMoneyRecords(self.__premiumMask)

    def getCrystalRecords(self):
        return self._economicsRecords.getCrystalRecords()

    def getUnpackedCrystalRecords(self):
        return self._economicsRecords.getUnpackedCrystalRecords()

    def haveCrystalsChanged(self):
        return self._economicsRecords.haveCrystalsChanged()

    def getBaseXPRecords(self):
        return self._economicsRecords.getBaseXPRecords()

    def getPremiumXPRecords(self):
        return self._economicsRecords.getPremiumXPRecords()

    def getPremiumXPAddRecords(self):
        return self._economicsRecords.getPremiumXPAddRecords()

    def getXPRecords(self):
        return self._economicsRecords.getXPRecords(self.__premiumMask, self.__isAddXPBonusApplied)

    def getXPDiff(self):
        return self._economicsRecords.getXPDiff()

    def getCrystalDetails(self):
        return self._economicsRecords.getCrystalDetails()

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

    def __collectRequiredData(self, info):
        getItemByCD = self.__itemsCache.items.getItemByCD
        itemCDs = [ key for key in info.keys() if isinstance(key, int) ]
        items = sorted((getItemByCD(itemCD) for itemCD in itemCDs))
        for item in items:
            intCD = item.intCD
            data = info[intCD]
            if data is None:
                self._addUnpackedItemID(intCD)
                continue
            self._economicsRecords.addResults(intCD, data)
            self.__premiumMask = data.get('premMask', PREMIUM_TYPE.NONE)

        return

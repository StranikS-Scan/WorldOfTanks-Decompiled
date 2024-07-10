# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/premium_plus.py
from constants import PREMIUM_TYPE
from gui.battle_results.pbs_helpers.additional_bonuses import getAdditionalXpBonusStatus, getAdditionalXPFactor10FromResult, getLeftAdditionalBonus, isAdditionalXpBonusAvailable, isAddXpBonusStatusAcceptable, getAdditionalXpBonusDiff
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.premium_plus_model import PremiumXpBonusRestriction
from helpers import dependency, time_utils
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from shared_utils import first

class PremiumPlus(IBattleResultsPacker):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    @classmethod
    def packModel(cls, model, battleResults):
        reusable = battleResults.reusable
        hasPremiumPlus = cls.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        model.setHasPremium(hasPremiumPlus)
        arenaUniqueID = reusable.arenaUniqueID
        isXpBonusAvailable = cls._getXpAdditionalBonusStatus(arenaUniqueID, reusable, hasPremiumPlus)
        model.setIsXpBonusEnabled(isXpBonusAvailable)
        if not isXpBonusAvailable:
            model.setRestriction(PremiumXpBonusRestriction.NORESTRICTION)
            return
        wasPremiumPlusInBattle = reusable.personal.isPremiumPlus
        model.setWasPremium(wasPremiumPlusInBattle)
        hasWotPlus = cls.__wotPlusController.isEnabled()
        cls._updateLeftCount(model, wasPremiumPlusInBattle, hasPremiumPlus, hasWotPlus)
        model.setBonusMultiplier(getAdditionalXPFactor10FromResult(battleResults.results[_RECORD.PERSONAL], reusable))
        isPersonalTeamWin = reusable.isPersonalTeamWin()
        _, vehicle = first(reusable.personal.getVehicleItemsIterator())
        vehicleCD = vehicle.intCD
        addXpBonusStatus = getAdditionalXpBonusStatus(arenaUniqueID, isPersonalTeamWin, vehicleCD, isXpBonusAvailable)
        model.setRestriction(addXpBonusStatus)
        model.setXpDiff(getAdditionalXpBonusDiff(arenaUniqueID))

    @classmethod
    def updateModel(cls, model, battleResults, ctx=None, isFullUpdate=True):
        if isFullUpdate:
            cls.packModel(model, battleResults)
            return
        else:
            isBonusApplied = ctx.get('isBonusApplied', True) if ctx is not None else True
            if not isBonusApplied:
                model.setRestriction(PremiumXpBonusRestriction.NOTAPPLYINGERROR)
            else:
                cls.packModel(model, battleResults)
            return

    @classmethod
    def _updateLeftCount(cls, model, wasPremiumPlusInBattle, hasPremiumPlus, hasWotPlus):
        hasAccessToAdditionalBonus, leftCount, _ = getLeftAdditionalBonus(hasWotPlus, hasPremiumPlus)
        timeLeft = time_utils.getDayTimeLeft() if leftCount == 0 and hasAccessToAdditionalBonus else -1
        model.setNextBonusTime(timeLeft)
        model.setLeftBonusCount(leftCount)

    @classmethod
    def _getXpAdditionalBonusStatus(cls, arenaUniqueID, reusable, hasPremiumPlus):
        return isAdditionalXpBonusAvailable(arenaUniqueID, reusable, hasPremiumPlus, isAddXpBonusStatusAcceptable)

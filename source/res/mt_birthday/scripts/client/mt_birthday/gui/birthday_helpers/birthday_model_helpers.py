# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_helpers/birthday_model_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from helpers import dependency
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker
from mt_birthday.gui.birthday_bonus_packers import BirthdayEntitlementBonusUIPacker, BirthdayTmanBonusUIPacker, BirthdayVehiclesBonusUIPacker
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday_common.constants import MT_BIRTHDAY_INFINITY_COMPLETE_TOKEN
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from typing import Dict
_BONUSES_ORDER = ('vehicles',
 'lootBoxToken',
 Currency.CRYSTAL,
 Currency.GOLD,
 'premium',
 'premium_plus',
 'tmanToken',
 'customizations',
 'goodies',
 'crewBooks',
 Currency.CREDITS,
 'entitlements',
 'items',
 'dossier')
_MAX_LEN_MAIN_REWARDS = 3

def birthdayBonusesSortKeyFunc(bonus):
    bonusName = bonus.getName()
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)


def getBirthdayBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'entitlements': BirthdayEntitlementBonusUIPacker,
     'tmanToken': BirthdayTmanBonusUIPacker,
     'vehicles': BirthdayVehiclesBonusUIPacker})
    return BonusUIPacker(mapping)


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def fillChapterLevelsModel(model, birthdayController=None, tooltipData=None):
    currentLevel, _ = birthdayController.progression.getCurrentProgressionLevel()
    if currentLevel is None:
        return
    else:
        levelModels = model.getLevels()
        levelModels.clear()
        levelsCount = len(birthdayController.progression.progressionConfig)
        for levelID in range(1, levelsCount + 1):
            levelModel = model.getLevelsType()()
            with levelModel.transaction() as tx:
                tx.setNumber(levelID)
                tx.setIsCompleted(currentLevel > levelID)
                _fillLevelRewardModels(tx, levelID, birthdayController, tooltipData)
            levelModels.addViewModel(levelModel)

        levelModels.invalidate()
        return


def _fillLevelRewardModels(levelModel, levelID, birthdayCtrl, tooltipData=None):
    levelRewards = birthdayCtrl.progression.progressionConfig.get(levelID, {}).get('bonuses')
    levelRewards.sort(key=birthdayBonusesSortKeyFunc)
    packer = getBirthdayBonusPacker()
    rewardsModel = levelModel.getRewards()
    rewardsModel.clear()
    packBonusModelAndTooltipData(levelRewards, rewardsModel, tooltipData=tooltipData, packer=packer)
    rewardsModel.invalidate()


def battleTokenFilter(bonus):
    if bonus.getName() == 'battleToken':
        value = bonus.getValue()
        if value.get(MT_BIRTHDAY_INFINITY_COMPLETE_TOKEN):
            return False
    return True


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def makeRewardModels(bonuses, mainRewards, otherRewards, tooltipData=None, birthdayController=None):
    bonuses = [ bonus for bonus in bonuses if battleTokenFilter(bonus) ]
    bonuses.sort(key=birthdayBonusesSortKeyFunc)
    packer = getBirthdayBonusPacker()
    mainBonuses = bonuses[:_MAX_LEN_MAIN_REWARDS]
    otherBonuses = bonuses[_MAX_LEN_MAIN_REWARDS:]
    if len(mainBonuses) == _MAX_LEN_MAIN_REWARDS:
        mainBonuses[0], mainBonuses[1] = mainBonuses[1], mainBonuses[0]
    packBonusModelAndTooltipData(mainBonuses, mainRewards, packer=packer, tooltipData=tooltipData)
    packBonusModelAndTooltipData(otherBonuses, otherRewards, packer=packer, tooltipData=tooltipData)
    mainRewards.invalidate()
    otherRewards.invalidate()


def entProcessor(rewardsData, rewardTemplate, makeQuestsAchieve):
    entitlements = rewardsData.get('entitlements', {})
    for entitlement, data in entitlements.iteritems():
        count = data.get('count', 0)
        if count > 0:
            return makeQuestsAchieve(rewardTemplate, text=backport.text(R.strings.messenger.serviceChannelMessages.epicReward.dyn(entitlement)()), count=count)

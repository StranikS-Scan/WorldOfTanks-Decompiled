# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_mission_bonuses_packers.py
import copy
import logging
from functools import partial
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_reward_item_model import Pm3RewardItemModel
from gui.selectable_reward.common import PersonalMissionsSelectableRewardManager
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events.bonuses import PersonalMissionsSelectTokensBonus
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap
from helpers import dependency
from personal_missions_constants import PM3_SELECT_BONUS_NAME
from shared_utils import first
from skeletons.gui.offers import IOffersDataProvider
import gui.server_events.bonuses as serverBonuses
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from account_helpers.offers.events_data import OfferEventData
    from gui.impl.backport import TooltipData
_logger = logging.getLogger(__name__)

def getPersonalMissionsBonusPackersMap():
    mapping = getDefaultBonusPackersMap()
    selectBonusPacker = SelectBonusPacker()
    mapping.update({'selectableBonus': selectBonusPacker,
     PM3_SELECT_BONUS_NAME: selectBonusPacker})
    return mapping


def getPersonalMissionsBonusPacker():
    mapping = getPersonalMissionsBonusPackersMap()
    return BonusUIPacker(mapping)


def getOfferTokenByGift(tokenID):
    return tokenID.replace('_gift', '')


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None, offersDataProvider=None, selectedRewards=None):
    if packer is None:
        packer = getPersonalMissionsBonusPacker()
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    if offersDataProvider is not None:
        bonuses = _getUpdatedSelectableBonuses(bonuses, offersDataProvider, selectedRewards)
    bonusModelsList.clear()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1

    return


def _getUpdatedSelectableBonuses(bonuses, offersDataProvider, selectedRewards=None):
    resultBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        if bonus.isShowInGUI() and (bonusName == PM3_SELECT_BONUS_NAME or bonusName == SELECTABLE_BONUS_NAME):
            tokens = bonus.getTokens()
            bonusCount = bonus.getCount()
            for tokenId in tokens.iterkeys():
                offerToken = getOfferTokenByGift(tokenId)
                offer = offersDataProvider.getOfferByToken(offerToken)
                if offer is None:
                    continue
                offerDataGifts = offersDataProvider.getReceivedGifts(offer.id)
                for giftId, countGift in offerDataGifts.iteritems():
                    if countGift > bonusCount:
                        countGift = bonusCount
                    gift = offer.getGift(giftId)
                    item = first(gift.rawBonuses.get('items', {}).keys())
                    if item is not None:
                        if selectedRewards is not None and item in selectedRewards:
                            __addNewPM3SelectTokensBonusToList(resultBonuses, bonus, countGift, True)
                        else:
                            resultBonuses.append(serverBonuses.ItemsBonus(name='items', value={item: countGift}))
                    bonusCount -= countGift

            if bonusCount != 0:
                __addNewPM3SelectTokensBonusToList(resultBonuses, bonus, bonusCount, False)
        resultBonuses.append(bonus)

    return resultBonuses


def __addNewPM3SelectTokensBonusToList(bonusList, bonus, newCount, isShowAnimation):
    value = copy.deepcopy(bonus.getValue())
    value[first(value.keys())]['count'] = newCount
    newBonus = serverBonuses.PersonalMissionsSelectTokensBonus(value, bonus.isCompensation(), bonus.getContext())
    newBonus.setIsShowAnimation(isShowAnimation)
    bonusList.append(newBonus)


class SelectBonusPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __selectableRewardManager = PersonalMissionsSelectableRewardManager

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = Pm3RewardItemModel()
        bonusType = bonus.getType()
        model.setName(bonus.getName())
        labelResId = R.strings.selectable_reward.tabs.items.dyn(bonusType)()
        if labelResId > 0:
            model.setLabel(backport.text(labelResId))
        model.setIcon(bonusType)
        model.setBigIcon(bonusType)
        isShowAnimation = bonus.getIsShowAnimation()
        model.setIsShowAnimation(isShowAnimation)
        questId = cls.getId(bonus)
        model.setId(questId)
        isAvailableToken = bool(cls.__selectableRewardManager.getAvailableSelectableBonuses(partial(cls.__isValidReward, questId)))
        model.setValue(str(cls.getValue(bonus, isAvailableToken, isShowAnimation)))
        model.setIsChooseReward(isAvailableToken and not isShowAnimation)
        model.setUserName(backport.text(R.strings.personal_missions_3.selectBonus.dyn(bonusType)()))
        return model

    @classmethod
    def getValue(cls, bonus, isAvailableToken, isShowAnimation):
        giftTokenName = first(bonus.getTokens().keys())
        offer = cls.__offersProvider.getOfferByToken(getOfferTokenByGift(giftTokenName))
        return bonus.getCount() if offer is None or not isAvailableToken or isShowAnimation else offer.availableTokens

    @classmethod
    def getId(cls, bonus):
        giftTokenName = first(bonus.getTokens().keys())
        return int(giftTokenName.split(':')[-1])

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            tooltipData.append(createTooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.PM3_GIFT_TOKEN, specialArgs=[tokenID] + [bonus.getContext().get('isReceived', True)]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for _ in bonus.getTokens().iterkeys():
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @staticmethod
    def __isValidReward(questId, tokenID):
        if not questId:
            return True
        tokenQuestID = tokenID.split(':')[-1]
        return int(tokenQuestID) == questId

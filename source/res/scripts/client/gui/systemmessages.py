# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/SystemMessages.py
from collections import namedtuple
from enumerations import Enumeration
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
ResultMsg = namedtuple('ResultMsg', 'success userMsg sysMsgType msgPriority msgData auxData')
SM_TYPE = Enumeration('System message type', ['Error',
 'ErrorHeader',
 'ErrorSimple',
 'Warning',
 'WarningHeader',
 'Information',
 'InformationHeader',
 'GameGreeting',
 'PowerLevel',
 'FinancialTransactionWithGold',
 'FinancialTransactionWithGoldHeader',
 'FinancialTransactionWithCredits',
 'FortificationStartUp',
 'PurchaseForGold',
 'DismantlingForGold',
 'PurchaseForCredits',
 'Selling',
 'SellingForGold',
 'Remove',
 'MultipleSelling',
 'Repair',
 'CustomizationForGold',
 'CustomizationForCredits',
 'Restore',
 'PurchaseForCrystal',
 'PrimeTime',
 'PeriodicBattlesNotSet',
 'PeriodicBattlesAvailable',
 'DismantlingForCredits',
 'DismantlingForCrystal',
 'OpenEventBoards',
 'tokenWithMarkAcquired',
 'PaymentMethodLink',
 'PaymentMethodUnlink',
 'RecruitGift',
 'LootBoxes',
 'LootBoxRewards',
 'SkinCompensation',
 'FeatureSwitcherOn',
 'FeatureSwitcherOff',
 'DismantlingForDemountKit',
 'UpgradeForCredits',
 'BattlePassDefault',
 'BattlePassReward',
 'BattlePassBuy',
 'BattlePassSwitchChapter',
 'BattlePassActivateChapter',
 'PurchaseForEventCoin',
 'DismantlingForEventCoin',
 'OfferGiftBonuses',
 'PurchaseForBpcoin',
 'DismantlingForBpcoin',
 'PurchaseForMoney',
 'PaymentMethodLinkWgnc',
 'PaymentMethodUnlinkWgnc',
 'BattlePassGameModeEnabled',
 'ResearchVehiclePostProgressionSteps',
 'BuyPostProgressionModForCredits',
 'ChangeSlotCategory',
 'MediumInfo',
 'MessageHeader',
 'PurchaseForGoldAndCredits',
 'BattlePassExtraStart',
 'BattlePassExtraFinish',
 'BattlePassExtraWillEndSoon',
 'Comp7ShopItemsAvailableForRank',
 'ResourceWellStart',
 'ResourceWellEnd',
 'IntegratedAuctionOperation',
 'IntegratedAuctionRateError',
 'IntegratedAuctionBelowCompetitiveRate',
 'PurchaseForEquipCoin',
 'DismantlingForEquipCoin',
 'Deconstructing',
 'UpgradeForEquipCoins',
 'EventLootBoxStart',
 'EventLootBoxFinish',
 'EventLootBoxEnabled',
 'EventLootBoxDisabled',
 'DismantlingForFreeWotPlus',
 'CollectionStart',
 'CollectionsDisabled',
 'CollectionsEnabled',
 'SimpleGift',
 'NotEnoughBerthError',
 'FairplayViolation',
 'NotEnoughBerthWarning'])
CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.PurchaseForCredits,
 Currency.GOLD: SM_TYPE.PurchaseForGold,
 Currency.CRYSTAL: SM_TYPE.PurchaseForCrystal,
 Currency.EVENT_COIN: SM_TYPE.PurchaseForEventCoin,
 Currency.BPCOIN: SM_TYPE.PurchaseForBpcoin,
 Currency.EQUIP_COIN: SM_TYPE.PurchaseForEquipCoin}
CURRENCY_TO_SM_TYPE_DISMANTLING = {Currency.CREDITS: SM_TYPE.DismantlingForCredits,
 Currency.GOLD: SM_TYPE.DismantlingForGold,
 Currency.CRYSTAL: SM_TYPE.DismantlingForCrystal,
 Currency.EVENT_COIN: SM_TYPE.DismantlingForEventCoin,
 Currency.BPCOIN: SM_TYPE.DismantlingForBpcoin,
 Currency.EQUIP_COIN: SM_TYPE.DismantlingForEquipCoin}

def _getSystemMessages():
    return dependency.instance(ISystemMessages)


def pushMessage(text, type=SM_TYPE.Information, priority=None, messageData=None, savedData=None):
    _getSystemMessages().pushMessage(text, type, priority, messageData=messageData, savedData=savedData)


def pushMessagesFromResult(resultMsg):
    if resultMsg and resultMsg.userMsg:
        pushMessage(resultMsg.userMsg, type=resultMsg.sysMsgType, priority=resultMsg.msgPriority, messageData=resultMsg.msgData)
    if resultMsg and hasattr(resultMsg, 'auxData') and not isinstance(resultMsg.auxData, dict) and resultMsg.auxData:
        for m in resultMsg.auxData:
            pushMessage(m.userMsg, type=m.sysMsgType, priority=m.msgPriority, messageData=m.msgData)


def pushI18nMessage(key, *args, **kwargs):
    _getSystemMessages().pushI18nMessage(key, *args, **kwargs)

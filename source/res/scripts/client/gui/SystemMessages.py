# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/SystemMessages.py
from enumerations import Enumeration
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
SM_TYPE = Enumeration('System message type', ['Error',
 'ErrorHeader',
 'ErrorSimple',
 'Warning',
 'WarningHeader',
 'Information',
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
 'RankedBattlesAvailable',
 'DismantlingForCredits',
 'DismantlingForCrystal',
 'OpenEventBoards',
 'tokenWithMarkAcquired',
 'PaymentMethodLink',
 'PaymentMethodUnlink',
 'RecruitGift',
 'RecruitReminder',
 'LootBoxes',
 'LootBoxesGift',
 'NewYearEventStarted',
 'NewYearRewardsReminder',
 'LootBoxRewards'])
CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.PurchaseForCredits,
 Currency.GOLD: SM_TYPE.PurchaseForGold,
 Currency.CRYSTAL: SM_TYPE.PurchaseForCrystal}
CURRENCY_TO_SM_TYPE_DISMANTLING = {Currency.CREDITS: SM_TYPE.DismantlingForCredits,
 Currency.GOLD: SM_TYPE.DismantlingForGold,
 Currency.CRYSTAL: SM_TYPE.DismantlingForCrystal}

def _getSystemMessages():
    return dependency.instance(ISystemMessages)


def pushMessage(text, type=SM_TYPE.Information, priority=None, messageData=None, savedData=None):
    _getSystemMessages().pushMessage(text, type, priority, messageData=messageData, savedData=savedData)


def pushI18nMessage(key, *args, **kwargs):
    _getSystemMessages().pushI18nMessage(key, *args, **kwargs)

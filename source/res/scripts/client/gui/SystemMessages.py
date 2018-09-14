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
 'Remove',
 'Repair',
 'CustomizationForGold',
 'CustomizationForCredits',
 'Restore',
 'PurchaseForCrystal',
 'PrimeTime',
 'RankedBattlesAvailable'])
CURRENCY_TO_SM_TYPE = {Currency.CREDITS: SM_TYPE.PurchaseForCredits,
 Currency.GOLD: SM_TYPE.PurchaseForGold,
 Currency.CRYSTAL: SM_TYPE.PurchaseForCrystal}

def _getSystemMessages():
    return dependency.instance(ISystemMessages)


def pushMessage(text, type=SM_TYPE.Information, priority=None, messageData=None):
    _getSystemMessages().pushMessage(text, type, priority, messageData=messageData)


def pushI18nMessage(key, *args, **kwargs):
    _getSystemMessages().pushI18nMessage(key, *args, **kwargs)

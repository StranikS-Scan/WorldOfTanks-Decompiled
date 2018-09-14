# Embedded file name: scripts/client/gui/SystemMessages.py
from abc import ABCMeta, abstractmethod
from enumerations import Enumeration
SM_TYPE = Enumeration('System message type', ['Error',
 'Warning',
 'Information',
 'GameGreeting',
 'PowerLevel',
 'FinancialTransactionWithGold',
 'FinancialTransactionWithCredits',
 'FortificationStartUp',
 'PurchaseForGold',
 'DismantlingForGold',
 'PurchaseForCredits',
 'Selling',
 'Remove',
 'Repair',
 'CustomizationForGold',
 'CustomizationForCredits'])

class BaseSystemMessages(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def pushMessage(self, text, type = SM_TYPE.Information):
        pass

    @abstractmethod
    def pushI18nMessage(self, key, *args, **kwargs):
        pass


g_instance = None

def pushMessage(text, type = SM_TYPE.Information, priority = None):
    if g_instance:
        g_instance.pushMessage(text, type, priority)


def pushI18nMessage(key, *args, **kwargs):
    if g_instance:
        g_instance.pushI18nMessage(key, *args, **kwargs)

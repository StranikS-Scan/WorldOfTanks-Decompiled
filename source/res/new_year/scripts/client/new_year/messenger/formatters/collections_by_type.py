# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/messenger/formatters/collections_by_type.py
from ExtensionsManager import g_extensionsManager
from gui.shared.system_factory import registerMessengerClientFormatter, registerServiceChannelSubformatter
from messenger.formatters.service_channel import IInvoiceDataSubFormatter, InvoiceReceivedFormatter, QuestAchievesFormatter, IQuestAchievesSubformatter
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.messenger.formatters.service_channel import NewNYEventFormatter, NewYearInvoiceDataSubformatter, NewYearQuestAchievesSubFormatter
from new_year.messenger.formatters.token_quest_subformatters import registerNewYearTokenQuestsSubFormatters

def registerNewYearMessengerFormatters():
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE, NewNYEventFormatter())
    registerServiceChannelSubformatter((InvoiceReceivedFormatter, IInvoiceDataSubFormatter), NewYearInvoiceDataSubformatter())
    registerServiceChannelSubformatter((QuestAchievesFormatter, IQuestAchievesSubformatter), NewYearQuestAchievesSubFormatter)
    registerNewYearTokenQuestsSubFormatters()
    if g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
        from gui_lootboxes.messenger.formatters.collections_by_type import registerAutoBoxesSubFormatter
        import auto_boxes_subformatters
        registerAutoBoxesSubFormatter(auto_boxes_subformatters.NYGiftSystemSurpriseFormatter())
        registerAutoBoxesSubFormatter(auto_boxes_subformatters.LunarNYEnvelopeAutoOpenFormatter())
        registerAutoBoxesSubFormatter(auto_boxes_subformatters.NYPostEventSurpriseMachineFormatter())

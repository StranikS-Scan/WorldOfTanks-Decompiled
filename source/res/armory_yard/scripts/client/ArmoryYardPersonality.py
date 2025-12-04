# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/ArmoryYardPersonality.py
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from armory_yard.gui.Scaleform import registerArmoryYardScaleform, registerArmoryYardTooltipsBuilders
from armory_yard.gui.game_control import registerAYGameControllers, registerAYShopControllers, registerAYRerollControllers
from armory_yard.gui.shared.gui_items.items_actions import registerActions
from debug_utils import LOG_DEBUG
from gui.shared.system_factory import registerExtensionQuestsSources, registerQuestBuilder, registerMessengerServerFormatter, registerServiceChannelSubformatter
from messenger.formatters.service_channel import QuestAchievesFormatter, IQuestAchievesSubformatter
from armory_yard.gui.shared.formatters import AYProgressionQuestAchievesSubFormatter, AYCancelingRerollFormatter, AYDeferredRewardCollectingFormatter

def registerAYAdditionalSystemMessageTypes():
    from gui.SystemMessages import SM_TYPE
    SM_TYPE.inject(['ArmoryYardRerollTransactionForGold',
     'ArmoryYardRerollTransactionForCrystal',
     'ArmoryYardRerollTransactionForFreeReroll',
     'ArmoryYardRerollNotCompleted',
     'ArmoryYardReceivingAwards',
     'ArmoryYardInformationHeader',
     'ArmoryYardPostprogression',
     'ArmoryYardOpenChapter',
     'ArmoryYardMain',
     'ArmoryYardBundlePurchase',
     'FinancialTransactionWithGoldAndArmoryCoinsHeader',
     'FinancialTransactionWithArmoryCoinsHeader',
     'FinancialTransactionBuyAYCoins',
     'FinancialTransactionBuyAYFreeCoins'])


def preInit():
    registerAYAdditionalSystemMessageTypes()
    registerArmoryYardScaleform()
    registerArmoryYardTooltipsBuilders()
    registerAYGameControllers()
    registerAYShopControllers()
    registerAYRerollControllers()
    registerActions()
    from armory_yard.gui.server_events.events_helpers import ArmoryPlayerConditionQuestsSource
    registerExtensionQuestsSources((ArmoryPlayerConditionQuestsSource(),))
    from armory_yard.gui.shared.armory_dynamic_quest import ArmoryDynamicQuestBuilder
    registerQuestBuilder(ArmoryDynamicQuestBuilder, index=0)
    registerServiceChannelSubformatter((QuestAchievesFormatter, IQuestAchievesSubformatter), AYProgressionQuestAchievesSubFormatter)
    from armory_yard.messenger import registerArmoryYardNotificationListener
    registerArmoryYardNotificationListener()
    registerMessengerServerFormatter(_SM_TYPE.armoryYardRevertRerollMessage.index(), AYCancelingRerollFormatter())
    registerMessengerServerFormatter(_SM_TYPE.armoryYardDeferredRewardCollecting.index(), AYDeferredRewardCollectingFormatter())


def init():
    LOG_DEBUG('init', __name__)


def start():
    pass


def fini():
    pass

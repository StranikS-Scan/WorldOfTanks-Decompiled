# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WhiteTigerAccountComponent.py
import AccountCommands
import random
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG_DEV
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache
from gui.prb_control.dispatcher import g_prbLoader
from gui.ClientUpdateManager import g_clientUpdateManager
_HARRIERS = ['usa:A120_M48A5_hound_TLXXL',
 'france:F18_Bat_Chatillon25t_hound_TLXXL',
 'ussr:R97_Object_140_hound_TLXXL',
 'czech:Cz04_T50_51_Waf_Hound_3DSt']

class WhiteTigerAccountComponent(BaseAccountExtensionComponent):
    __wtController = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        BaseAccountExtensionComponent.__init__(self)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        events.onAccountBecomeNonPlayer += self.onBecomeNonPlayer
        self.__isFakeQueueSwitchEnabled = False

    def onBecomeNonPlayer(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        events.onAccountBecomeNonPlayer -= self.onBecomeNonPlayer

    def getWhiteTigerController(self):
        return self.__wtController

    def enqueueBattle(self, queueType, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (queueType, vehInvID))

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)

    def enableQueueSwitchSimulator(self):
        if IS_DEVELOPMENT:
            self.__isFakeQueueSwitchEnabled = True
            LOG_DEBUG_DEV('Queue simulator enabled')

    def __simulateRequeue(self, vehicleType):
        vehTypeCompDescr = vehicles.VehicleDescr(typeName=vehicleType).type.compactDescr
        data = self.__itemsCache.items.inventory.getItemData(vehTypeCompDescr)
        g_prbLoader.getDispatcher().getEntity().requeue(vehInvID=data.invID)

    def __onTokensUpdate(self, diff):
        if self.__isFakeQueueSwitchEnabled and IS_DEVELOPMENT:
            if 'wtevent:quick_ticket_boss' in diff.keys():
                self.__isFakeQueueSwitchEnabled = False
                self.__simulateRequeue('germany:G98_Waffentrager_E100_TLXXL')
                LOG_DEBUG_DEV('Try switching to Waffentrager queue - cheat disabled')
            elif 'wtevent:quick_ticket_hunter' in diff.keys():
                self.__isFakeQueueSwitchEnabled = False
                self.__simulateRequeue(random.choice(_HARRIERS))
                LOG_DEBUG_DEV('Try switching to random harrier queue - cheat disabled')
            return

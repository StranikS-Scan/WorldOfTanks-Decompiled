# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/awards_controller.py
from chat_shared import SYS_MESSAGE_TYPE
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.fun_gui_constants import SCH_CLIENT_MSG_TYPE
from fun_random.gui.impl.lobby.common.lootboxes import FEP_CATEGORY, FunRandomLootBoxTypes
from fun_random.gui.shared.event_dispatcher import showFunRandomLootBoxAwardWindow
from gui.game_control.AwardController import ServiceChannelHandler
from gui.server_events.bonuses import getMergedCompensatedBonuses
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

def _getMessage(ctx):
    _, message = ctx
    return message


class FunProgressionQuestsHandler(ServiceChannelHandler, FunProgressionWatcher):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.FUN_RANDOM_PROGRESSION

    def __init__(self, awardCtrl):
        super(FunProgressionQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(_getMessage(ctx), self._CLIENT_MSG_TYPE)

    def _needToShowAward(self, ctx):
        if super(FunProgressionQuestsHandler, self)._needToShowAward(ctx):
            return bool([ qID for qID in _getMessage(ctx).data.get('completedQuestIDs', set()) if self._funRandomCtrl.progressions.isProgressionExecutor(qID) ])
        return False


class FunRandomLootBoxAutoOpenHandler(ServiceChannelHandler, FunProgressionWatcher):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, awardCtrl):
        super(FunRandomLootBoxAutoOpenHandler, self).__init__(SYS_MESSAGE_TYPE.lootBoxesAutoOpenReward.index(), awardCtrl)
        self.__lootBoxData = None
        return

    def fini(self):
        self.__lootBoxData = None
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        super(FunRandomLootBoxAutoOpenHandler, self).fini()
        return

    def _showAward(self, ctx):
        self.__lootBoxData = _getMessage(ctx).data
        if not self.__lootBoxData:
            return
        if not self.itemsCache.isSynced():
            self.itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted
        else:
            self.__showAward()

    def __showAward(self):
        legendaryRewards = []
        otherRewards = []
        for lootboxID, lootboxData in self.__lootBoxData.iteritems():
            lb = self.itemsCache.items.tokens.getLootBoxByID(lootboxID)
            if lb and lb.getCategory() == FEP_CATEGORY:
                awardList = legendaryRewards if lb.getType() == FunRandomLootBoxTypes.LEGENDARY else otherRewards
                awardList.append(lootboxData.get('rewards', {}))

        if legendaryRewards:
            data = {'lootBoxType': FunRandomLootBoxTypes.LEGENDARY,
             'mainRewards': getMergedCompensatedBonuses(legendaryRewards),
             'addRewards': getMergedCompensatedBonuses(otherRewards)}
            showFunRandomLootBoxAwardWindow(data)

    def __onItemCacheSyncCompleted(self, *_):
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.__showAward()

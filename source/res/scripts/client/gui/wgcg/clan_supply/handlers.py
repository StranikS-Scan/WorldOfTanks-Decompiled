# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/clan_supply/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class ClanSupplyRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.CLAN_SUPPLY_GET_QUESTS: self.__getQuests,
         WebRequestDataType.CLAN_SUPPLY_POST_QUESTS: self.__postQuests,
         WebRequestDataType.CLAN_SUPPLY_CLAIM_QUESTS_REWARDS: self.__claimQuestRewards,
         WebRequestDataType.CLAN_SUPPLY_GET_PROGRESSION_SETTINGS: self.__getProgressionSettings,
         WebRequestDataType.CLAN_SUPPLY_GET_PROGRESSION_PROGRESS: self.__getProgressionProgress,
         WebRequestDataType.CLAN_SUPPLY_PURCHASE_PROGRESSION_STAGE: self.__purchaseProgressionStage}
        return handlers

    def __getQuests(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'get_clan_supply_quests'))

    def __postQuests(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'post_clan_supply_quests'))

    def __claimQuestRewards(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'claim_quest_rewards'))

    def __getProgressionSettings(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'get_progression_settings'))

    def __getProgressionProgress(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'get_progression_progress'))

    def __purchaseProgressionStage(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('clan_supply', 'purchase_progression_stage'), *ctx.getRequestArgs())

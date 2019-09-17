# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/quests/__init__.py
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from web_client_api import w2c, w2capi, Field, W2CSchema

class _QuestsSchema(W2CSchema):
    ids = Field(type=list)


@w2capi(name='user_data', key='action')
class QuestsWebApi(W2CSchema):
    _eventsCache = dependency.descriptor(IEventsCache)

    @w2c(_QuestsSchema, 'get_tokens')
    def handleGetTokens(self, command):
        tokens = self._eventsCache.questsProgress.getTokensData()
        if hasattr(command, 'ids') and command.ids:
            tokens = {k:v for k, v in tokens.iteritems() if k in command.ids}
        return {'token_list': tokens,
         'action': 'get_tokens'}

    @w2c(_QuestsSchema, 'get_quests')
    def handleGetQuests(self, command):
        quests = self._eventsCache.questsProgress.getQuestsData()
        if hasattr(command, 'ids') and command.ids:
            quests = {k:v for k, v in quests.iteritems() if k in command.ids}
        return {'quest_list': quests,
         'action': 'get_quests'}

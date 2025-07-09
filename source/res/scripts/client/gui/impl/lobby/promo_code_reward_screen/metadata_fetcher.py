# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/metadata_fetcher.py
import logging
import BigWorld
import ResMgr
from BWUtil import AsyncReturn
from gui.impl.lobby.promo_code_reward_screen import RewardScreenDescr
from helpers import getClientLanguage, dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_async, await_callback, wg_await
_logger = logging.getLogger(__name__)

class MetadataFetcher(object):

    @staticmethod
    def get(codeId):
        codeDescr = yield wg_await(MetadataFetcher.fetch(codeId))
        raise AsyncReturn(codeDescr)

    @staticmethod
    @wg_async()
    def fetch(codeId):
        lobbyContext = dependency.instance(ILobbyContext)
        filecache = BigWorld.player().customFilesCache
        fileserver = lobbyContext.getServerSettings().fileServer
        descriptorUrl = fileserver.getRewardScreensDescrsUrl(getClientLanguage())
        if not descriptorUrl:
            _logger.error('Error getting descriptor URL for promo code %s', codeId)
            raise AsyncReturn(None)
        _, content = yield await_callback(filecache.get)(descriptorUrl, headers={})
        if not content:
            _logger.error('Error fetching description for promo code %s', codeId)
            raise AsyncReturn(None)
        descrData = MetadataFetcher.__handleCodeDescrData(codeId, content)
        if descrData is None:
            _logger.error('There is not description for promo code %s', codeId)
            raise AsyncReturn(None)
        descr, title, subtitle, background, quests, questsDescr, tags = descrData
        defaultDescr = RewardScreenDescr(codeId, descr, title, subtitle, None, quests, questsDescr, tags)
        if not background:
            raise AsyncReturn(defaultDescr)
        backgroundUrl = fileserver.getRewardScreenBackgroundUrl(background)
        if not backgroundUrl:
            _logger.warning('Error getting decoration URL for reward screen %s', codeId)
            raise AsyncReturn(defaultDescr)
        raise AsyncReturn(RewardScreenDescr(codeId, descr, title, subtitle, backgroundUrl, quests, questsDescr, tags))
        return

    @staticmethod
    def __handleCodeDescrData(codeId, content):
        section = ResMgr.DataSection()
        section.createSectionFromString(content)
        if not section.has_key('root/reward_screens'):
            return
        codesSection = section['root/reward_screens']
        _, codeItem = findFirst(lambda (itemName, sub): itemName == 'item' and sub['id'].asString == codeId, codesSection.items(), default=(None, None))
        if codeItem is not None:
            codeId = codeItem['id'].asString
            description = codeItem.readString('description') if codeItem.has_key('description') else ''
            title = codeItem['title'].asString
            subtitle = codeItem.readString('subtitle') if codeItem.has_key('subtitle') else ''
            background = codeItem.readString('background') if codeItem.has_key('background') else ''
            questsStr = codeItem.readString('quests') if codeItem.has_key('quests') else ''
            quests = None
            if questsStr:
                quests = questsStr.split(' ')
            questsDescr = codeItem.readString('questsDescription') if codeItem.has_key('questsDescription') else ''
            tagsStr = codeItem.readString('tags') if codeItem.has_key('tags') else ''
            tags = None
            if tagsStr:
                tags = tagsStr.split(' ')
            return (description,
             title,
             subtitle,
             background,
             quests,
             questsDescr,
             tags)
        else:
            return

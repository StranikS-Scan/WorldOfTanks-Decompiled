# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/badges_requester.py
import BigWorld
import resource_helper
from adisp import async
from constants import ITEM_DEFS_PATH
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IBadgesRequester
_BADGES_XML_PATH = ITEM_DEFS_PATH + 'badges.xml'

def _readBadges(xmlPath):
    result = {}
    ctx, section = resource_helper.getRoot(xmlPath)
    for ctx, subSection in resource_helper.getIterator(ctx, section['badges']):
        try:
            item = resource_helper.readItem(ctx, subSection, name='badge')
            if not item.name:
                raise Exception('No name for badge is provided', item.name)
            if 'id' not in item.value:
                raise Exception('No ID for badge is provided', item.value)
            value = dict(item.value)
            if 'weight' not in value:
                value['weight'] = -1.0
            value['name'] = item.name
            result[value['id']] = value
        except:
            LOG_CURRENT_EXCEPTION()

    return result


class BadgesRequester(AbstractSyncDataRequester, IBadgesRequester):
    """
    Requester for data of account badges.
    """

    def __init__(self):
        super(BadgesRequester, self).__init__()
        self.__availableBadges = _readBadges(_BADGES_XML_PATH)

    @property
    def available(self):
        """
        List of all available badges
        :return: (badgeData, ...)
        """
        return self.__availableBadges

    @property
    def selected(self):
        """
        List of player badges currently selected for display.
        :return: (badgeID, ...)
        """
        return self.getCacheValue('badges', ())

    @async
    def _requestCache(self, callback):
        BigWorld.player().badges.getCache(lambda resID, value: self._response(resID, value, callback))

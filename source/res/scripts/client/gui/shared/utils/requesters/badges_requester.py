# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/badges_requester.py
import BigWorld
import resource_helper
from adisp import async
from constants import ITEM_DEFS_PATH, CURRENT_REALM
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IBadgesRequester
from soft_exception import SoftException
_BADGES_XML_PATH = ITEM_DEFS_PATH + 'badges.xml'

def _readBadges(xmlPath):
    result = {}
    ctx, section = resource_helper.getRoot(xmlPath)
    for ctx, subSection in resource_helper.getIterator(ctx, section['badges']):
        try:
            item = resource_helper.readItem(ctx, subSection, name='badge')
            if not item.name:
                raise SoftException('No name for badge is provided', item.name)
            if 'id' not in item.value:
                raise SoftException('No ID for badge is provided', item.value)
            value = dict(item.value)
            realms = value.pop('realm', None)
            if realms is not None:
                if CURRENT_REALM in realms.get('exclude', []) or 'include' in realms and CURRENT_REALM not in realms.get('include', []):
                    continue
            if 'weight' not in value:
                value['weight'] = -1.0
            if 'type' not in value:
                value['type'] = 0
            value['name'] = item.name
            result[value['id']] = value
        except Exception:
            LOG_CURRENT_EXCEPTION()

    return result


class BadgesRequester(AbstractSyncDataRequester, IBadgesRequester):

    def __init__(self):
        super(BadgesRequester, self).__init__()
        self.__availableBadges = _readBadges(_BADGES_XML_PATH)

    @property
    def available(self):
        return self.__availableBadges

    @property
    def selected(self):
        return self.getCacheValue('badges', ())

    @async
    def _requestCache(self, callback):
        BigWorld.player().badges.getCache(lambda resID, value: self._response(resID, value, callback))

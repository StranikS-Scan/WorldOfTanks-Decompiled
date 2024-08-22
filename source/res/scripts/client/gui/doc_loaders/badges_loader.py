# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/badges_loader.py
from typing import TYPE_CHECKING
import resource_helper
from constants import ITEM_DEFS_PATH
from gui.shared.gui_items.badge import BadgeLayouts, BadgeTypes
from realm import CURRENT_REALM
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Optional, Dict
_BADGES_XML_PATH = ITEM_DEFS_PATH + 'badges.xml'

def _readBadges():
    result = {}
    ctx, section = resource_helper.getRoot(_BADGES_XML_PATH)
    for ctx, subSection in resource_helper.getIterator(ctx, section['badges']):
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
        if value['type'] == BadgeTypes.COLLAPSIBLE and 'group' not in value:
            raise SoftException('Invalid badge. No group for the COLLAPSIBLE badge', value)
        if 'layout' not in value:
            value['layout'] = BadgeLayouts.PREFIX
        else:
            layout = value['layout']
            if layout not in BadgeLayouts.ALL():
                raise SoftException('Invalid badge layout type "{}" is provided'.format(layout))
        value['name'] = item.name
        result[value['id']] = value

    resource_helper.purgeResource(_BADGES_XML_PATH)
    return result


def getSelectedByLayout(badgesIDs):
    prefixBadge = 0
    suffixBadge = 0
    availableBadges = getAvailableBadges()
    for bID in badgesIDs:
        badgeDescr = availableBadges.get(bID, None)
        if badgeDescr:
            layout = badgeDescr.get('layout', BadgeLayouts.PREFIX)
            if layout == BadgeLayouts.PREFIX:
                prefixBadge = bID
            else:
                suffixBadge = bID

    return (prefixBadge, suffixBadge)


def getAvailableBadges():
    global _badges
    if _badges is None:
        _badges = _readBadges()
    return _badges


def reloadAvailableBadges():
    global _badges
    if _badges:
        _badges = _readBadges()


_badges = None

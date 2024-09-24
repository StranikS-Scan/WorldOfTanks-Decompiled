# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/common.py
import logging
from enum import Enum
from typing import TYPE_CHECKING
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Tuple
_logger = logging.getLogger(__name__)
LOOTBOX_RANDOM_NATIONAL_BLUEPRINT = 'randomNationalBlueprint'
LOOTBOX_RANDOM_NATIONAL_BROCHURE = 'randomNationalBrochure'
LOOTBOX_RANDOM_NATIONAL_GUIDE = 'randomNationalGuide'
LOOTBOX_RANDOM_NATIONAL_CREW_BOOK = 'randomNationalCrewBook'
TEXT_RESOURCE_PREFIX = 'lootbox_'
COUNTRY_CODES_FOR_EXTERNAL_LOOT_LIST = ('KR',)

class NotificationPathPart(str, Enum):
    MAIN = 'serviceChannelMessages'
    AUTOOPEN = 'lootBoxesAutoOpen'
    HEADER = 'header'
    TEXT = 'text'
    COUNT = 'count'


class BonusTypeForPreview(str, Enum):
    VEHICLE = 'vehicles'
    CUSTOMIZATION = 'customizations'


class BonusesLayoutAttrs(object):
    PRIORITY = 'priority'
    RARITY = 'rarity'
    VISIBILITY = 'isVisible'
    OVERRIDE = 'override'
    ID = 'id'
    MAIN = (PRIORITY, RARITY, VISIBILITY)


class ViewID(str, Enum):
    INTRO = 'intro'
    MAIN = 'main'
    INFO = 'info'
    AUTOOPEN = 'autoopen'
    SHOP = 'shop'


class _ViewsResolver(object):

    def __init__(self):
        self.__loaders = {}

    def load(self, viewID, *args, **kwargs):
        loadView = self.__loaders.get(viewID)
        if callable(loadView):
            loadView(*args, **kwargs)
        else:
            _logger.warning('View "%s" does not exists', viewID.name)

    def getLoader(self, viewID):
        return self.__loaders.get(viewID)

    def setLoader(self, viewID, func):
        self.__loaders[viewID] = func

    def setLoaders(self, loaders):
        self.__loaders.update(loaders)

    def clear(self):
        self.__loaders.clear()


Views = _ViewsResolver()

@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def getTextResource(path, lootBoxes=None):

    def getResourceFromPath(resource):
        for part in path:
            resource = resource.dyn(part)

        return resource

    customResource = getResourceFromPath(R.strings.dyn(TEXT_RESOURCE_PREFIX + lootBoxes.eventName))
    return customResource if customResource.isValid() else getResourceFromPath(R.strings.lootbox_system)

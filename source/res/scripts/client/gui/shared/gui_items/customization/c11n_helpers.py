# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/c11n_helpers.py
import logging
from customization_quests_common import serializeToken
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import CustomizationType
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getProgressionStyle(styleID, group, level, c11nService=None):
    return c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getProgressionStyleCamouflage(styleID, group, level, c11nService=None):
    style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
    tokenID = serializeToken(styleID, group)
    c11nQuestProgress = style.descriptor.questsProgression
    groupItems = c11nQuestProgress.getItemsForGroup(tokenID)
    if level >= len(groupItems):
        _logger.error('Wrong progress level [%s] for customization progress group [%s]', level, tokenID)
        return
    levelItems = groupItems[level]
    camoID = first(levelItems.get(CustomizationType.CAMOUFLAGE, ()))
    if camoID is None:
        _logger.error('Missing camouflage for level [%s] in customization progress group [%s]', level, tokenID)
        return
    else:
        return c11nService.getItemByID(GUI_ITEM_TYPE.CAMOUFLAGE, camoID)

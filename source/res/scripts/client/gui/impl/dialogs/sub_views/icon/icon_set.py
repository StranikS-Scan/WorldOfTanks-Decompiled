# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/icon/icon_set.py
import logging
import typing
from gui.impl.dialogs.sub_views.common import IconSetData
from gui.impl.dialogs.sub_views.icon.multiple_icons_set import MultipleIconsSet
from gui.impl.gen.view_models.views.dialogs.sub_views.multiple_icons_set_view_model import IconPositionLogicEnum
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Optional
_logger = logging.getLogger(__name__)

class IconSet(MultipleIconsSet):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, iconResID, backgroundResIDList=None, overlayResIDList=None, layoutID=None, iconPositionLogic=IconPositionLogicEnum.CENTREDANDTHROUGHCONTENT.value):
        iconsRes = [IconSetData(iconResID, None, None)]
        super(IconSet, self).__init__(iconsRes, backgroundResIDList, overlayResIDList, layoutID, iconPositionLogic)
        return

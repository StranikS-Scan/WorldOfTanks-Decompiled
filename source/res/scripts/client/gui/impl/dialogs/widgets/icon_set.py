# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/widgets/icon_set.py
import typing
from gui.impl.dialogs.sub_views.common import IconSetData
from gui.impl.dialogs.sub_views.icon.multiple_icons_set import MultipleIconsSet
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_view_model import IconViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.multiple_icons_set_view_model import IconPositionLogicEnum
from gui.impl.gen_utils import INVALID_RES_ID
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from frameworks.wulf import Array

def _addIconResIdsToViewModelArray(source, target):
    if source:
        for resID in source:
            if resID != INVALID_RES_ID:
                iconVM = IconViewModel()
                iconVM.setPath(resID)
                target.addViewModel(iconVM)


class IconSet(MultipleIconsSet):
    __slots__ = ()

    def __init__(self, iconResID, backgroundResIDList=None, overlayResIDList=None, layoutID=None, iconPositionLogic=IconPositionLogicEnum.CENTREDANDTHROUGHCONTENT.value):
        iconsRes = [IconSetData(iconResID, None, None)]
        super(IconSet, self).__init__(iconsRes, backgroundResIDList, overlayResIDList, layoutID, iconPositionLogic)
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/icon/icon_with_blinking.py
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.icon_with_blinking_model import IconWithBlinkingModel

class IconWithBlinking(IconSet):
    _VIEW_MODEL = IconWithBlinkingModel

    def __init__(self, iconResID, backgroundResIDList=None, overlayResIDList=None, isBottomPushingDown=True, tooltip=None, blinkingResIDList=None):
        super(IconWithBlinking, self).__init__(iconResID=iconResID, backgroundResIDList=backgroundResIDList, overlayResIDList=overlayResIDList, layoutID=R.views.historical_battles.dialogs.sub_views.icon.IconWithBlinking(), isBottomPushingDown=isBottomPushingDown, tooltip=tooltip)
        self._blinkingResIDList = blinkingResIDList

    def _onLoading(self, *args, **kwargs):
        super(IconWithBlinking, self)._onLoading(*args, **kwargs)
        self._addIconResIdsToViewModelArray(self._blinkingResIDList, self.getViewModel().getBlinkingIcons())

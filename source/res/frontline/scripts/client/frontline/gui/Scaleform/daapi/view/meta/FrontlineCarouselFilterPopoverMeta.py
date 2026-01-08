# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineCarouselFilterPopoverMeta.py
from gui.Scaleform.daapi.view.common.filter_popover import TankCarouselFilterPopover

class FrontlineCarouselFilterPopoverMeta(TankCarouselFilterPopover):

    def onPlayListsChange(self, playListId):
        self._printOverrideError('onPlayListsChange')

    def as_updatePlayListsS(self, dataProvider):
        return self.flashObject.as_updatePlayLists(dataProvider) if self._isDAAPIInited() else None

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/marker_blocks.py
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from HintManager import HintManager

class MarkerMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ShowMarker(Block, MarkerMeta):

    def __init__(self, *args, **kwargs):
        super(ShowMarker, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__onShow)
        self._marker = self._makeDataInputSlot('marker', SLOT_TYPE.MARKER_POINT)
        self._out = self._makeEventOutputSlot('out')

    def __onShow(self):
        if not IS_VS_EDITOR:
            marker = self._marker.getValue()
            if marker:
                HintManager.hintManager().addMarker(marker)
                HintManager.hintManager().showMarker(marker)
        self._out.call()


class HideMarker(Block, MarkerMeta):

    def __init__(self, *args, **kwargs):
        super(HideMarker, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__onHide)
        self._marker = self._makeDataInputSlot('marker', SLOT_TYPE.MARKER_POINT)
        self._hideSilently = self._makeDataInputSlot('hideSilently ', SLOT_TYPE.BOOL)
        self._hideSilently.setDefaultValue(False)
        self._out = self._makeEventOutputSlot('out')

    def __onHide(self):
        if not IS_VS_EDITOR:
            marker = self._marker.getValue()
            if marker:
                hideSilently = False
                if self._hideSilently.hasValue():
                    hideSilently = self._hideSilently.getValue()
                HintManager.hintManager().hideMarker(marker, hideSilently)
        self._out.call()


class IsMarkerVisible(Block, MarkerMeta):

    def __init__(self, *args, **kwargs):
        super(IsMarkerVisible, self).__init__(*args, **kwargs)
        self._marker = self._makeDataInputSlot('marker', SLOT_TYPE.MARKER_POINT)
        self._visible = self._makeDataOutputSlot('visible', SLOT_TYPE.BOOL, self._isVisible)

    def _isVisible(self):
        if not IS_VS_EDITOR:
            marker = self._marker.getValue()
            if marker:
                visible = HintManager.hintManager().isMarkerVisible(marker)
                self._visible.setValue(visible)

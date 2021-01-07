# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/event_platform_blocks.py
import Math
from visual_script.block import Block, Meta, InitParam
from visual_script.dependency import dependencyImporter
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
battle_session, dependency, Avatar = dependencyImporter('skeletons.gui.battle_session', 'helpers.dependency', 'Avatar')

class EventPlatformMeta(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @classmethod
    def blockIcon(cls):
        pass


class AddMarkerAtPoint(Block, EventPlatformMeta):
    guiSessionProvider = dependency.descriptor(battle_session.IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(AddMarkerAtPoint, self).__init__(*args, **kwargs)
        self._position = self._makeDataInputSlot('Position', SLOT_TYPE.VECTOR3)
        self._markerType = self._makeDataInputSlot('Type', SLOT_TYPE.INT)
        self._markerID = self._makeDataOutputSlot('markerID', SLOT_TYPE.INT, self._execute)

    @classmethod
    def blockIcon(cls):
        pass

    def _execute(self):
        markerID = 0
        ctrl = self.guiSessionProvider.shared.areaMarker if isinstance(self.guiSessionProvider, battle_session.IBattleSessionProvider) else None
        if ctrl:
            matrix = Math.Matrix()
            matrix.translation = self._position.getValue()
            marker = ctrl.createMarker(matrix, self._markerType.getValue())
            markerID = ctrl.addMarker(marker)
        self._markerID.setValue(markerID)
        return


class RemoveMarkerAtPoint(Block, EventPlatformMeta):
    guiSessionProvider = dependency.descriptor(battle_session.IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(RemoveMarkerAtPoint, self).__init__(*args, **kwargs)
        self._number = self._getInitParams()
        self._in = self._makeEventInputSlot('in', self._execute)
        if self._number > 0:
            self._markerIds = [ self._makeDataInputSlot('markerId' + str(i), SLOT_TYPE.INT) for i in xrange(self._number) ]
        self._out = self._makeEventOutputSlot('out')

    @classmethod
    def blockIcon(cls):
        pass

    def _execute(self):
        ctrl = self.guiSessionProvider.shared.areaMarker if isinstance(self.guiSessionProvider, battle_session.IBattleSessionProvider) else None
        if ctrl:
            if self._number > 0:
                for slot in self._markerIds:
                    ctrl.removeMarker(slot.getValue())

            else:
                ctrl.removeAllMarkersAtPoint()
        self._out.call()
        return

    @classmethod
    def initParams(cls):
        return [InitParam('Should all the markers be removed? Input 0, otherwise, input tne number of markers', SLOT_TYPE.INT, 1)]

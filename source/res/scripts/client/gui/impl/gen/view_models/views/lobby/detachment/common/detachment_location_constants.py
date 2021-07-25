# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_location_constants.py
from frameworks.wulf import ViewModel

class DetachmentLocationConstants(ViewModel):
    __slots__ = ()
    BARRACKS = 'barracks_check'
    VEHICLE = 'vehicle_check'
    DISMISSED = 'dismissed'

    def __init__(self, properties=0, commands=0):
        super(DetachmentLocationConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DetachmentLocationConstants, self)._initialize()

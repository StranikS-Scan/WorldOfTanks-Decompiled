# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/common_tank_structure.py
from collections import namedtuple
VehicleAppearanceCacheInfo = namedtuple('VehicleAppearanceCacheInfo', ('typeDescr', 'health', 'isCrewActive', 'isTurretDetached', 'outfitCD', 'forceDynAttachmentLoading', 'entityGameObject'))
VehicleAppearanceCacheInfo.__new__.__defaults__ = (None,
 0,
 False,
 False,
 '',
 False)

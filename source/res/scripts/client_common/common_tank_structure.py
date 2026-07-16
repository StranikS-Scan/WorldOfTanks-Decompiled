# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/common_tank_structure.py
from __future__ import absolute_import
from collections import namedtuple
import CGF
from constants import UNKNOWN_RESPAWN_ID
VehicleAppearanceCacheInfo = namedtuple('VehicleAppearanceCacheInfo', ('typeDescr', 'health', 'isCrewActive', 'isTurretDetached', 'outfitCD', 'forceDynAttachmentLoading', 'entityGameObject', 'respawnID'))
VehicleAppearanceCacheInfo.__new__.__defaults__ = (None,
 0,
 False,
 False,
 '',
 False,
 CGF.GameObject.INVALID_GAME_OBJECT,
 UNKNOWN_RESPAWN_ID)

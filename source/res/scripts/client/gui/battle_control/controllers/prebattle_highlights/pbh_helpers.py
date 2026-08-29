# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/pbh_helpers.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
from collections import namedtuple
from shared_utils import CONST_CONTAINER
from CGF import TransformComponent
from GenericComponents import getGlobalTagStorage
from cgf_components.prefab_path_component import PyPrefabPathComponent
from gui.battle_control.avatar_getter import getSpaceID
from gui.battle_control.controllers.prebattle_highlights.pbh_constants import TANK_POS_TEMPLATE
from helpers.dependency import replace_none_kwargs
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from CGF import GameObject
    from typing import Optional
_logger = logging.getLogger(__name__)
_PBH_PREFAB_TAG = 'pbh_root'
_PBH_ANCHOR_TAG = 'pbh_anchor'
_PBH_SPACE_PREFAB_TAG = 'pbh_space_object'
_PBH_PET_ANCHOR_TEMPLATE = 'pbh_pet_top{}_{}'

class PbhSounds(CONST_CONTAINER):
    GROUP = 'STATE_ext_pbh'
    GROUP_ON = 'STATE_ext_pbh_on'
    GROUP_OFF = 'STATE_ext_pbh_off'
    EXIT_EVENT = 'pbh_stage_exit'
    ESC_EVENT = 'dc_ui_exit'
    ENTER_EVENT = 'pbh_stage_01'


PbhAnchorData = namedtuple('PbhAnchorData', ('go', 'prefabPath'))

def getPbhPrefabGo():
    pbhPrefabs = getGlobalTagStorage(getSpaceID()).getGameObjects(_PBH_PREFAB_TAG)
    if not pbhPrefabs:
        _logger.error('[PBH] No PBH prefab on scene')
        return None
    else:
        if len(pbhPrefabs) > 1:
            _logger.warning('[PBH] Multiple PBH prefabs GameObjects found for tag %s (count=%s). Using the first one.', _PBH_PREFAB_TAG, len(pbhPrefabs))
        return first(pbhPrefabs)


def getPointTransformComponent(position, size):
    tankPosTag = TANK_POS_TEMPLATE.format(position, size)
    positionsGo = getGlobalTagStorage(BigWorld.player().spaceID).getGameObjects(tankPosTag)
    if not positionsGo:
        _logger.error('No position object with tag %s', tankPosTag)
        return None
    else:
        if len(positionsGo) > 1:
            _logger.warning('Multiple position GameObjects found for tag %s (count=%s). Using the first one.', tankPosTag, len(positionsGo))
        return first(positionsGo).findRead(TransformComponent)


@replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def timeUntilEndOfPeriod(sessionProvider=None):
    periodEndTime = sessionProvider.arenaVisitor.getArenaPeriodEndTime()
    return max(int(periodEndTime - BigWorld.serverTime()), 0)


def getPbhAnchorData():
    pbhPrefabAnchors = getGlobalTagStorage(getSpaceID()).getGameObjects(_PBH_ANCHOR_TAG)
    if not pbhPrefabAnchors:
        _logger.info('[PBH] No PBH prefab anchor on scene')
        return None
    if len(pbhPrefabAnchors) > 1:
        _logger.warning('[PBH] Multiple PBH prefab anchors found for tag %s (count=%s). Using the first one.', _PBH_ANCHOR_TAG, len(pbhPrefabAnchors))
    anchorGo = first(pbhPrefabAnchors)
    prefabPathCMP = anchorGo.findRead(PyPrefabPathComponent)
    if not prefabPathCMP or not prefabPathCMP.prefabPath:
        _logger.error('[PBH] Can not find prefab path component in pbh anchor')
        return None
    else:
        return PbhAnchorData(go=anchorGo, prefabPath=prefabPathCMP.prefabPath)


def getPbhPetAnchorGo(position, size):
    petAnchorTag = _PBH_PET_ANCHOR_TEMPLATE.format(position, size)
    pbhPrefabPetAnchors = getGlobalTagStorage(getSpaceID()).getGameObjects(petAnchorTag)
    if not pbhPrefabPetAnchors:
        _logger.info('No pet anchor object with tag %s', petAnchorTag)
        return None
    else:
        if len(pbhPrefabPetAnchors) > 1:
            _logger.warning('Multiple pet anchor GameObjects found for tag %s (count=%s). Using the first one.', petAnchorTag, len(pbhPrefabPetAnchors))
        return first(pbhPrefabPetAnchors)


def getPbhSpacePrefab():
    objects = getGlobalTagStorage(getSpaceID()).getGameObjects(_PBH_SPACE_PREFAB_TAG)
    if not objects:
        _logger.info('No pbh space prefab with tag %s', _PBH_SPACE_PREFAB_TAG)
        return None
    else:
        if len(objects) > 1:
            _logger.warning('Multiple pbh space prefabs for tag %s (count=%s). Using the first one.', _PBH_SPACE_PREFAB_TAG, len(objects))
        return first(objects)

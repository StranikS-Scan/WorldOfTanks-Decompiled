# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/resource_mapping.py
from __future__ import absolute_import
import logging
import typing
from gui.impl import backport
from gui.lobby_state_machine.states import LobbyState
_logger = logging.getLogger(__name__)
_RESOURCE_LAYOUT_TO_STATE_ID_MAPPING = {}
_STATE_ID_TO_RESOURCE_ID_MAPPING = {}

def mappedToResourceId(resourceAccessor):

    def decorator(stateCls):
        resourceId = resourceAccessor()
        resourceLayout = backport.layout(resourceId)
        existingResIdMapping = _STATE_ID_TO_RESOURCE_ID_MAPPING.get(stateCls.STATE_ID)
        _RESOURCE_LAYOUT_TO_STATE_ID_MAPPING[resourceLayout] = stateCls.STATE_ID
        _STATE_ID_TO_RESOURCE_ID_MAPPING[stateCls.STATE_ID] = resourceId
        _logger.info('%s was mapped to %s (0x%x)', stateCls.STATE_ID, resourceLayout, resourceId)
        return stateCls

    return decorator


def stateIdToResId(stateId):
    return _STATE_ID_TO_RESOURCE_ID_MAPPING.get(stateId, None)


def stateIdToResLayout(stateId):
    resId = _STATE_ID_TO_RESOURCE_ID_MAPPING.get(stateId, None)
    return resId if resId is None else backport.layout(resId)


def resIdToStateId(resId):
    return resLayoutToStateId(backport.layout(resId))


def resLayoutToStateId(resLayout):
    return _RESOURCE_LAYOUT_TO_STATE_ID_MAPPING.get(resLayout, None)

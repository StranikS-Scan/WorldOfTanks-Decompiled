# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/cgf_client_common/entity_dyn_components.py
from __future__ import absolute_import
import BigWorld
from constants import IS_EDITOR

class DynamicScriptComponentStub(object):
    pass


ReplicableDynamicScriptComponent = BigWorld.DynamicScriptComponent if not IS_EDITOR else DynamicScriptComponentStub

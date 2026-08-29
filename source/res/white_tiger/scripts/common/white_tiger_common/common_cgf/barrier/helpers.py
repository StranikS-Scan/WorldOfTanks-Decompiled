# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/barrier/helpers.py
import CGF
from constants import IS_EDITOR
if IS_EDITOR:

    class WTBarrierComponent(object):
        pass


else:
    from WTBarrierComponent import WTBarrierComponent
WT_BARRIER_COMPONENTS = (CGF.GameObject, WTBarrierComponent)

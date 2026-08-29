# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/dome/helpers.py
import CGF
from constants import IS_EDITOR
if IS_EDITOR:

    class WTDomeComponent(object):
        pass


else:
    from WTDomeComponent import WTDomeComponent
WT_DOME_COMPONENTS = (CGF.GameObject, WTDomeComponent)

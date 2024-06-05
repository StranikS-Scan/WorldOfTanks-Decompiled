# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/dyn_objects.py
import typing
from dyn_objects_cache import DynObjectsBase, createTerrainCircleSettings
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
AIMING_CIRCLE_KEY = 'AimingCircleRestrictionVisual'

class StoryModeDynObjects(DynObjectsBase):

    def __init__(self):
        super(StoryModeDynObjects, self).__init__()
        self._aimingCircleRestrictionEffect = {}

    def init(self, dataSection):
        if not self._initialized:
            if dataSection.has_key(AIMING_CIRCLE_KEY):
                self._aimingCircleRestrictionEffect = createTerrainCircleSettings(dataSection[AIMING_CIRCLE_KEY])
            super(StoryModeDynObjects, self).init(dataSection)

    def destroy(self):
        self._aimingCircleRestrictionEffect.clear()
        super(StoryModeDynObjects, self).destroy()

    def getAimingCircleRestrictionEffect(self):
        return self._aimingCircleRestrictionEffect

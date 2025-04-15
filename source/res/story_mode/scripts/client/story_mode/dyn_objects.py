# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/dyn_objects.py
import typing
from dyn_objects_cache import DynObjectsBase, createTerrainCircleSettings
from story_mode_common.story_mode_constants import RECON_ABILITY, DISTRACTION_ABILITY
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
DEFAULT = 'default'
EQUIPMENT_VISUALS = {RECON_ABILITY: 'ReconAimingCircleVisual',
 DISTRACTION_ABILITY: 'DistractionAimingCircleVisual',
 DEFAULT: 'AimingCircleRestrictionVisual'}

class StoryModeDynObjects(DynObjectsBase):

    def __init__(self):
        super(StoryModeDynObjects, self).__init__()
        self._circleSettings = {}

    def init(self, dataSection):
        if not self._initialized:
            for name, visual in EQUIPMENT_VISUALS.iteritems():
                if dataSection.has_key(visual):
                    self._circleSettings[name] = createTerrainCircleSettings(dataSection[visual])

            super(StoryModeDynObjects, self).init(dataSection)

    def destroy(self):
        self._circleSettings.clear()
        super(StoryModeDynObjects, self).destroy()

    def getAimingCircleRestrictionEffect(self, equipment):
        settings = self._circleSettings.get(equipment.name)
        return settings if settings else self._circleSettings.get(DEFAULT)

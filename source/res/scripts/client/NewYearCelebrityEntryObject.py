# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearCelebrityEntryObject.py
from NewYearBaseEntryObject import NewYearBaseEntryObject
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from new_year.ny_constants import AnchorNames
from helpers import dependency
from skeletons.new_year import ICelebritySceneController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger

@loggerTarget(logKey=NY_LOG_KEYS.NY_CELEBRITY_CHALLENGE, loggerCls=NYLogger)
class NewYearCelebrityEntryObject(NewYearBaseEntryObject):
    _celebrityController = dependency.descriptor(ICelebritySceneController)

    @loggerEntry
    def onEnterWorld(self, prereqs):
        super(NewYearCelebrityEntryObject, self).onEnterWorld(prereqs)
        self._celebrityController.addCelebrityEntryEntity(self)

    def onLeaveWorld(self):
        self._celebrityController.removeCelebrityEntryEntity()
        super(NewYearCelebrityEntryObject, self).onLeaveWorld()

    @simpleLog(action=NY_LOG_ACTIONS.NY_CELEBRITY_ENTRY_FROM_HANGAR)
    def onMouseClick(self):
        super(NewYearCelebrityEntryObject, self).onMouseClick()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

    def _addEdgeDetect(self):
        self._celebrityController.addEdgeDetect()

    def _delEdgeDetect(self):
        self._celebrityController.delEdgeDetect()

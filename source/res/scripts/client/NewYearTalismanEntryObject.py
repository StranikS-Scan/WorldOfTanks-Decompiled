# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanEntryObject.py
import logging
import AnimationSequence
import BigWorld
import Math
from NewYearBaseEntryObject import NewYearBaseEntryObject
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from helpers import dependency
from new_year.ny_constants import AnchorNames, SyncDataKeys
from skeletons.new_year import ITalismanSceneController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)
_EVENT_ANIMATION_COMPLETE = 'ev_animation_complete'

@loggerTarget(logKey=NY_LOG_KEYS.NY_TALISMANS, loggerCls=NYLogger)
class NewYearTalismanEntryObject(NewYearBaseEntryObject):
    __talismanController = dependency.descriptor(ITalismanSceneController)

    def __init__(self):
        super(NewYearTalismanEntryObject, self).__init__()
        self.__progressUpAnimation = None
        self.__billboardAnimation = None
        return

    @loggerEntry
    def onEnterWorld(self, prereqs):
        super(NewYearTalismanEntryObject, self).onEnterWorld(prereqs)
        matrix = Math.Matrix(self.matrix)
        resourceNames = (self.progressUpAnimation, self.billboardAnimation)
        self.__loadAnimationSequences(resourceNames, matrix, self.spaceID)
        self.__talismanController.onShowGiftLevelUpEffect += self.__playProgressLevelUp
        self._nyController.onDataUpdated += self.__onDataUpdated

    def onLeaveWorld(self):
        if self.__progressUpAnimation is not None:
            self.__progressUpAnimation.stop()
            self.__progressUpAnimation = None
        if self.__billboardAnimation is not None:
            self.__billboardAnimation.stop()
            self.__billboardAnimation = None
        self.__talismanController.onShowGiftLevelUpEffect -= self.__playProgressLevelUp
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(NewYearTalismanEntryObject, self).onLeaveWorld()
        return

    @simpleLog(action=NY_LOG_ACTIONS.NY_TALISMAN_ENTRY_FROM_HANGAR)
    def onMouseClick(self):
        super(NewYearTalismanEntryObject, self).onMouseClick()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
        NewYearNavigation.switchByAnchorName(AnchorNames.MASCOT)

    def __loadAnimationSequences(self, resourceNames, matrix, spaceID):
        if not all(resourceNames):
            _logger.error('Missing effect for NewYearTalismanEntryObject')
            return
        loaders = tuple((AnimationSequence.Loader(resourceName, spaceID) for resourceName in resourceNames))
        BigWorld.loadResourceListBG(loaders, makeCallbackWeak(self.__onAnimationsLoaded, resourceNames, matrix))

    def __onAnimationsLoaded(self, resourceNames, matrix, resourceList):
        if self.model is None:
            _logger.error('Failed to setup sequences. Model is missing: [modelName=%s]', self.modelName)
            return
        else:
            for resourceName in resourceNames:
                if resourceName in resourceList.failedIDs:
                    _logger.error('Failed to load sequence: [resourceName=%s]', resourceName)
                    continue
                animator = resourceList[resourceName]
                animator.bindToWorld(matrix)
                if resourceName == self.progressUpAnimation:
                    self.__progressUpAnimation = animator
                    self.__progressUpAnimation.subscribe(self.__onProgressUpAnimatorEvent)
                if resourceName == self.billboardAnimation:
                    self.__billboardAnimation = animator
                    self.__updateBillboardAnimation()

            return

    def __onProgressUpAnimatorEvent(self, eventName, _):
        if eventName == _EVENT_ANIMATION_COMPLETE:
            self.__progressUpAnimation.stop()
            self.__progressUpAnimation.setEnabled(False)

    def __playProgressLevelUp(self, _):
        if self.__progressUpAnimation is not None:
            self.__progressUpAnimation.setEnabled(True)
            self.__progressUpAnimation.start()
        return

    def __onDataUpdated(self, keys):
        if {SyncDataKeys.TALISMAN_TOY_TAKEN, SyncDataKeys.TALISMANS} & set(keys):
            self.__updateBillboardAnimation()

    def __updateBillboardAnimation(self):
        if self.__billboardAnimation is None:
            return
        else:
            hasGift = self._nyController.getTalismans(isInInventory=True) and not self._nyController.isTalismanToyTaken()
            self.__billboardAnimation.setEnabled(bool(hasGift))
            if hasGift:
                self.__billboardAnimation.start()
            else:
                self.__billboardAnimation.stop()
            return

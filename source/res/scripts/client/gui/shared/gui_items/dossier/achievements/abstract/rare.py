# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/rare.py
import uuid
import imghdr
import BigWorld
from gui.shared.utils.RareAchievementsCache import IMAGE_TYPE
from regular import RegularAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from gui.shared.gui_items.dossier.achievements import validators
from helpers import dependency
from skeletons.gui.shared.utils import IRaresCache

class RareAchievement(RegularAchievement):
    __slots__ = ('_rareID',)
    SHOW_COUNTER = True
    rareAchievesCache = dependency.descriptor(IRaresCache)

    def __init__(self, rareID, dossier, value=None):
        self._rareID = int(rareID)
        super(RareAchievement, self).__init__(rareID, _AB.RARE, dossier, value)

    def getRareID(self):
        return self._rareID

    def getRecordName(self):
        return (_AB.RARE, self._rareID)

    def getUserName(self):
        return self.rareAchievesCache.getTitle(self._rareID)

    def getUserDescription(self):
        return self.rareAchievesCache.getDescription(self._rareID)

    @classmethod
    def checkIsInDossier(cls, block, rareID, dossier):
        return rareID in dossier.getBlock(_AB.RARE) if dossier is not None else False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return not validators.accountIsRoaming(dossier) if dossier is not None else True

    def getUserHeroInfo(self):
        return self.rareAchievesCache.getHeroInfo(self._rareID)

    def getUserCondition(self):
        return self.rareAchievesCache.getConditions(self._rareID)

    def isAvailableInQuest(self):
        return self.rareAchievesCache.isLocallyLoaded(self._rareID)

    def hasCounter(self):
        return self.SHOW_COUNTER and self._value > 1

    def requestImageID(self):
        return self._requestImageID(IMAGE_TYPE.IT_67X71)

    def requestBigImageID(self):
        return self._requestImageID(IMAGE_TYPE.IT_180X180)

    def _readValue(self, dossier):
        return dossier.getBlock(_AB.RARE).count(self._rareID)

    def _requestImageID(self, imgType):
        self.rareAchievesCache.request([self._rareID])
        memImgID = None
        iconData = self.rareAchievesCache.getImageData(imgType, self._rareID)
        if iconData and imghdr.what(None, iconData) is not None:
            memImgID = str(uuid.uuid4())
            BigWorld.wg_addTempScaleformTexture(memImgID, iconData)
        return memImgID

    def getIcons(self):
        memImgID = self.requestImageID()
        icons = super(RareAchievement, self).getIcons()
        if memImgID is not None:
            icons[self.ICON_TYPE.IT_67X71] = 'img://%s' % str(memImgID)
        memBigImgID = self.requestBigImageID()
        if memBigImgID is not None:
            icons[self.ICON_TYPE.IT_180X180] = 'img://%s' % str(memBigImgID)
        return icons

    def getIconName(self):
        pass

    def __repr__(self):
        return '%s<rareID=%s; value=%s>' % (self.__class__.__name__, str(self._rareID), str(self._value))

# Embedded file name: scripts/client/gui/goodies/Booster.py
import BigWorld
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils import CONST_CONTAINER
from helpers import time_utils
from helpers.i18n import makeString as _ms
_BOOSTER_ICON_PATH = '../maps/icons/boosters/%s.png'
_BOOSTER_BIG_ICON_PATH = '../maps/icons/boosters/%s_big.png'
_BOOSTER_QUALITY_SOURCE_PATH = '../maps/icons/boosters/booster_quality_%s.png'
_BOOSTER_TYPE_LOCALE = '#menu:booster/userName/%s'
_BOOSTER_DESCRIPTION_LOCALE = '#menu:booster/description/%s'
_BOOSTER_QUALITY_LOCALE = '#menu:booster/quality/%s'
MAX_ACTIVE_BOOSTERS_COUNT = 3

class BOOSTER_QUALITY(CONST_CONTAINER):
    BIG = 12.5
    MEDIUM = 7.5
    SMALL = 5


_BOOSTER_QUALITY_NAMES = dict([ (v, k.lower()) for k, v in BOOSTER_QUALITY.__dict__.iteritems() ])
_BOOSTER_TYPE_NAMES = {GOODIE_RESOURCE_TYPE.GOLD: 'booster_gold',
 GOODIE_RESOURCE_TYPE.CREDITS: 'booster_credits',
 GOODIE_RESOURCE_TYPE.XP: 'booster_xp',
 GOODIE_RESOURCE_TYPE.CREW_XP: 'booster_crew_xp',
 GOODIE_RESOURCE_TYPE.FREE_XP: 'booster_free_xp'}

class Booster(object):

    def __init__(self, boosterID, boosterDescription, boosterValues, activeBoosterTypes):
        self.boosterID = boosterID
        self.expiryTime = boosterDescription.useby
        self.maxCount = boosterDescription.limit
        self.effectTime = boosterDescription.lifetime
        self.boosterType, self.effectValue, _ = boosterDescription.resources[0]
        self.__activeBoosterTypes = activeBoosterTypes
        if boosterValues is not None:
            self.state = boosterValues.state
            self.count = boosterValues.count
            self.finishTime = boosterValues.finishTime
        else:
            self.state = GOODIE_STATE.INACTIVE
            self.count = 0
            self.finishTime = None
        return

    @property
    def icon(self):
        return _BOOSTER_ICON_PATH % self.boosterGuiType

    @property
    def bigIcon(self):
        return _BOOSTER_BIG_ICON_PATH % self.boosterGuiType

    @property
    def boosterGuiType(self):
        return _BOOSTER_TYPE_NAMES[self.boosterType]

    @property
    def quality(self):
        if self.effectValue >= BOOSTER_QUALITY.BIG:
            return _BOOSTER_QUALITY_NAMES[BOOSTER_QUALITY.BIG]
        elif self.effectValue >= BOOSTER_QUALITY.MEDIUM:
            return _BOOSTER_QUALITY_NAMES[BOOSTER_QUALITY.MEDIUM]
        else:
            return _BOOSTER_QUALITY_NAMES[BOOSTER_QUALITY.SMALL]

    @property
    def qualityStr(self):
        return _ms(_BOOSTER_QUALITY_LOCALE % self.quality)

    @property
    def inCooldown(self):
        return self.state == GOODIE_STATE.ACTIVE

    @property
    def isInAccount(self):
        return self.count > 0

    @property
    def isReadyToActivate(self):
        return self.count > 0 and self.state == GOODIE_STATE.INACTIVE and self.boosterType not in self.__activeBoosterTypes

    @property
    def userName(self):
        return _ms(_BOOSTER_TYPE_LOCALE % self.boosterGuiType)

    @property
    def description(self):
        return _ms(_BOOSTER_DESCRIPTION_LOCALE % self.boosterGuiType, effectValue=self.effectValue) + _ms(MENU.BOOSTER_DESCRIPTION_EFFECTTIME, effectTime=self.getEffectTimeStr())

    def getCooldownAsPercent(self):
        percent = 0
        if self.finishTime is not None and self.effectTime is not None:
            leftTime = self.getUsageLeftTime()
            percent = float(max(self.effectTime - leftTime, 0)) / self.effectTime * 100
        return percent

    def getUsageLeftTime(self):
        if self.finishTime is not None:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.finishTime))
        else:
            return 0

    def getUsageLeftTimeStr(self):
        return self._getLocalizedTime(self.getUsageLeftTime(), MENU.TIME_TIMEVALUE)

    def getShortLeftTimeStr(self):
        return self._getLocalizedTime(self.getUsageLeftTime(), MENU.TIME_TIMEVALUESHORT)

    def getEffectTimeStr(self):
        return self._getLocalizedTime(self.effectTime, MENU.TIME_TIMEVALUE)

    def getQualityIcon(self):
        return _BOOSTER_QUALITY_SOURCE_PATH % self.quality

    def getExpiryDate(self):
        return BigWorld.wg_getLongDateFormat(self.expiryTime)

    def _getLocalizedTime(self, seconds, locale):
        return time_utils.getTillTimeString(seconds, locale)

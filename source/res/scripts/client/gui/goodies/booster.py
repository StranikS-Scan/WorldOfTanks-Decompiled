# Embedded file name: scripts/client/gui/goodies/Booster.py
import BigWorld
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE
from gui import GUI_SETTINGS
from gui.Scaleform.locale.MENU import MENU
from shared_utils import CONST_CONTAINER
from helpers import time_utils
from helpers.i18n import makeString as _ms
_BOOSTER_ICON_PATH = '../maps/icons/boosters/%s.png'
_BOOSTER_BIG_ICON_PATH = '../maps/icons/boosters/%s_big.png'
_BOOSTER_QUALITY_SOURCE_PATH = '../maps/icons/boosters/booster_quality_%s.png'
_BOOSTER_TYPE_LOCALE = '#menu:booster/userName/%s'
_BOOSTER_DESCRIPTION_LOCALE = '#menu:booster/description/%s'
_BOOSTER_QUALITY_LOCALE = '#menu:booster/quality/%s'
MAX_ACTIVE_BOOSTERS_COUNT = 3

class BOOSTER_QUALITY_NAMES(CONST_CONTAINER):
    BIG = 'big'
    MEDIUM = 'medium'
    SMALL = 'small'


_BOOSTER_QUALITY_VALUES = {BOOSTER_QUALITY_NAMES.BIG: 12.5,
 BOOSTER_QUALITY_NAMES.MEDIUM: 7.5}
_BOOSTER_TYPE_NAMES = {GOODIE_RESOURCE_TYPE.GOLD: 'booster_gold',
 GOODIE_RESOURCE_TYPE.CREDITS: 'booster_credits',
 GOODIE_RESOURCE_TYPE.XP: 'booster_xp',
 GOODIE_RESOURCE_TYPE.CREW_XP: 'booster_crew_xp',
 GOODIE_RESOURCE_TYPE.FREE_XP: 'booster_free_xp'}

class Booster(object):

    def __init__(self, boosterID, boosterDescription, boosterValues, activeBoostersValues):
        self.boosterID = boosterID
        self.expiryTime = boosterDescription.useby
        self.maxCount = boosterDescription.limit
        self.effectTime = boosterDescription.lifetime
        self.boosterType, self.effectValue, _ = boosterDescription.resource
        self.__activeBoostersValues = activeBoostersValues
        self.enabled = boosterDescription.enabled
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
        boosterQualityValues = GUI_SETTINGS.lookup(self.boosterGuiType) or _BOOSTER_QUALITY_VALUES
        if self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.BIG]:
            return BOOSTER_QUALITY_NAMES.BIG
        elif self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.MEDIUM]:
            return BOOSTER_QUALITY_NAMES.MEDIUM
        else:
            return BOOSTER_QUALITY_NAMES.SMALL

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
        return self.isReadyToUse or self.isReadyToUpdate

    @property
    def isReadyToUse(self):
        activeBoosterTypes = [ boosterType for boosterType, _, _ in self.__activeBoostersValues ]
        if self.enabled:
            return self.count > 0 and self.state == GOODIE_STATE.INACTIVE and len(self.__activeBoostersValues) < MAX_ACTIVE_BOOSTERS_COUNT and self.boosterType not in activeBoosterTypes
        return False

    @property
    def isReadyToUpdate(self):
        if self.enabled:
            for aBoosterType, aEffectValue, _ in self.__activeBoostersValues:
                if self.boosterType == aBoosterType and self.count > 0:
                    return self.effectValue > aEffectValue

        return False

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
        if self.expiryTime is not None:
            return BigWorld.wg_getLongDateFormat(self.expiryTime)
        else:
            return ''

    def _getLocalizedTime(self, seconds, locale):
        return time_utils.getTillTimeString(seconds, locale)

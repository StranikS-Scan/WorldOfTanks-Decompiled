# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/promo/hangar_teaser_widget.py
import weakref
from functools import partial
import BigWorld
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.promo.constants import PROMO_SOUNDS
from gui.promo.promo_logger import PromoLogActions
from gui.shared.formatters import icons
from gui.shared.view_helpers.image_helper import ImageHelper, getTextureLinkByID
from helpers import time_utils, dependency
from items.components.shared_components import i18n
from skeletons.gui.shared.promo import IPromoLogger

class TeaserViewer(object):
    _TIMER_PERIOD = 0.1
    _SALE_PROMO_TYPE = 'hot_stock'

    def __init__(self, view, showCallback, closeCallback):
        self.__viewProxy = weakref.proxy(view)
        self.__teaserData = None
        self.__promoCount = 0
        self.__prevTimerValue = 0
        self.__callbackID = None
        self.__imagePath = None
        self.__showCallback = showCallback
        self.__closeCallback = closeCallback
        return

    def show(self, teaserData, promoCount):
        self.__teaserData = teaserData
        self.__promoCount = promoCount
        teaserID = teaserData['promoID']
        ImageHelper.requestImageByUrl(self.__teaserData['image'], partial(self.__onImageLoaded, teaserID))

    def stop(self, byUser=False):
        logAction = PromoLogActions.CLOSED_BY_USER if byUser else PromoLogActions.KILLED_BY_SYSTEM
        dependency.instance(IPromoLogger).logTeaserAction(self.__teaserData, action=logAction)
        self.__stopTimer()
        self.__closeCallback(byUser)
        self.__teaserData = None
        return

    def __onImageLoaded(self, requestedTeaserID, image):
        if not self.__teaserData or self.__teaserData['promoID'] != requestedTeaserID:
            return
        self.__imagePath = getTextureLinkByID(ImageHelper.getMemoryTexturePath(image))
        self.__stopTimer()
        isShopPromo = self.__teaserData.get('promoType') == self._SALE_PROMO_TYPE
        self.__viewProxy.as_showTeaserS({'postTitle': i18n.makeString(MENU.PROMO_TEASER_TITLE),
         'postCounter': self.__promoCount,
         'descr': self.__teaserData['description'],
         'title': self.__teaserData.get('version', ''),
         'isVideo': bool(self.__teaserData.get('video')),
         'isShopPromo': isShopPromo,
         'image': self.__imagePath})
        self.__viewProxy.soundManager.playSound(PROMO_SOUNDS.SALE_TEASER if isShopPromo else PROMO_SOUNDS.INFO_TEASER)
        if self.__teaserData.get('finishTime'):
            self.__startTimer()
        self.__showCallback(self.__teaserData.get('promoID'))

    def __startTimer(self):
        self.__timeIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON, 16, 16, -3, 0)
        self.__timerTick()

    def __timerTick(self):
        timeLeft = int(self.__teaserData.get('finishTime') - time_utils.getServerUTCTime())
        if timeLeft > 0:
            timerStr = time_utils.getTillTimeString(timeLeft, MENU.PROMO_TEASERTIMEFORMAT)
            if self.__prevTimerValue != timerStr:
                self.__viewProxy.as_setTeaserTimerS(self.__timeIcon + timerStr)
                self.__prevTimerValue = timerStr
            self.__callbackID = BigWorld.callback(self._TIMER_PERIOD, self.__timerTick)
        else:
            self.__stopTimer()

    def __stopTimer(self):
        if self.__callbackID:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
            self.__viewProxy.as_hideTeaserTimerS()
        return

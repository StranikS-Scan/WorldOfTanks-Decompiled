# Embedded file name: scripts/client/gui/game_control/gc_constants.py
from gui.shared.utils import CONST_CONTAINER

class CONTROLLER(CONST_CONTAINER):
    ROAMING = 'roaming'
    AOGAS = 'aogas'
    GAME_SESSION = 'gameSession'
    CAPTCHA = 'captcha'
    RENTALS = 'rentals'
    IGR = 'igr'
    WALLET = 'wallet'
    LANGUAGE = 'language'
    NOTIFIER = 'notifier'
    LINKS = 'links'
    SOUND_CHECKER = 'soundChecker'
    SERVER_STATS = 'serverStats'
    REF_SYSTEM = 'refSystem'
    BROWSER = 'browser'
    PROMO = 'promo'
    EVENTS_NOTIFICATION = 'eventsNotifications'
    CHINA = 'china'
    AWARD = 'award'


class BROWSER(CONST_CONTAINER):
    CHINA_BROWSER_COUNT = 999
    SIZE = (990, 550)
    BACKGROUND = 'file:///gui/maps/bg.png'
    PROMO_SIZE = (780, 470)
    PROMO_BACKGROUND = 'file:///gui/maps/promo_bg.png'


class PROMO(CONST_CONTAINER):

    class TEMPLATE(CONST_CONTAINER):
        PATCH = 'promo_patchnote'
        ACTION = 'promo_action'

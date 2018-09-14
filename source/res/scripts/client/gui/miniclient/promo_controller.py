# Embedded file name: scripts/client/gui/miniclient/promo_controller.py
from helpers import aop

class ShowPromoBrowserPointcut(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.game_control.PromoController', 'PromoController', 'onLobbyInited', aspects=(aop.DummyAspect,))

# Embedded file name: scripts/client/gui/game_control/__init__.py
import BigWorld
from gui.game_control.LanguageController import LanguageController
from gui.game_control.RefSystem import RefSystem
from gui.game_control.RentalsController import RentalsController
from gui.game_control.links import ExternalLinksHandler
from gui.game_control.roaming import RoamingController
from gui.game_control.AOGAS import AOGASController
from gui.game_control.captcha_control import CaptchaController
from gui.game_control.GameSessionController import GameSessionController
from gui.game_control.IGR import IGRController
from gui.game_control.wallet import WalletController
from gui.game_control.NotifyController import NotifyController
from gui.game_control.SoundEventChecker import SoundEventChecker
from gui.game_control.ServerStats import ServerStats

class _GameControllers(object):

    def __init__(self):
        super(_GameControllers, self).__init__()
        self.__roaming = RoamingController()
        self.__captcha = CaptchaController()
        self.__rentals = RentalsController()
        self.__aogas = AOGASController()
        self.__gameSession = GameSessionController()
        self.__igr = IGRController()
        self.__wallet = WalletController()
        self.__language = LanguageController()
        self.__notifier = NotifyController()
        self.__links = ExternalLinksHandler()
        self.__soundChecker = SoundEventChecker()
        self.__serverStats = ServerStats()
        self.__refSystem = RefSystem()
        self.__collectUiStats = False
        self.__logUXEvents = False

    @property
    def collectUiStats(self):
        return self.__collectUiStats

    @property
    def rentals(self):
        return self.__rentals

    @property
    def needLogUXEvents(self):
        return self.__logUXEvents

    @property
    def captcha(self):
        return self.__captcha

    @property
    def aogas(self):
        return self.__aogas

    @property
    def gameSession(self):
        return self.__gameSession

    @property
    def igr(self):
        return self.__igr

    @property
    def roaming(self):
        return self.__roaming

    @property
    def wallet(self):
        return self.__wallet

    @property
    def notifier(self):
        return self.__notifier

    @property
    def language(self):
        return self.__language

    @property
    def links(self):
        return self.__links

    @property
    def soundChecker(self):
        return self.__soundChecker

    @property
    def serverStats(self):
        return self.__serverStats

    @property
    def refSystem(self):
        return self.__refSystem

    def init(self):
        self.__captcha.init()
        self.__aogas.init()
        self.__gameSession.init()
        self.__igr.init()
        self.__roaming.init()
        self.__wallet.init()
        self.__language.init()
        self.__notifier.init()
        self.__links.init()
        self.__soundChecker.init()
        self.__serverStats.init()
        self.__refSystem.init()
        self.__rentals.init()

    def fini(self):
        self.__igr.fini()
        self.__captcha.fini()
        self.__aogas.fini()
        self.__gameSession.fini()
        self.__roaming.fini()
        self.__wallet.fini()
        self.__language.fini()
        self.__notifier.fini()
        self.__links.fini()
        self.__soundChecker.fini()
        self.__serverStats.fini()
        self.__refSystem.fini()
        self.__rentals.fini()

    def onAccountShowGUI(self, ctx):
        self.__language.start()
        self.__captcha.start()
        self.__aogas.start(ctx)
        self.__gameSession.start(ctx.get('sessionStartedAt', -1))
        self.__igr.start(ctx)
        self.__wallet.start()
        self.__rentals.start()
        self.__notifier.start()
        self.__soundChecker.start()
        self.__serverStats.start()
        self.__refSystem.start()
        self.__collectUiStats = ctx.get('collectUiStats', False)
        self.__logUXEvents = ctx.get('logUXEvents', False)

    def onAvatarBecomePlayer(self):
        self.__aogas.disableNotifyAccount()
        self.__gameSession.stop(True)
        self.__roaming.stop()
        self.__rentals.stop()
        self.__wallet.stop()
        self.__soundChecker.stop()
        self.__serverStats.stop()
        self.__refSystem.stop()

    def onAccountBecomePlayer(self):
        self.__roaming.start(BigWorld.player().serverSettings)

    def onDisconnected(self):
        self.__language.stop()
        self.__captcha.stop()
        self.__aogas.stop()
        self.__gameSession.stop()
        self.__rentals.stop()
        self.__igr.clear()
        self.__roaming.onDisconnected()
        self.__wallet.stop()
        self.__notifier.stop()
        self.__soundChecker.stop()
        self.__serverStats.stop()
        self.__refSystem.stop()


g_instance = _GameControllers()

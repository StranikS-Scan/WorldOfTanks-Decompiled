# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampLobbyAppearConfig.py


class Appear:
    TOP = 1
    LEFT = 2
    RIGHT = 4
    BOTTOM = 8
    ALPHA = 16
    SCALE = 32


class BootcampLobbyAppearConfig:
    objects = {'Header': {'type': Appear.TOP},
     'HangarCrew': {'type': Appear.LEFT | Appear.ALPHA},
     'HangarQuestControl': {'type': Appear.TOP | Appear.ALPHA},
     'HeaderSilver': {'type': Appear.ALPHA},
     'HeaderGold': {'type': Appear.ALPHA},
     'MenuTechTree': {'type': Appear.ALPHA},
     'MenuHangar': {'type': Appear.TOP | Appear.ALPHA},
     'HeaderBattleSelector': {'type': Appear.ALPHA},
     'HeaderPremium': {'type': Appear.ALPHA},
     'HeaderMainMenuButtonBar': {'type': Appear.TOP | Appear.ALPHA},
     'HangarCarousel': {'type': Appear.BOTTOM}}

    def getItems(self):
        return self.objects


g_bootcampAppearConfig = BootcampLobbyAppearConfig()

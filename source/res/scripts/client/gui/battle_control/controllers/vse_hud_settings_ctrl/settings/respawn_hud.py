# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/respawn_hud.py


class RespawnHUDClientModel(object):
    __slots__ = ('dynamicRespawnHeader', 'dynamicRespawnSubheader', 'staticRespawnHeader', 'staticRespawnSubheader', 'battleOverHeader', 'battleOverSubheader', 'staticRespawnSound', 'dynamicRespawnSound', 'battleOverSound', 'showLivesInAlliesList', 'showLivesInTankPanel')

    def __init__(self, dynamicRespawnHeader, dynamicRespawnSubheader, staticRespawnHeader, staticRespawnSubheader, battleOverHeader, battleOverSubheader, staticRespawnSound, dynamicRespawnSound, battleOverSound, showLivesInAlliesList, showLivesInTankPanel):
        super(RespawnHUDClientModel, self).__init__()
        self.dynamicRespawnHeader = dynamicRespawnHeader
        self.dynamicRespawnSubheader = dynamicRespawnSubheader
        self.staticRespawnHeader = staticRespawnHeader
        self.staticRespawnSubheader = staticRespawnSubheader
        self.battleOverHeader = battleOverHeader
        self.battleOverSubheader = battleOverSubheader
        self.staticRespawnSound = staticRespawnSound
        self.dynamicRespawnSound = dynamicRespawnSound
        self.battleOverSound = battleOverSound
        self.showLivesInAlliesList = showLivesInAlliesList
        self.showLivesInTankPanel = showLivesInTankPanel

    def __repr__(self):
        return '<RespawnHUDClientModel>: dynamicRespawnHeader=%s, dynamicRespawnSubheader=%s, staticRespawnHeader=%sstaticRespawnSubheader=%s, battleOverHeader=%s, battleOverSubheader=%sstaticRespawnSound=%s, dynamicRespawnSound=%s, battleOverSound=%sshowLivesInAlliesList=%s, showLivesInTankPanel=%s' % (self.dynamicRespawnHeader,
         self.dynamicRespawnSubheader,
         self.staticRespawnHeader,
         self.staticRespawnSubheader,
         self.battleOverHeader,
         self.battleOverSubheader,
         self.staticRespawnSound,
         self.dynamicRespawnSound,
         self.battleOverSound,
         self.showLivesInAlliesList,
         self.showLivesInTankPanel)

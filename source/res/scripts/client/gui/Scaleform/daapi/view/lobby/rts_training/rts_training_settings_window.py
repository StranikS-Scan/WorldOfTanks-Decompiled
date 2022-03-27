# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_training/rts_training_settings_window.py
from gui.Scaleform.daapi.view.lobby.trainings.TrainingSettingsWindow import ArenasCache
from gui.Scaleform.daapi.view.meta.TrainingWindowMeta import TrainingWindowMeta
from gui.prb_control import prbEntityProperty
from gui.prb_control.prb_getters import getTrainingBattleRoundLimits
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.shared import IItemsCache

class RtsTrainingSettingsWindow(TrainingWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RtsTrainingSettingsWindow, self).__init__()
        self.__isCreateRequest = ctx.get('isCreateRequest', False)
        self.__settings = ctx.get('settings', None)
        self.__arenasCache = ArenasCache(allowedOnlyGpNames=('rts',))
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(RtsTrainingSettingsWindow, self)._populate()
        self.as_setDataS(self.getInfo(), self.getMapsData())

    def getMapsData(self):
        return self.__arenasCache.cache

    def getInfo(self):
        if not self.__isCreateRequest:
            self.__settings = self.__settings.fetch(self.prbEntity.getSettings())
        if self.itemsCache.isSynced():
            accountAttrs = self.itemsCache.items.stats.attributes
        else:
            accountAttrs = 0
        _, maxBound = getTrainingBattleRoundLimits(accountAttrs)
        rTitle = R.strings.menu.training.create.title() if self.__isCreateRequest else R.strings.menu.training.info.settings.title()
        info = {'description': self.__settings.getComment(),
         'timeout': self.__settings.getRoundLen() / 60,
         'arena': self.__settings.getArenaTypeID(),
         'privacy': not self.__settings.isOpened(),
         'create': self.__isCreateRequest,
         'wndTitle': backport.text(rTitle),
         'canMakeOpenedClosed': True,
         'canChangeComment': True,
         'canChangeArenaTime': True,
         'canChangeArena': True,
         'maxBattleTime': maxBound / 60}
        if not self.__isCreateRequest:
            permissions = self.prbEntity.getPermissions()
            info['canMakeOpenedClosed'] = permissions.canMakeOpenedClosed()
            info['canChangeComment'] = permissions.canChangeComment()
            info['canChangeArena'] = permissions.canChangeArena()
        return info

    def updateTrainingRoom(self, arena, roundLength, isPrivate, comment):
        self.__settings.setArenaTypeID(arena)
        self.__settings.setRoundLen(roundLength * 60)
        self.__settings.setOpened(not isPrivate)
        self.__settings.setComment(comment)
        self.fireEvent(events.TrainingSettingsEvent(events.TrainingSettingsEvent.UPDATE_RTS_TRAINING_SETTINGS, ctx={'settings': self.__settings}), scope=EVENT_BUS_SCOPE.LOBBY)

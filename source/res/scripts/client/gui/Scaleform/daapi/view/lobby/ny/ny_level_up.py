# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_level_up.py
from gui.Scaleform.daapi.view.meta.NYLevelUpMeta import NYLevelUpMeta
from gui.Scaleform.locale.NY import NY
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearUIManager, ICustomizableObjectsManager, INewYearController
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE
_DEF_DATA = {'closeBtnLabel': NY.LEVELUP_CLOSEBTN_LABEL,
 'description': NY.LEVELUP_DESCRIPTION,
 'giftDescription': NY.LEVELUP_GIFTDESCRIPTION,
 'openLabel': NY.LEVELUP_BUTTONS_OPEN_LABEL}

class NYLevelUp(NYLevelUpMeta):
    nyUIManager = dependency.descriptor(INewYearUIManager)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    newYearController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        super(NYLevelUp, self).__init__()
        self.__level = ctx.get('level', 0)

    def onWindowClose(self):
        self.destroy()

    def onPlaySound(self, soundType):
        NYSoundEvents.playSound(soundType)

    def onOpenClick(self):
        self.as_boxOpenS(self.newYearController.chestStorage.count > 0)

    def onAnimFinished(self, isBoxOpened):
        if isBoxOpened:
            self.nyUIManager.buttonClickOpenChest()
        else:
            self.__close()

    def onClose(self):
        self.__close()

    def __close(self):
        self.destroy()

    def _populate(self):
        super(NYLevelUp, self)._populate()
        data = _DEF_DATA
        data['level'] = self.__level
        self.as_setDataS(data)
        self.newYearController.onStateChanged += self.__onNyStateChanged
        self.addListener(events.NewYearEvent.CLOSE_LEVEL_UP_VIEW, self.__handleCloseEvent, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.newYearController.onStateChanged += self.__onNyStateChanged
        self.removeListener(events.NewYearEvent.CLOSE_LEVEL_UP_VIEW, self.__handleCloseEvent, EVENT_BUS_SCOPE.LOBBY)

    def __handleCloseEvent(self, _):
        self.__close()

    def __onNyStateChanged(self, _):
        if not self.newYearController.isAvailable():
            self.destroy()

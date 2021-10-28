# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_ingame_help.py
from gui import GUI_CTRL_MODE_FLAG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.HWIngameHelpWindowMeta import HWIngameHelpWindowMeta
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R

class HWIngameHelpWindow(HWIngameHelpWindowMeta, BattleGUIKeyHandler):
    _MAX_PAGES = 4

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def _populate(self):
        super(HWIngameHelpWindow, self)._populate()
        self.app.registerGuiKeyHandler(self)
        self.app.enterGuiControlMode(VIEW_ALIAS.EVENT_INGAME_HELP, cursorVisible=True, enableAiming=False)
        avatar_getter.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.GUI_ENABLED, enableAiming=False)
        self.as_setDataS([ self.__getPageConfig(pageNum + 1) for pageNum in xrange(self._MAX_PAGES) ])
        self.as_setPaginatorDataS([ self.__getPaginatorConfig(pageNum) for pageNum in xrange(self._MAX_PAGES) ])

    @staticmethod
    def __getPageConfig(pageNum):
        pageData = {'rendererLinkage': 'HWHintPageBigUI',
         'header1Text': backport.text(R.strings.event.ingameHelp.dyn('page{}'.format(pageNum)).title()),
         'header1AutoSize': 'center',
         'description1Text': backport.text(R.strings.event.ingameHelp.dyn('page{}'.format(pageNum)).text()),
         'description1AutoSize': 'center',
         'background': backport.image(R.images.gui.maps.icons.event.ingameHelp.dyn('bg{}'.format(pageNum))())}
        return pageData

    @staticmethod
    def __getPaginatorConfig(pageNum):
        pageData = {'buttonsGroup': 'HelpPagesGroup',
         'pageIndex': pageNum,
         'label': str(pageNum + 1),
         'status': '',
         'selected': pageNum == 0,
         'tooltip': {}}
        return pageData

    def _dispose(self):
        self.app.leaveGuiControlMode(VIEW_ALIAS.EVENT_INGAME_HELP)
        self.app.unregisterGuiKeyHandler(self)
        super(HWIngameHelpWindow, self)._dispose()

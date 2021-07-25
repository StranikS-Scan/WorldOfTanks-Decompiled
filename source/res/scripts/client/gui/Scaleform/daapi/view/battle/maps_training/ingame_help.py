# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/ingame_help.py
from gui import GUI_CTRL_MODE_FLAG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MapsTrainingIngameHelpWindowMeta import MapsTrainingIngameHelpWindowMeta
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
_HTML_TEMPLATE_PATH = 'html_templates:mapsTraining/loadingScreen'

class MapsTrainingIngameHelpWindow(MapsTrainingIngameHelpWindowMeta, BattleGUIKeyHandler):

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def _populate(self):
        super(MapsTrainingIngameHelpWindow, self)._populate()
        self.app.registerGuiKeyHandler(self)
        self.app.enterGuiControlMode(VIEW_ALIAS.INGAME_HELP, cursorVisible=True, enableAiming=False)
        avatar_getter.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.GUI_ENABLED, enableAiming=False)
        self.as_setDataS([ self.__getPageConfig(pageNum + 1) for pageNum in xrange(4) ])

    @staticmethod
    def __getPageConfig(pageNum):
        pageData = {'rendererLinkage': 'MapsTrainingHint{}PageBigUI'.format(pageNum),
         'header1Text': backport.text(R.strings.maps_training.loadingScreen.num(pageNum).title()),
         'header1AutoSize': 'center',
         'description1Text': backport.text(R.strings.maps_training.loadingScreen.num(pageNum).description()),
         'description1AutoSize': 'center',
         'background': backport.image(R.images.gui.maps.icons.mapsTraining.dyn('tip_bg_0{}'.format(pageNum))())}
        return pageData

    def _dispose(self):
        self.app.leaveGuiControlMode(VIEW_ALIAS.INGAME_HELP)
        self.app.unregisterGuiKeyHandler(self)
        super(MapsTrainingIngameHelpWindow, self)._dispose()

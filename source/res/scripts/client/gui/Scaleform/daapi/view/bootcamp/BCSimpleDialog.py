# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCSimpleDialog.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog
from gui.Scaleform.framework import ScopeTemplates

class BCSimpleDialog(SimpleDialog):

    def __init__(self, message, title, buttons, handler, dialogScope=ScopeTemplates.DEFAULT_SCOPE, timer=0):
        super(BCSimpleDialog, self).__init__(message, title, buttons, handler, dialogScope=dialogScope, timer=timer)

    def onWindowClose(self):
        super(BCSimpleDialog, self).onWindowClose()
        self.__showPrevHint()

    def __showPrevHint(self):
        from bootcamp.Bootcamp import g_bootcamp
        if g_bootcamp.getLessonNum() < g_bootcamp.getContextIntParameter('researchFreeLesson'):
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.showPrevHint()

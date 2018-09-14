# Embedded file name: scripts/client/gui/Scaleform/framework/entities/View.py
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.doc_loaders import hints_layout
from gui.shared.events import FocusEvent
__author__ = 'd_trofimov'

class View(AbstractViewMeta):

    def __init__(self, ctx = None):
        super(View, self).__init__()
        self.__settings = None
        self.__uniqueName = None
        from gui.Scaleform.framework import ScopeTemplates
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        return

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED))

    def __del__(self):
        LOG_DEBUG('View deleted:', self)

    def getSubContainerType(self):
        """
        Called by container manager. Should return container type of view sub-container, if it exists.
        Returns None by default
        Override in sub-classes if needed.
        """
        return None

    def setCurrentScope(self, scope):
        from gui.Scaleform.framework import ScopeTemplates
        FOR_ALIAS = 'for ' + self.settings.alias + ' view.'
        if self.__settings is not None:
            if self.__settings.scope == ScopeTemplates.DYNAMIC_SCOPE:
                if scope != ScopeTemplates.DYNAMIC_SCOPE:
                    self.__scope = scope
                else:
                    raise Exception('View.__scope can`t be a ScopeTemplates.DYNAMIC value. This value might have only ' + 'settings.scope ' + FOR_ALIAS)
            else:
                raise Exception('You can not change a non-dynamic scope. Declare ScopeTemplates.DYNAMIC in settings ' + FOR_ALIAS)
        else:
            LOG_ERROR('You can not change a current scope, until unimplemented __settings ')
        return

    def getCurrentScope(self):
        return self.__scope

    @property
    def settings(self):
        return self.__settings

    def setSettings(self, settings):
        from gui.Scaleform.framework import ScopeTemplates
        if settings is not None:
            self.__settings = settings
            if self.__settings.scope != ScopeTemplates.DYNAMIC_SCOPE:
                self.__scope = self.__settings.scope
        else:
            LOG_DEBUG('settings can`t be None!')
        return

    @property
    def alias(self):
        return self.__settings.alias

    @property
    def uniqueName(self):
        return self.__uniqueName

    def setUniqueName(self, name):
        if name is not None:
            self.__uniqueName = name
        else:
            LOG_DEBUG('uniqueName can`t be None!')
        return

    def setupContextHints(self, hintID):
        if hintID is not None:
            hintsData = dict(hints_layout.getLayout(hintID))
            if hintsData is not None:
                builder = hintsData.pop('builderLnk', '')
                self.as_setupContextHintBuilderS(builder, hintsData)
            else:
                LOG_ERROR('Hint layout is nor defined', hintID)
        return

    def _dispose(self):
        super(View, self)._dispose()

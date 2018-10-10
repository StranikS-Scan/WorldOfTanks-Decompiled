# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/View.py
import logging
from collections import namedtuple
from gui.Scaleform.framework.entities.ub_windows_tracker import UnboundWindowsTracker
from soft_exception import SoftException
from gui.Scaleform.framework.settings import UIFrameworkImpl
from gui.Scaleform.framework.entities.DisposableEntity import EntityState
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.Scaleform.framework.entities.view_interface import ViewInterface
from gui.doc_loaders import hints_layout
from gui.shared.events import FocusEvent
_logger = logging.getLogger(__name__)
_ViewKey = namedtuple('_ViewKey', ['alias', 'name'])

class ViewKey(_ViewKey):

    @staticmethod
    def __new__(cls, alias, name=None):
        if name is None:
            name = alias
        return _ViewKey.__new__(cls, alias, name)

    def __repr__(self):
        return '{}[alias={}, name={}]'.format(self.__class__.__name__, self.alias, self.name)

    def __eq__(self, other):
        return self.name == other.name and self.alias == other.alias if isinstance(other, ViewKey) else False


class ViewKeyDynamic(ViewKey):

    def __eq__(self, other):
        return self.alias == other.alias if isinstance(other, ViewKey) else False


CommonSoundSpaceSettings = namedtuple('CommonSoundSpaceSettings', ('name', 'entranceStates', 'exitStates', 'persistentSounds', 'stoppableSounds', 'priorities', 'autoStart', 'enterEvent', 'exitEvent'))

class View(AbstractViewMeta, ViewInterface):
    _COMMON_SOUND_SPACE = None
    __commonSoundManagers = {}

    def __init__(self, *args, **kwargs):
        super(View, self).__init__()
        from gui.Scaleform.framework import ViewSettings
        self.__settings = ViewSettings()
        self.__key = ViewKey(None, None)
        self.__initSoundManager()
        from gui.Scaleform.framework import ScopeTemplates
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        self.__ubWindowsTracker = None
        return

    def __repr__(self):
        return '{}[{}]=[key={}, scope={}, state={}]'.format(self.__class__.__name__, hex(id(self)), self.key, self.__scope, self.getState())

    def __del__(self):
        _logger.debug('View deleted: %r', self)

    @property
    def uiImpl(self):
        return UIFrameworkImpl.SCALEFORM

    @property
    def settings(self):
        return self.__settings

    @property
    def viewType(self):
        return self.__settings.type

    @property
    def viewScope(self):
        return self.__settings.scope

    @property
    def key(self):
        return self.__key

    @property
    def alias(self):
        return self.__key.alias

    @property
    def uniqueName(self):
        return self.__key.name

    @property
    def soundManager(self):
        return self.__commonSoundManagers.get(self._COMMON_SOUND_SPACE.name) if self._COMMON_SOUND_SPACE else self.__soundsManager

    def isViewModal(self):
        return self.__settings.isModal

    def getUniqueName(self):
        return self.__key.name

    def getSubContainersSettings(self):
        return self.settings.containers or ()

    def getCurrentScope(self):
        return self.__scope

    def setCurrentScope(self, scope):
        from gui.Scaleform.framework import ScopeTemplates
        if self.__settings is not None:
            if self.__settings.scope == ScopeTemplates.DYNAMIC_SCOPE:
                if scope != ScopeTemplates.DYNAMIC_SCOPE:
                    self.__scope = scope
                else:
                    raise SoftException('View.__scope cannot be a ScopeTemplates.DYNAMIC value. This value might have only settings.scope for {} view.'.format(self.alias))
            else:
                raise SoftException('You can not change a non-dynamic scope. Declare ScopeTemplates.DYNAMIC in settings for {} view'.format(self.alias))
        else:
            _logger.error('Can not change a current scope, until unimplemented __settings ')
        return

    def setSettings(self, settings):
        from gui.Scaleform.framework import ScopeTemplates
        if settings is not None:
            self.__settings = settings.toImmutableSettings()
            if self.__settings.scope != ScopeTemplates.DYNAMIC_SCOPE:
                self.__scope = self.__settings.scope
            self.__key = ViewKey(self.__settings.alias, self.uniqueName)
        else:
            _logger.debug('settings can`t be None!')
        return

    def setUniqueName(self, name):
        if name is not None:
            self.__key = ViewKey(self.alias, name)
        else:
            _logger.debug('Unique name cannot be set to None: %r', self)
        return

    def setupContextHints(self, hintID):
        if hintID is not None:
            hintsData = hints_layout.getLayout(hintID)
            if hintsData is not None:
                tutorialManager = self.app.tutorialManager if self.app is not None else None
                if tutorialManager is not None:
                    viewTutorialID = tutorialManager.getViewTutorialID(self.__key.name)
                    tutorialManager.setupViewContextHints(viewTutorialID, hintsData)
            else:
                _logger.error('Hint layout is not defined %r', hintID)
        return

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED))

    def getParentWindow(self):
        if self.__ubWindowsTracker is None:
            self.__ubWindowsTracker = UnboundWindowsTracker()
            self.__ubWindowsTracker.create()
        return self.__ubWindowsTracker.getParentWindow()

    def isVisible(self):
        return self.getState() == EntityState.CREATED

    def _populate(self):
        super(View, self)._populate()
        self.soundManager.startSpace(self._COMMON_SOUND_SPACE)

    def _destroy(self):
        if self.__ubWindowsTracker is not None:
            self.__ubWindowsTracker.destroy()
            self.__ubWindowsTracker = None
        self.soundManager.unregister(id(self))
        self.soundManager.clear(requester=id(self))
        if not self.soundManager.isUsed:
            if self._COMMON_SOUND_SPACE and not self._COMMON_SOUND_SPACE.persistentSounds:
                self.__commonSoundManagers.pop(self._COMMON_SOUND_SPACE.name)
        super(View, self)._destroy()
        return

    def __initSoundManager(self):
        from ViewSoundManager import _ViewSoundsManager
        if self._COMMON_SOUND_SPACE:
            soundSpaceName = self._COMMON_SOUND_SPACE.name
            if soundSpaceName not in self.__commonSoundManagers:
                self.__commonSoundManagers[soundSpaceName] = _ViewSoundsManager()
        else:
            self.__soundsManager = _ViewSoundsManager()
        self.soundManager.register(id(self), self._COMMON_SOUND_SPACE)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/View.py
import logging
import typing
import BigWorld
from collections import namedtuple
from gui.Scaleform.framework.settings import UIFrameworkImpl
from gui.Scaleform.framework.entities.DisposableEntity import EntityState
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.Scaleform.framework.entities.view_interface import ViewInterface
from gui.doc_loaders import hints_layout
from gui.shared.events import FocusEvent
from ids_generators import SequenceIDGenerator
from skeletons.tutorial import ITutorialLoader
from soft_exception import SoftException
from sound_gui_manager import ViewSoundExtension
from helpers import dependency, uniprof
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_view_id_generator = SequenceIDGenerator()
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


class View(AbstractViewMeta, ViewInterface):
    _COMMON_SOUND_SPACE = None
    __tutorialLoader = dependency.descriptor(ITutorialLoader)

    def __init__(self, *args, **kwargs):
        super(View, self).__init__()
        from gui.Scaleform.framework import ViewSettings
        self.__settings = ViewSettings()
        self.__uid = _view_id_generator.next()
        self.__key = ViewKey(None, None)
        self.__soundExtension = None
        self.initSoundManager(self._COMMON_SOUND_SPACE)
        from gui.Scaleform.framework import ScopeTemplates
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        self.__window = None
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
    def layer(self):
        return self.__settings.layer

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
        return self.__soundExtension.soundManager

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
            _logger.error('settings can`t be None!')
        return

    def setUniqueName(self, name):
        if name is not None:
            self.__key = ViewKey(self.alias, name)
        else:
            _logger.debug('Unique name cannot be set to None: %r', self)
        return

    def setupContextHints(self, hintID, hintsArgs=None):
        if hintID is not None:
            hintsData = hints_layout.getLayout(hintID)
            if hintsData is not None:
                viewTutorialID = self.__tutorialLoader.gui.getViewTutorialID(self.__key.name)
                self.__tutorialLoader.gui.setupViewContextHints(viewTutorialID, hintsData, hintsArgs=hintsArgs)
            else:
                _logger.error('Hint layout is not defined %r', hintID)
        return

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, ctx={'alias': alias}))

    def getParentWindow(self):
        return self.__window

    def setParentWindow(self, window):
        self.__window = window
        self.__uid = window.uniqueID

    def isVisible(self):
        return self.getState() == EntityState.CREATED

    def canBeClosed(self):
        return True

    def initSoundManager(self, soundSpace):
        if self.__soundExtension is not None:
            self.__soundExtension.destroySoundManager()
        self.__soundExtension = ViewSoundExtension(soundSpace)
        self.__soundExtension.initSoundManager()
        return

    def _populate(self):
        super(View, self)._populate()
        self.__soundExtension.startSoundSpace()

    def _destroy(self):
        self.__window = None
        self.__soundExtension.destroySoundManager()
        if self.__key.name and self.__key.alias:
            uniprof.exitFromRegion('Scaleform {} {}'.format(self.__key.name, self.__uid))
            BigWorld.notify(BigWorld.EventType.VIEW_DESTROYED, self.__key.alias, self.__uid, self.__key.name)
        super(View, self)._destroy()
        return

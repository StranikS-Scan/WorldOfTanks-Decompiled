# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/tooltip_mgr.py
import inspect
import itertools
import logging
from collections import namedtuple
import BigWorld
import Keys
from Event import SafeEvent, EventManager
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewStatus
from gui import InputHandler
from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared import events
from gui.shared.tooltips import builders
from helpers import dependency, uniprof
from ids_generators import SequenceIDGenerator
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
ToolTipInfo = namedtuple('ToolTipInfo', ('id', 'region', 'name'))
_logger = logging.getLogger(__name__)
_id_generator = SequenceIDGenerator()
LIVE_REGION_COLOR = 9611473
LOADING_REGION_COLOR = 12757201
_TOOLTIP_VARIANT_TYPED = 'typed'
_TOOLTIP_VARIANT_COMPLEX = 'complex'
_TOOLTIP_VARIANT_WULF = 'wulf'

class ToolTip(ToolTipMgrMeta):
    appLoader = dependency.descriptor(IAppLoader)
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, settings, advComplexSettings, *noTooltipSpaceIDs):
        super(ToolTip, self).__init__()
        self._areTooltipsDisabled = False
        self._isAllowedTypedTooltip = True
        self._noTooltipSpaceIDs = noTooltipSpaceIDs
        self._complex = builders.ComplexBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI, advComplexSettings)
        self._builders = builders.LazyBuildersCollection(settings)
        self._builders.addBuilder(builders.SimpleBuilder(TOOLTIPS_CONSTANTS.DEFAULT, TOOLTIPS_CONSTANTS.COMPLEX_UI))
        self._dynamic = {}
        self.__fastRedraw = False
        self.__isAdvancedKeyPressed = False
        self.__tooltipVariant = None
        self.__tooltipID = None
        self.__args = None
        self.__stateType = None
        self.__tooltipInfos = []
        self.__tooltipWindowId = 0
        self.__em = EventManager()
        self.onShow = SafeEvent(self.__em)
        self.onHide = SafeEvent(self.__em)
        return

    def show(self, data, linkage):
        self.as_showS(data, linkage, self.__fastRedraw)

    def hide(self):
        self.as_hideS()
        self.__destroyTooltipWindow()

    def handleKeyEvent(self, event):
        if not self.isReadyToHandleKey(event):
            return
        tooltipType = self.__tooltipID
        args = self.__args
        isSupportAdvanced = self.isSupportAdvanced(tooltipType, *args)
        if isSupportAdvanced:
            self.__fastRedraw = True
            if self.__tooltipVariant == _TOOLTIP_VARIANT_COMPLEX:
                self.onCreateComplexTooltip(tooltipType, self.__stateType)
            elif self.__tooltipVariant == _TOOLTIP_VARIANT_TYPED:
                self.onCreateTypedTooltip(tooltipType, args, self.__stateType)
            elif self.__tooltipVariant == _TOOLTIP_VARIANT_WULF:
                self.onCreateWulfTooltip(tooltipType, args, *self.__stateType)

    def isReadyToHandleKey(self, event):
        altPressed = event.key == Keys.KEY_LALT or event.key == Keys.KEY_RALT
        self.__isAdvancedKeyPressed = event.isKeyDown() and altPressed
        return self.__tooltipID is not None and altPressed

    def getTypedTooltipDefaultBuildArgs(self, tooltipType):
        builder = self._builders.getBuilder(tooltipType)
        if builder is None:
            raise SoftException('Builder for tooltip: type "%s" is not found', tooltipType)
        provider = builder.provider
        if provider is None:
            raise SoftException('"%s" does not have any provider', builder.__name__)
        spec = inspect.getargspec(provider.context.buildItem)
        return tuple(reversed([ (argName, defaultValue) for argName, defaultValue in itertools.izip_longest(reversed(spec.args), reversed(spec.defaults or [])) if argName != 'self' ]))

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        if self._areTooltipsDisabled:
            return
        elif not self._isAllowedTypedTooltip:
            return
        else:
            id = _id_generator.next()
            region = 'Typed tooltip {} {}'.format(tooltipType, id)
            name = 'tooltip {}'.format(tooltipType)
            info = ToolTipInfo(id, region, name)
            self.__tooltipInfos.append(info)
            uniprof.enterToRegion(region, LIVE_REGION_COLOR)
            BigWorld.notify(BigWorld.EventType.VIEW_CREATED, name, id, name)
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                region = 'Loading {} {}'.format(tooltipType, id)
                uniprof.enterToRegion(region, LOADING_REGION_COLOR)
                BigWorld.notify(BigWorld.EventType.LOADING_VIEW, name, id, name)
                try:
                    data, drawData, linkage = builder.build(stateType, self.__isAdvancedKeyPressed, *args)
                except:
                    BigWorld.notify(BigWorld.EventType.LOAD_FAILED, name, id, name)
                    uniprof.exitFromRegion(region)
                    raise

                BigWorld.notify(BigWorld.EventType.VIEW_LOADED, name, id, name)
                uniprof.exitFromRegion(region)
                if drawData:
                    self.show(drawData, linkage)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                BigWorld.notify(BigWorld.EventType.LOAD_FAILED, name, id, name)
                return
            self.__cacheTooltipData(_TOOLTIP_VARIANT_TYPED, tooltipType, args, stateType)
            self.onShow(tooltipType, args, self.__isAdvancedKeyPressed)
            if data is not None and data.isDynamic():
                data.changeVisibility(True)
                if tooltipType not in self._dynamic:
                    self._dynamic[tooltipType] = data
            return

    def onCreateWulfTooltip(self, tooltipType, args, x, y, parent=None):
        if not self._isAllowedTypedTooltip:
            return
        else:
            builder = self._builders.getBuilder(tooltipType)
            if builder is not None:
                data = builder.build(None, self.__isAdvancedKeyPressed, *args)
            else:
                _logger.warning('Tooltip can not be displayed: type "%s" is not found', tooltipType)
                return
            self.__destroyTooltipWindow()
            window = data.getDisplayableData(parent=parent, *args)
            window.load()
            window.move(int(x), int(y))
            window.onStatusChanged += self._onWulfWindowStatusChanged
            self.__tooltipWindowId = window.uniqueID
            self.__cacheTooltipData(_TOOLTIP_VARIANT_WULF, tooltipType, args, (x, y))
            self.onShow(tooltipType, args, self.__isAdvancedKeyPressed)
            return

    def onCreateComplexTooltip(self, tooltipID, stateType):
        if self._areTooltipsDisabled:
            return
        else:
            id = _id_generator.next()
            region = 'Complex tooltip {} {}'.format(tooltipID, id)
            info = ToolTipInfo(id, region, None)
            self.__tooltipInfos.append(info)
            uniprof.enterToRegion(region, LIVE_REGION_COLOR)
            _, drawData, linkage = self._complex.build(stateType, self.__isAdvancedKeyPressed, tooltipID)
            if drawData:
                self.show(drawData, linkage)
            self.__cacheTooltipData(_TOOLTIP_VARIANT_COMPLEX, tooltipID, tuple(), stateType)
            self.onShow(tooltipID, None, self.__isAdvancedKeyPressed)
            return

    def onHideTooltip(self, tooltipId):
        if not self._areTooltipsDisabled and tooltipId in self._dynamic:
            self._dynamic[tooltipId].changeVisibility(False)
        hideTooltipId = tooltipId or self.__tooltipID or ''
        self.__tooltipID = None
        self.__fastRedraw = False
        self.__destroyTooltipWindow()
        if self.__tooltipInfos:
            info = self.__tooltipInfos.pop(0)
            if info.name is not None:
                BigWorld.notify(BigWorld.EventType.VIEW_DESTROYED, info.name, info.id, info.name)
            uniprof.exitFromRegion(info.region)
        self.onHide(hideTooltipId)
        return

    def _onWulfWindowStatusChanged(self, state):
        if state == ViewStatus.DESTROYED:
            self.onHideTooltip(self.__tooltipID)

    def _populate(self):
        super(ToolTip, self)._populate()
        self.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.addListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        InputHandler.g_instance.onKeyDown += self.handleKeyEvent
        InputHandler.g_instance.onKeyUp += self.handleKeyEvent

    def _dispose(self):
        self._builders.clear()
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.removeListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        while self._dynamic:
            _, data = self._dynamic.popitem()
            data.stopUpdates()

        InputHandler.g_instance.onKeyDown -= self.handleKeyEvent
        InputHandler.g_instance.onKeyUp -= self.handleKeyEvent
        self.__destroyTooltipWindow()
        self.__em.clear()
        super(ToolTip, self)._dispose()

    def __onAccountBecomeNonPlayer(self):
        _logger.debug('Cancel tooltips on account become non player')
        self.hide()

    def __onGUISpaceEntered(self, spaceID):
        self._isAllowedTypedTooltip = spaceID not in self._noTooltipSpaceIDs

    def __onAppCreating(self, appNS):
        if self.app.appNS != appNS:
            self._areTooltipsDisabled = True

    def isSupportAdvanced(self, tooltipType, *args):
        isComplex = self.__tooltipVariant == _TOOLTIP_VARIANT_COMPLEX
        builder = self._complex if isComplex else self._builders.getBuilder(tooltipType)
        return False if builder is None else builder.supportAdvanced(tooltipType, *args)

    def __cacheTooltipData(self, tooltipType, tooltipID, args, stateType):
        self.__tooltipVariant = tooltipType
        self.__tooltipID = tooltipID
        self.__args = args
        self.__stateType = stateType

    def __destroyTooltipWindow(self):
        if self.__tooltipWindowId:
            window = self.gui.windowsManager.getWindow(self.__tooltipWindowId)
            if window is not None:
                window.destroy()
            self.__tooltipWindowId = 0
        return

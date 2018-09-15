# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_screen_view_base.py
import BigWorld
import Math
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.Scaleform.daapi.view.meta.NYScreenViewMeta import NYScreenViewMeta
from gui import g_guiResetters
from gui.shared.utils.timers import EachFrameTickTimer
from items.new_year_types import g_cache, INVALID_TOY_ID
from AvatarInputHandler.cameras import worldToScreenPos, mathUtils
from new_year import Mappings
from new_year.camera_switcher import CameraSwitcher
from shared_utils import BoundMethodWeakref
from gui.Scaleform.locale.NY import NY
from helpers.i18n import makeString as _ms
_CAMERA_SLIDE_TIME = 0.3

class NYScreenViewBase(NYScreenViewMeta):
    newYearController = dependency.descriptor(INewYearController)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        super(NYScreenViewBase, self).__init__()
        self._slots = []
        self._tabID = None
        self.__changeResCallbackID = None
        self.__scrollUpdateTimer = EachFrameTickTimer(BoundMethodWeakref(self.doScrollUpdate))
        self.__isActive = False
        self.__interfaceScale = 1.0
        return

    def _populate(self):
        super(NYScreenViewBase, self)._populate()
        self.newYearController.onSlotUpdated += self.__updateSlot
        self.newYearController.onInventoryUpdated += self.__onInventoryUpdated
        self.newYearController.onToysBreak += self._onToysBreak
        self.__setSlotsData()

    def _dispose(self):
        super(NYScreenViewBase, self)._dispose()
        if self.__isActive:
            self.onHide()
        self.__scrollUpdateTimer.destroy()
        self.newYearController.onSlotUpdated -= self.__updateSlot
        self.newYearController.onInventoryUpdated -= self.__onInventoryUpdated
        self.newYearController.onToysBreak -= self._onToysBreak

    def onShow(self):
        self.__readInterfaceScale()
        self.__setSlotsPosition()
        g_guiResetters.add(self.__onChangeScreenResolution)
        cameraSwitcher = self.customizableObjectsMgr.getSwitchHandler(CameraSwitcher)
        if cameraSwitcher is not None:
            cameraSwitcher.addScrollListener(self.__onScrollEvent)
        self.__isActive = True
        return

    def onHide(self):
        self.__isActive = False
        self.__scrollUpdateTimer.stop()
        if self.__changeResCallbackID is not None:
            BigWorld.cancelCallback(self.__changeResCallbackID)
            self.__changeResCallbackID = None
        cameraSwitcher = self.customizableObjectsMgr.getSwitchHandler(CameraSwitcher)
        if cameraSwitcher is not None:
            cameraSwitcher.removeScrollListener(self.__onScrollEvent)
        g_guiResetters.remove(self.__onChangeScreenResolution)
        return

    def _onToysBreak(self, toyIndexes, fromSlot):
        if toyIndexes and fromSlot:
            self.as_breakToyS(toyIndexes[0])

    def __onInventoryUpdated(self):
        self.__setSlotsData()

    def __setSlotsData(self):
        self._slots = [ int(slotID) for slotID in self.as_slotsIDS() ]
        data = self.newYearController.getPlacedToys(self._slots)
        self.as_initS([ self.__makeVO(k, v) for k, v in data.iteritems() ])

    def __updateSlot(self, slot, toy):
        slotID = slot.id
        if slotID in self._slots:
            self.as_initS([self.__makeVO(slotID, toy)])

    def __makeVO(self, slotID, item):
        toys = self.newYearController.getToysForSlot(slotID)
        toysCount = sum((toy.count for toy in toys))
        toyNewCount = sum((toy.newCount for toy in toys))
        slotType = g_cache.slots[slotID].type
        res = {'id': slotID,
         'slotType': slotType,
         'availableToysCount': toysCount,
         'newToyCount': toyNewCount,
         'tooltip': makeTooltip(_ms(NY.decorations_tooltip_empty_header(slotType)), _ms(NY.DECORATIONS_TOOLTIP_EMPTY_BODY))}
        if item.id != INVALID_TOY_ID:
            res.update({'toyIcon': item.icon or item.slotIcon,
             'toyId': str(item.id),
             'toyLevel': item.rank,
             'settings': item.setting})
        return res

    def __setSlotsPosition(self):
        anchorName = Mappings.ID_TO_ANCHOR[self._tabID]
        assert anchorName is not None
        entity = self.customizableObjectsMgr.getCustomizableEntity(anchorName)
        if entity is None:
            return
        else:
            targetPos = entity.position
            cylinderRadius = entity.slotsRadius
            leftPoint, rightPoint = self.__getSlotsPointsByRadius(targetPos, cylinderRadius)
            leftPointScreenX, _ = worldToScreenPos(leftPoint)
            rightPointScreenX, _ = worldToScreenPos(rightPoint)
            assert leftPointScreenX is not None
            assert rightPointScreenX is not None
            if self.__interfaceScale > 1.0:
                leftPointScreenX = round(leftPointScreenX / self.__interfaceScale)
                rightPointScreenX = round(rightPointScreenX / self.__interfaceScale)
            self.as_slotsPositionS(leftPointScreenX, rightPointScreenX)
            return

    @staticmethod
    def __getSlotsPointsByRadius(targetPos, cylinderRadius):
        initMatrix = Math.Matrix(BigWorld.camera().invViewMatrix)
        initDirection = initMatrix.applyToAxis(2)
        startPoint = initMatrix.translation
        xPlanePoint = startPoint + initMatrix.applyToAxis(0)
        zPlanePoint = startPoint + initDirection
        camHorizontalPlane = Math.Plane()
        camHorizontalPlane.init(startPoint, xPlanePoint, zPlanePoint)
        intersectedPoint = camHorizontalPlane.intersectRay(targetPos, Math.Vector3(0.0, 1.0, 0.0))
        leftPoint = intersectedPoint - initMatrix.applyToAxis(0) * cylinderRadius
        rightPoint = intersectedPoint + initMatrix.applyToAxis(0) * cylinderRadius
        return (leftPoint, rightPoint)

    def __onChangeScreenResolution(self):
        self.__scrollUpdateTimer.stop()
        self.__changeResCallbackID = BigWorld.callback(0.0, self.__afterChangeResolution)

    def __afterChangeResolution(self):
        self.__changeResCallbackID = None
        self.__readInterfaceScale()
        self.__setSlotsPosition()
        return

    def __onScrollEvent(self):
        if not self.__isActive:
            return
        if self.__scrollUpdateTimer.isActive:
            return
        self.__scrollUpdateTimer.start(_CAMERA_SLIDE_TIME)

    def doScrollUpdate(self):
        self.__setSlotsPosition()

    @dependency.replace_none_kwargs(settingsCore=ISettingsCore)
    def __readInterfaceScale(self, settingsCore=None):
        self.__interfaceScale = mathUtils.clamp(1.0, 2.0, round(settingsCore.interfaceScale.get()))

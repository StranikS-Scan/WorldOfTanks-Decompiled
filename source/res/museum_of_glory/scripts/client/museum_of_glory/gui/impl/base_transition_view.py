# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/impl/base_transition_view.py
import BigWorld
import CGF
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub import ViewImpl
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from museum_of_glory.cgf.museum_components import MuseumTankLightFade
from skeletons.gui.shared.utils import IHangarSpace
from GenericComponents import DynamicModelComponent, AnimatorComponent
_WAITER_ID = 'museum/transition'

class BaseTransitionView(ViewImpl):
    __slots__ = ('__delayer', '__bgLoaderId', '__textureMapping', '__isForwardRender', '__isFaded')
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args, **kwargs):
        super(BaseTransitionView, self).__init__(*args, **kwargs)
        self.__delayer = CallbackDelayer()
        self.__bgLoaderId = None
        self.__textureMapping = dict()
        self.__isForwardRender = False
        self.__isFaded = True
        return

    @property
    def materialQueryItems(self):
        pass

    @property
    def lightQueryItems(self):
        pass

    @property
    def waiterID(self):
        return _WAITER_ID

    def onTextureChanged(self):
        pass

    def onFadeIn(self):
        pass

    def onFadeOut(self):
        pass

    def updateTextures(self, **kwargs):
        if self.__bgLoaderId is not None:
            BigWorld.stopLoadResourceListBGTask(self.__bgLoaderId)
        self.__textureMapping = kwargs
        BigWorld.loadResourceListBG(kwargs.values(), self.__updateModelParameters)
        return

    def fade(self, isFadeIn=True):
        if isFadeIn:
            Waiting.show(self.waiterID, isAlwaysOnTop=True, isVisible=self.__isForwardRender)
        handler = self.__onFadeIn if isFadeIn else self.__onFadeOut
        if self.__isForwardRender or self.__isFaded == isFadeIn:
            handler()
            return
        self.__delayer.clearCallbacks()
        items = (CGF.GameObject, MuseumTankLightFade) + self.lightQueryItems
        delay = 0.0
        for item in CGF.Query(self.__hangarSpace.spaceID, items):
            go, fadeComp = item[:2]
            delay = max(delay, self.__fadeLight(go, fadeComp, isFadeIn))

        self.__delayer.delayCallback(delay, handler)

    def _initialize(self, *args, **kwargs):
        super(BaseTransitionView, self)._initialize(*args, **kwargs)
        self.__isForwardRender = not isRendererPipelineDeferred()

    def _finalize(self):
        Waiting.hide(self.waiterID)
        self.__delayer.destroy()
        if self.__bgLoaderId is not None:
            BigWorld.stopLoadResourceListBGTask(self.__bgLoaderId)
        self.__textureMapping.clear()
        super(BaseTransitionView, self)._finalize()
        return

    def __onFadeIn(self):
        self.__isFaded = True
        self.onFadeIn()

    def __onFadeOut(self):
        self.__isFaded = False
        self.onFadeOut()
        Waiting.hide(_WAITER_ID)

    def __fadeLight(self, go, fadeComp, isFadeIn):
        hManager = CGF.HierarchyManager(self.__hangarSpace.spaceID)
        delay = 0.0
        for child in hManager.getChildrenIncludingInactive(go):
            delay = max(delay, self.__fadeChild(child, isFadeIn == fadeComp.isFadeIn))

        return delay

    def __updateModelParameters(self, texturesDict):
        items = (CGF.GameObject, DynamicModelComponent, AnimatorComponent) + self.materialQueryItems
        for item in CGF.Query(self.__hangarSpace.spaceID, items):
            _, model, animComp = item[:3]
            for key, value in self.__textureMapping.iteritems():
                model.setMaterialParameterTexture(key, texturesDict[value])

            animComp.reset()
            animComp.start()

        self.__textureMapping.clear()
        self.onTextureChanged()

    @classmethod
    def __fadeChild(cls, child, isActive):
        animator = child.findComponentByType(AnimatorComponent)
        if animator is None:
            return 0.0
        elif not isActive:
            child.deactivate()
            return 0.0
        else:
            child.activate()
            animator.reset()
            animator.start()
            return animator.getDuration()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/soul_collector_wrappers.py
from __future__ import absolute_import
import logging
import typing
from builtins import range
import CGF
import GenericComponents
from halloween.cgf_components.soul_collector_components import SoulCollectorComponent, SoulCollectorProgressComponent
_logger = logging.getLogger(__name__)

class _AnimatorStatus(object):
    STATUS_ENABLED = 1.0
    STATUS_DISABLED = 0.0


class SoulCollectorProgressWrapper(object):

    def __init__(self, dynAccess, goLink):
        super(SoulCollectorProgressWrapper, self).__init__()
        self._currentProgress = 0
        self._gos = []
        self._dynAccess = dynAccess
        progressComponent = dynAccess.findRead(goLink, SoulCollectorProgressComponent)
        self.progressSectors = progressComponent.progressSectors
        self.sectorOffsetY = progressComponent.sectorOffsetY
        self.progressSequence = progressComponent.progressSequence
        parentGO = progressComponent.object
        queue = CGF.CommandQueue(parentGO.spaceID)
        for i in range(self.progressSectors):
            newGO = queue.createGameObject()
            queue.createComponent(newGO, CGF.HierarchyComponent, parentGO)
            queue.createComponent(newGO, CGF.TransformComponent, (0.0, float(i) * self.sectorOffsetY, 0.0))
            newAnimator = queue.createComponent(newGO, GenericComponents.AnimatorComponent, self.progressSequence, 0, 1, -1, True, '')
            newAnimator.start()
            self._gos.append(newGO)

    def isReady(self):
        for go in self._gos:
            if not go.valid:
                return False
            if not go.isActive:
                return False
            animator = self._getAnimator(go)
            if not bool(animator):
                return False
            if not animator.isPlaying():
                return False

        return True

    def onDestroy(self):
        self._gos = []
        self._dynAccess = None
        return

    def update(self, progress):
        newProgress = int(self.progressSectors * progress)
        if newProgress == self._currentProgress:
            return
        for i, go in enumerate(self._gos):
            animator = self._getAnimator(go, True)
            if i < newProgress:
                animator.setFloatParam('Status', _AnimatorStatus.STATUS_ENABLED)
            if i >= newProgress:
                animator.setFloatParam('Status', _AnimatorStatus.STATUS_DISABLED)

        self._currentProgress = newProgress

    def _getAnimator(self, go, isWritable=False):
        return self._dynAccess.findWrite(go, GenericComponents.AnimatorComponent) if isWritable else self._dynAccess.findRead(go, GenericComponents.AnimatorComponent)


class SoulCollectorWrapper(object):

    def __init__(self, go, component):
        super(SoulCollectorWrapper, self).__init__()
        self._isReady = False
        self._go = go
        self._dynAccess = CGF.DynamicComponentAccess(go.spaceID)
        self.loadProgressGO = component.loadProgressGO
        self.energyGlowAnimator = component.energyGlowAnimator
        self.auraAnimator = component.auraAnimator
        self.drainerAnimator = component.drainerAnimator
        self._progressComponent = SoulCollectorProgressWrapper(self._dynAccess, self.loadProgressGO)

    def onDestroy(self):
        self._go = None
        self._progressComponent.onDestroy()
        self._progressComponent = None
        return

    @property
    def isReady(self):
        if not self._isReady:
            self._isReady = bool(self._getAnimator(self.energyGlowAnimator)) and bool(self._getAnimator(self.auraAnimator)) and bool(self._getAnimator(self.drainerAnimator)) and self._progressComponent.isReady()
        return self._isReady

    def updateProgress(self, progress):
        energyGlowAnimator = self._getAnimator(self.energyGlowAnimator)
        if energyGlowAnimator:
            energyGlowAnimator.setFloatParam('FillStatus', progress)
        auraAnimator = self._getAnimator(self.auraAnimator)
        if auraAnimator:
            auraAnimator.setFloatParam('FillStatus', progress)
        self._progressComponent.update(progress)

    def updateIsCollecting(self, isCollecting):
        drainerAnimator = self._getAnimator(self.drainerAnimator)
        if drainerAnimator:
            drainerAnimator.setFloatParam('DrainStatus', _AnimatorStatus.STATUS_ENABLED if isCollecting else _AnimatorStatus.STATUS_DISABLED)

    def _getAnimator(self, uuid):
        if self._dynAccess is None:
            _logger.error('Unable to get animator: DynamicComponentAccess is None')
            return
        else:
            return self._dynAccess.findWrite(uuid, GenericComponents.AnimatorComponent) if uuid else None

    @staticmethod
    def init(go):
        if not go.valid:
            return None
        elif not go.isActive:
            return None
        else:
            component = go.findWrite(SoulCollectorComponent)
            return None if not component else SoulCollectorWrapper(go, component)

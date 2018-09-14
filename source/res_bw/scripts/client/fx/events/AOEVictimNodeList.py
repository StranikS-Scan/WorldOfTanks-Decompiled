# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/AOEVictimNodeList.py
import BigWorld
import random
from FX import s_sectionProcessors
import math
from ParticleSubSystem import ParticleSubSystem
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from ParticleSubSystem import MATRIX_SWARM_PSA
from Math import Vector3
from Math import Matrix
from bwdebug import *

class AOEVictimNodeList(ParticleSubSystem):

    def __init__(self):
        ParticleSubSystem.__init__(self)
        self.maxRange = 25.0
        self.nodeList = []
        self.calculatedTargets = []
        self.maxNodes = 5
        self.findTeam = 0

    def load(self, pSection, prereqs = None):
        self.nodeList = pSection.readStrings('Node')
        self.maxNodes = pSection.readFloat('maxNodes', 5.0)
        self.maxRange = pSection.readFloat('maxRange', 25.0)
        self.findTeam = pSection.readInt('findTeam', 0)
        return ParticleSubSystem.load(self, pSection)

    def isInteresting(self, subSystem):
        act = subSystem.action(MATRIX_SWARM_PSA)
        return act != None

    def setNodes(self, actor, source, target, subSystem):
        subSystem.action(MATRIX_SWARM_PSA).targets = self.calculatedTargets

    def randomStrike(self, source, basis, origin, left):
        pos = basis
        dpos = Vector3(random.random() * 2.0 - 1.0, 0.0, random.random() * 2.0 - 1.0)
        dpos.normalise()
        dpos[1] = random.random() * 0.1
        dpos.normalise()
        dotp = basis.dot(dpos)
        dpLeft = dotp < 0.0
        if left == dpLeft:
            dpos = dpos.scale(self.maxRange)
        else:
            dpos = dpos.scale(-self.maxRange)
        dpos = dpos + origin
        res = BigWorld.collide(source.spaceID, origin, dpos)
        if not res:
            return dpos
        return res[0]

    def findTargets(self, actor, source, target):
        self.calculatedTargets = []
        origin = source.position + Vector3(0, 0.5, 0)
        yaw = source.yaw + math.pi / 2.0
        basis = Vector3(math.sin(yaw), 0, math.cos(yaw))
        left = []
        right = []
        leftOver = self.maxNodes
        victims = []
        if hasattr(self, 'victims'):
            victims = self.victims
        elif self.findTeam == 1:
            team = BigWorld.player().team()
            for i in team.members.keys():
                entity = BigWorld.entity(i)
                if entity:
                    if (entity.position - origin).length < self.maxRange:
                        victims.append(entity)

            entity = BigWorld.player()
            if entity:
                if (entity.position - origin).length < self.maxRange:
                    victims.append(entity)
        for e in victims:
            if e.inWorld:
                dpos = e.position - origin
                dpos.normalise()
                dotp = basis.dot(dpos)
                leftOver -= 2
                try:
                    self.calculatedTargets.append(e.model.node('biped Spine'))
                except:
                    self.calculatedTargets.append(e.model.node('Scene Root'))

        while leftOver > 0:
            m = Matrix()
            if leftOver % 2 == 0:
                m.setTranslate(self.randomStrike(source, basis, origin, 1))
                self.calculatedTargets.append(m)
            else:
                m.setTranslate(self.randomStrike(source, basis, origin, 0))
                self.calculatedTargets.append(m)
            leftOver -= 1

    def go(self, effect, actor, source, target, **kargs):
        self.findTargets(actor, source, target)
        self.subSystemIterate(actor, source, target, self.setNodes)

    def eventTiming(self):
        return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors['AOEVictimNodeList'] = AOEVictimNodeList

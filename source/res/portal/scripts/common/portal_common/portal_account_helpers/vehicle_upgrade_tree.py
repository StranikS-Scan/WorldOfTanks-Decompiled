# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common/portal_account_helpers/vehicle_upgrade_tree.py
MAX_NODES_PER_LEVEL = 2

class VehicleUpgradeTreeSerializer(object):

    @staticmethod
    def deserializeTree(serializedTree, maxLevel=None):
        upgradeTree = {}
        currentLevel = 0
        while currentLevel < maxLevel or maxLevel is None:
            rightNodeResearchedMask = 1
            leftNodeResearchedMask = 2
            isRightNodeResearched = bool(serializedTree & rightNodeResearchedMask)
            isLeftNodeResearched = bool(serializedTree & leftNodeResearchedMask)
            if not maxLevel and not (isLeftNodeResearched or isRightNodeResearched):
                break
            upgradeTree[currentLevel] = {'leftNode': isLeftNodeResearched,
             'rightNode': isRightNodeResearched}
            serializedTree >>= 2
            currentLevel += 1

        return upgradeTree

    @staticmethod
    def deserializeTreeLevel(serializedTree, upgradeLevel):
        serializedTree >>= 2 * upgradeLevel
        rightNodeResearchedMask = 1
        leftNodeResearchedMask = 2
        isRightNodeResearched = bool(serializedTree & rightNodeResearchedMask)
        isLeftNodeResearched = bool(serializedTree & leftNodeResearchedMask)
        return {'leftNode': isLeftNodeResearched,
         'rightNode': isRightNodeResearched}

    @staticmethod
    def serializeTreeLevel(upgradeLevel, isRightNode=False):
        upgradeNodeMask = 1 if isRightNode else 2
        upgradeNodeMask <<= 2 * upgradeLevel
        return upgradeNodeMask

    @staticmethod
    def serializeTree(deserializedTree):
        resultBit = 0
        for levelSection in sorted(deserializedTree, reverse=True):
            resultBit <<= 2
            resultBit |= 1 if deserializedTree[levelSection]['rightNode'] else 0
            resultBit |= 2 if deserializedTree[levelSection]['leftNode'] else 0

        return resultBit


class VehicleUpgradesHelper(object):

    @staticmethod
    def getTurretDependencyGuns(upgradeNodes, turretNode, turretDescr):
        dependencyGuns = []
        turretLevel = turretNode / MAX_NODES_PER_LEVEL
        nodes = upgradeNodes
        turretGuns = [ gun.compactDescr for gun in turretDescr.guns ]
        for upgradeLevel, upgradeNode in nodes.iteritems():
            if upgradeLevel >= turretLevel:
                break
            for nodeNumber, node in enumerate(upgradeNode['nodes']):
                modules = node['modules']
                for module in modules:
                    if module in turretGuns:
                        dependencyNodeNumber = nodeNumber + upgradeLevel * MAX_NODES_PER_LEVEL
                        dependencyGuns.append((dependencyNodeNumber, module))

        return dependencyGuns

    @staticmethod
    def getGunDependencyTurrets(upgradeNodes, gunNode, vehicleDescr, gunDescr):
        dependencyTurrets = []
        gunLevel = gunNode / MAX_NODES_PER_LEVEL
        nodes = upgradeNodes
        turretsGuns = {}
        for turret in vehicleDescr.type.turrets[0]:
            turretsGuns[turret.compactDescr] = [ gun.compactDescr for gun in turret.guns ]

        for upgradeLevel, upgradeNode in nodes.iteritems():
            if upgradeLevel >= gunLevel:
                break
            for nodeNumber, node in enumerate(upgradeNode['nodes']):
                modules = node['modules']
                for module in modules:
                    if module in turretsGuns and gunDescr.compactDescr in turretsGuns[module]:
                        dependencyNodeNumber = nodeNumber + upgradeLevel * MAX_NODES_PER_LEVEL
                        dependencyTurrets.append((dependencyNodeNumber, module))

        return dependencyTurrets

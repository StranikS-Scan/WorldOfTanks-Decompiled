# Embedded file name: scripts/client/vehicles_check.py
import BigWorld
from items import vehicles
from debug_utils import *
import Math
import ResMgr
EPSILON = 0.001

def check(*vehicleNames):
    if len(vehicleNames) == 0:
        for nationID in (0, 1):
            for id in vehicles.g_list.getList(nationID).keys():
                _vehicleCheck(vehicles.g_cache.vehicle(nationID, id))

    else:
        for name in vehicleNames:
            _vehicleCheck(vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByName(name)))

    print 'Test finished!'


def _vehicleCheck(vehType):
    tank = vehType.name
    for state in ('undamaged', 'destroyed', 'exploded'):
        for chassis in vehType.chassis:
            _parameterCheck(chassis['hullPosition'], chassis['models'][state], ('Scene Root', 'Tank', 'V'), 'hullPosition', tank, chassis['name'])

        for hull in vehType.hulls:
            _parameterCheck(hull['turretPositions'][0], hull['models'][state], ('Scene Root', hull['turretHardPoints'][0]), 'turretPosition', tank, 'hull')

        for turret in vehType.turrets[0]:
            _parameterCheck(turret['gunPosition'], turret['models'][state], ('Scene Root', 'HP_gunJoint'), 'gunPosition', tank, turret['name'])


def _parameterCheck(pos, modelPath, nodes, parameter, tank, comp):
    modelSec = ResMgr.openSection(modelPath)
    if modelSec is None:
        print 'Error loading ', modelPath
        return
    else:
        visualFile = modelSec.readString('nodefullVisual') + '.visual'
        sec = ResMgr.openSection(visualFile)
        if sec is None:
            print "Error: can't find visual %s" % visualFile
            return
        translation = Math.Vector3()
        for node in nodes:
            sec = _findNodeSec(sec, node)
            if sec is None:
                print "Error: cant't find node %s in visual %s" % (node, visualFile)
                return
            translation += sec.readVector3('transform/row3')

        if (translation - pos).length > EPSILON:
            print 'Error: %s parameter is incorrect\n   Model:\t %s\n   Tank:\t  %s\n   Component: %s\n   Note: it must be <%s>' % (parameter,
             modelPath,
             tank,
             comp,
             translation)
        return


def _findNodeSec(sec, nodeName):
    for nodeSec in sec.values():
        if nodeSec.readString('identifier') == nodeName:
            return nodeSec

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/PhysicsTurretShape.py
import BigWorld
import Math
_DEBUG_WITH_SVG = False

class PhysicsTurretShape:
    PARAMS_DESC = {'zScale': (0.0, 2.0, 1.0, 0),
     'zPos': (-2.0, 2.0, 0.0, 1),
     'xScale': (0.0, 2.0, 1.0, 2),
     'xPos': (-2.0, 2.0, 0.0, 3),
     'yScale': (0.0, 2.0, 1.0, 4),
     'yPos': (-2.0, 2.0, 0.0, 5),
     'zRounding': (0.0, 1.0, 0.5, 6),
     'zRoundingCenter': (0.0, 1.0, 0.5, 7),
     'xRounding': (0.0, 1.0, 0.5, 8),
     'xRoundingCenter': (0.0, 1.0, 0.5, 9),
     'xSlope': (0.0, 1.0, 0.5, 10),
     'xSlopeCenter': (0.0, 1.0, 0.5, 11),
     'zSlope': (0.0, 1.0, 0.6, 12),
     'zSlopeCenter': (0.0, 1.0, 0.1, 13),
     'topSlope': (0.0, 1.0, 0.5, 14)}
    PARAM_NAME_BY_INDEX = dict(((desc[3], name) for name, desc in PARAMS_DESC.iteritems()))

    def __init__(self, bbMin, bbMax):
        self.__polys = None
        self.__params = dict(zip(PhysicsTurretShape.PARAMS_DESC.iterkeys(), (d[2] for d in PhysicsTurretShape.PARAMS_DESC.itervalues())))
        self.setTurretBox(bbMin, bbMax)
        self.__isDirty = True
        return

    def setTurretBox(self, bbMin, bbMax):
        self.__box = (Math.Vector3(bbMin), Math.Vector3(bbMax))
        self.__isDirty = True

    def setParam(self, name, value):
        d = PhysicsTurretShape.PARAMS_DESC[name]
        self.__params[name] = max(d[0], min(d[1], value))
        self.__isDirty = True

    def setParamByIndex(self, index, value):
        self.setParam(PhysicsTurretShape.PARAM_NAME_BY_INDEX[index], value)

    def setParams(self, params):
        for i, value in enumerate(params):
            self.setParamByIndex(i, value)

    def getParam(self, name):
        return self.__params[name]

    def getPolygons(self):
        if self.__isDirty:
            self.__recalcPolys()
            self.__isDirty = False
        return self.__polys

    def __recalcPolys(self):
        params = self.__params
        bbMin, bbMax = self.__box
        w = bbMax.x - bbMin.x
        h = bbMax.y - bbMin.y
        l = bbMax.z - bbMin.z
        sw = w * params['xScale']
        sh = h * params['yScale']
        sl = l * params['zScale']
        centerY = bbMin.y + h * 0.5 + params['yPos']
        minY = centerY - sh * 0.5
        maxY = centerY + sh * 0.5
        centerZ = bbMin.z + l * 0.5 + params['zPos']
        minZ = centerZ - sl * 0.5
        maxZ = centerZ + sl * 0.5
        centerX = bbMin.x + w * 0.5 + params['xPos']
        minX = centerX - sw * 0.5
        maxX = centerX + sw * 0.5
        roundedDeltaZ = sl * params['zRounding']
        alignedDeltaZ = sl - roundedDeltaZ
        roundingCenterZ = minZ + roundedDeltaZ * params['zRoundingCenter'] + alignedDeltaZ * 0.5
        alignedMinZ = roundingCenterZ - alignedDeltaZ * 0.5
        alignedMaxZ = roundingCenterZ + alignedDeltaZ * 0.5
        roundedDeltaX = sw * params['xRounding']
        alignedDeltaX = sw - roundedDeltaX
        roundingCenterX = minX + roundedDeltaX * params['xRoundingCenter'] + alignedDeltaX * 0.5
        alignedMinX = roundingCenterX - alignedDeltaX * 0.5
        alignedMaxX = roundingCenterX + alignedDeltaX * 0.5
        zTopScale = 1.0 - params['zSlope']
        topL = zTopScale * sl
        roundedTopDeltaZ = roundedDeltaZ * zTopScale
        alignedTopDeltaZ = alignedDeltaZ * zTopScale
        topCenterZ = minZ + topL * 0.5 + params['zSlopeCenter'] * params['zSlope'] * sl
        topMinZ = topCenterZ - topL * 0.5
        topMaxZ = topCenterZ + topL * 0.5
        topRoundingCenterZ = topMinZ + roundedTopDeltaZ * params['zRoundingCenter'] + alignedTopDeltaZ * 0.5
        topAlignedMinZ = topRoundingCenterZ - alignedTopDeltaZ * 0.5
        topAlignedMaxZ = topRoundingCenterZ + alignedTopDeltaZ * 0.5
        xTopScale = 1.0 - params['xSlope']
        topW = xTopScale * sw
        roundedTopDeltaX = roundedDeltaX * xTopScale
        alignedTopDeltaX = alignedDeltaX * xTopScale
        topCenterX = minX + topW * 0.5 + params['xSlopeCenter'] * params['xSlope'] * sw
        topMinX = topCenterX - topW * 0.5
        topMaxX = topCenterX + topW * 0.5
        topRoundingCenterX = topMinX + roundedTopDeltaX * params['xRoundingCenter'] + alignedTopDeltaX * 0.5
        topAlignedMinX = topRoundingCenterX - alignedTopDeltaX * 0.5
        topAlignedMaxX = topRoundingCenterX + alignedTopDeltaX * 0.5
        verts = [Math.Vector3((alignedMaxX, minY, minZ)),
         Math.Vector3((maxX, minY, alignedMinZ)),
         Math.Vector3((maxX, minY, alignedMaxZ)),
         Math.Vector3((alignedMaxX, minY, maxZ)),
         Math.Vector3((alignedMinX, minY, maxZ)),
         Math.Vector3((minX, minY, alignedMaxZ)),
         Math.Vector3((minX, minY, alignedMinZ)),
         Math.Vector3((alignedMinX, minY, minZ)),
         Math.Vector3((topAlignedMaxX, maxY, topMinZ)),
         Math.Vector3((topMaxX, maxY, topAlignedMinZ)),
         Math.Vector3((topMaxX, maxY, topAlignedMaxZ)),
         Math.Vector3((topAlignedMaxX, maxY, topMaxZ)),
         Math.Vector3((topAlignedMinX, maxY, topMaxZ)),
         Math.Vector3((topMinX, maxY, topAlignedMaxZ)),
         Math.Vector3((topMinX, maxY, topAlignedMinZ)),
         Math.Vector3((topAlignedMinX, maxY, topMinZ))]
        pt = Math.Vector3(verts[4])
        pt.y = minY + (1.0 - params['topSlope']) * (maxY - minY)
        plPt = verts[8]
        v2 = pt - plPt
        if v2.length < 0.001:
            plN = Math.Vector3((0.0, 1.0, 0.0))
        else:
            v1 = plPt - verts[15]
            if v1.length < 0.001:
                plN = Math.Vector3((0.0, v2.z, -v2.y))
            else:
                plN = v1 * v2
            if plN.length < 0.001:
                plN = Math.Vector3((0.0, 1.0, 0.0))
        for i in xrange(1, 7):
            s1 = verts[i]
            s2 = verts[i + 8]
            t = _intersectPlaneSegment(plPt, plN, s1, s2)
            verts[i + 8] = s1 + t * (s2 - s1)

        inds = ((7, 6, 5, 4, 3, 2, 1, 0),
         (8, 9, 10, 11, 12, 13, 14, 15),
         (0, 1, 9, 8),
         (1, 2, 10, 9),
         (2, 3, 11, 10),
         (3, 4, 12, 11),
         (4, 5, 13, 12),
         (5, 6, 14, 13),
         (6, 7, 15, 14),
         (7, 0, 8, 15))
        self.__polys = (tuple(verts), inds)
        if _DEBUG_WITH_SVG:
            scene = _Scene('turret')
            offs = 10
            for face in inds:
                for i in xrange(len(face)):
                    v1 = verts[face[i]]
                    v2 = verts[face[(i + 1) % len(face)]]
                    scene.add(_Line((offs + v1.x, offs + v1.z), (offs + v2.x, offs + v2.z)))

            scene.write_svg()


def _intersectPlaneSegment(planePt, planeN, seg1, seg2):
    dot = planeN.dot(seg2 - seg1)
    return 0.0 if dot * dot < 1e-08 else planeN.dot(planePt - seg1) / dot


def createPhysicsTurretShape(bbMin, bbMax):
    return PhysicsTurretShape(bbMin, bbMax)


class _Scene:

    def __init__(self, name='scene', height=400, width=400):
        self.name = name
        self.items = []
        self.height = height
        self.width = width

    def add(self, item):
        self.items.append(item)

    def strarray(self):
        var = ['<?xml version="1.0"?>\n',
         '<svg height="%d" width="%d" >\n' % (self.height, self.width),
         ' <g style="fill-opacity:1.0; stroke:black;\n',
         '  stroke-width:1;">\n']
        for item in self.items:
            var += item.strarray()

        var += [' </g>\n</svg>\n']
        return var

    def write_svg(self, filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + '.svg'
        file = open(self.svgname, 'w')
        file.writelines(self.strarray())
        file.close()

    def display(self, prog='explorer'):
        import os
        os.system('%s %s' % (prog, self.svgname))


class _Line:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def strarray(self):
        return ['  <line x1="%d" y1="%d" x2="%d" y2="%d" />\n' % (self.start[0],
          self.start[1],
          self.end[0],
          self.end[1])]

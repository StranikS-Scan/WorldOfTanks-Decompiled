# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/w2gt/w2gt_helper.py
import typing
if typing.TYPE_CHECKING:
    from typing import List, Tuple

def isPointInsidePolygonByRayTracing(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if min(y1, y2) < y <= max(y1, y2):
            if x <= max(x1, x2):
                if y1 != y2:
                    xinters = (y - y1) * (x2 - x1) / (y2 - y1) + x1
                else:
                    xinters = x1
                if x1 == x2 or x <= xinters:
                    inside = not inside

    return inside

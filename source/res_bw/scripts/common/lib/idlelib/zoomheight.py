# Embedded file name: scripts/common/Lib/idlelib/ZoomHeight.py
import re
import sys
from idlelib import macosxSupport

class ZoomHeight:
    menudefs = [('windows', [('_Zoom Height', '<<zoom-height>>')])]

    def __init__(self, editwin):
        self.editwin = editwin

    def zoom_height_event(self, event):
        top = self.editwin.top
        zoom_height(top)


def zoom_height(top):
    geom = top.wm_geometry()
    m = re.match('(\\d+)x(\\d+)\\+(-?\\d+)\\+(-?\\d+)', geom)
    if not m:
        top.bell()
        return
    width, height, x, y = map(int, m.groups())
    newheight = top.winfo_screenheight()
    if sys.platform == 'win32':
        newy = 0
        newheight = newheight - 72
    elif macosxSupport.isAquaTk():
        newy = 22
        newheight = newheight - newy - 88
    else:
        newy = 0
        newheight = newheight - 88
    if height >= newheight:
        newgeom = ''
    else:
        newgeom = '%dx%d+%d+%d' % (width,
         newheight,
         x,
         newy)
    top.wm_geometry(newgeom)

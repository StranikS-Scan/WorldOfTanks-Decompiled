# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/GuiDirReader.py
import ResMgr

class GuiDirReader(object):
    SCALEFORM_STARTUP_VIDEO_PATH = 'gui/flash/videos'
    SCALEFORM_STARTUP_VIDEO_MASK = 'videos/%s'
    VIDEO_EXTENSION = 'usm'

    @staticmethod
    def getAvailableIntroVideoFiles():
        ds = ResMgr.openSection(GuiDirReader.SCALEFORM_STARTUP_VIDEO_PATH)
        movieFiles = []
        for filename in ds.keys():
            try:
                basename, extension = filename.split('.')
            except ValueError:
                continue

            if extension == GuiDirReader.VIDEO_EXTENSION and basename[0:1] != '_':
                movieFiles.append(GuiDirReader.SCALEFORM_STARTUP_VIDEO_MASK % filename)

        ResMgr.purge(GuiDirReader.SCALEFORM_STARTUP_VIDEO_PATH, True)
        return movieFiles

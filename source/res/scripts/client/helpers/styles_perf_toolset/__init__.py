# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/styles_perf_toolset/__init__.py
import sys
from . import styles_overrider
from . import report_generator
g_stylesOverrider = styles_overrider.StylesOverrider()
g_reportGenerator = report_generator.ReportGenerator()

def setup():
    applyStylesFlag = '--applyStyles'
    if applyStylesFlag in sys.argv:
        path = sys.argv[sys.argv.index(applyStylesFlag) + 1]
        g_stylesOverrider.loadStylesConfig(path)
    generateReportFlag = '--generateReport'
    if generateReportFlag in sys.argv:
        location = sys.argv[sys.argv.index(generateReportFlag) + 1]
        g_reportGenerator.setLocation(location)


__all__ = ('styles_overrider', 'report_generator', 'g_stylesOverrider', 'g_reportGenerator', 'setup')

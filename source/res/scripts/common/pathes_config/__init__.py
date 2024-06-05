# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pathes_config/__init__.py
import os
import sys
import site

def setupPaths():
    root = '../../../../..'

    def expandPath(item):
        if not os.path.isabs(item):
            if item[0] == '~':
                item = os.path.expanduser(item)
            else:
                item = os.path.join(os.path.split(os.path.abspath(__file__))[0], item)
        return os.path.normpath(item)

    platformSuffix = None
    try:
        from pycommon import platform_info
    except:
        platformSuffix = None

    platformSuffix = platform_info.getPlatformSuffix()
    if not platformSuffix:
        raise SoftException('Unable to determine platform suffix')
    addPath = [root + '/tools/bigworld/server',
     root + '/res/bigworld/scripts/common',
     root + '/res/bigworld/scripts/common/Lib',
     root + '/res/bigworld/scripts/common/site-packages',
     root + '/res/bigworld/scripts/server_common',
     root + '/res/bigworld/scripts/server_common/lib-dynload-el7',
     root + '/res/wot/scripts',
     root + '/res/wot/scripts/base',
     root + '/res/wot/scripts/base/account_helpers',
     root + '/res/wot/scripts/server_common',
     root + '/res/wot/scripts/server_common/virtual_machine',
     root + '/res/wot/scripts/server_common/site-packages/' + platformSuffix,
     root + '/res/wot/scripts/common',
     root + '/res/wot/scripts/development/libs',
     root + '/tools/wot/server/bw_lib/bigworld/fake']
    for path in addPath:
        norm_path = expandPath(path)
        if norm_path.endswith('site-packages'):
            site.addsitedir(norm_path)
        sys.path.append(norm_path)

    bw_xml = expandPath(root + '/res/wot/server/bw.xml')
    if not os.path.exists(bw_xml):
        from shutil import copyfile
        copyfile(expandPath(root + '/res/wot/server/bw.xml.dist'), bw_xml)
    return

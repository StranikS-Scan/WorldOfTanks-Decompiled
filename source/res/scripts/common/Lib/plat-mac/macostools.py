# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/macostools.py
from warnings import warnpy3k
warnpy3k('In 3.x, the macostools module is removed.', stacklevel=2)
from Carbon import Res
from Carbon import File, Files
import os
import errno
import MacOS
try:
    openrf = MacOS.openrf
except AttributeError:
    openrf = open

Error = 'macostools.Error'
BUFSIZ = 524288
COPY_FLAGS = Files.kIsStationary | Files.kNameLocked | Files.kHasBundle | Files.kIsInvisible | Files.kIsAlias

def mkalias(src, dst, relative=None):
    srcfsr = File.FSRef(src)
    dstdir, dstname = os.path.split(dst)
    if not dstdir:
        dstdir = os.curdir
    dstdirfsr = File.FSRef(dstdir)
    if relative:
        relativefsr = File.FSRef(relative)
        alias = File.FSNewAlias(relativefsr, srcfsr)
    else:
        alias = srcfsr.FSNewAliasMinimal()
    dstfsr, dstfss = Res.FSCreateResourceFile(dstdirfsr, unicode(dstname), File.FSGetResourceForkName())
    h = Res.FSOpenResourceFile(dstfsr, File.FSGetResourceForkName(), 3)
    resource = Res.Resource(alias.data)
    resource.AddResource('alis', 0, '')
    Res.CloseResFile(h)
    dstfinfo = dstfss.FSpGetFInfo()
    dstfinfo.Flags = dstfinfo.Flags | 32768
    dstfss.FSpSetFInfo(dstfinfo)


def mkdirs(dst):
    if dst == '' or os.path.exists(dst):
        return
    head, tail = os.path.split(dst)
    if os.sep == ':' and ':' not in head:
        head = head + ':'
    mkdirs(head)
    try:
        os.mkdir(dst, 511)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def touched(dst):
    import warnings
    warnings.warn('macostools.touched() has been deprecated', DeprecationWarning, 2)


def touched_ae(dst):
    pardir = os.path.split(dst)[0]
    if not pardir:
        pardir = os.curdir
    import Finder
    f = Finder.Finder()
    f.update(File.FSRef(pardir))


def copy(src, dst, createpath=0, copydates=1, forcetype=None):
    src = File.pathname(src)
    dst = File.pathname(dst)
    if createpath:
        mkdirs(os.path.split(dst)[0])
    ifp = open(src, 'rb')
    ofp = open(dst, 'wb')
    d = ifp.read(BUFSIZ)
    while d:
        ofp.write(d)
        d = ifp.read(BUFSIZ)

    ifp.close()
    ofp.close()
    ifp = openrf(src, '*rb')
    ofp = openrf(dst, '*wb')
    d = ifp.read(BUFSIZ)
    while d:
        ofp.write(d)
        d = ifp.read(BUFSIZ)

    ifp.close()
    ofp.close()
    srcfss = File.FSSpec(src)
    dstfss = File.FSSpec(dst)
    sf = srcfss.FSpGetFInfo()
    df = dstfss.FSpGetFInfo()
    df.Creator, df.Type = sf.Creator, sf.Type
    if forcetype is not None:
        df.Type = forcetype
    df.Flags = sf.Flags & COPY_FLAGS
    dstfss.FSpSetFInfo(df)
    if copydates:
        srcfsr = File.FSRef(src)
        dstfsr = File.FSRef(dst)
        catinfo, _, _, _ = srcfsr.FSGetCatalogInfo(Files.kFSCatInfoAllDates)
        dstfsr.FSSetCatalogInfo(Files.kFSCatInfoAllDates, catinfo)
    return


def copytree(src, dst, copydates=1):
    if os.path.isdir(src):
        mkdirs(dst)
        files = os.listdir(src)
        for f in files:
            copytree(os.path.join(src, f), os.path.join(dst, f), copydates)

    else:
        copy(src, dst, 1, copydates)

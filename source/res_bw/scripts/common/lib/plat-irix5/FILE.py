# Embedded file name: scripts/common/Lib/plat-irix5/FILE.py
from warnings import warnpy3k
warnpy3k('the FILE module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
_MIPS_ISA_MIPS1 = 1
_MIPS_ISA_MIPS2 = 2
_MIPS_ISA_MIPS3 = 3
_MIPS_ISA_MIPS4 = 4
_MIPS_SIM_ABI32 = 1
_MIPS_SIM_NABI32 = 2
_MIPS_SIM_ABI64 = 3
P_MYID = -1
P_MYHOSTID = -1
ONBITSMAJOR = 7
ONBITSMINOR = 8
OMAXMAJ = 127
OMAXMIN = 255
NBITSMAJOR = 14
NBITSMINOR = 18
MAXMAJ = 511
MAXMIN = 262143
OLDDEV = 0
NEWDEV = 1
MKDEV_VER = NEWDEV

def major(dev):
    return __major(MKDEV_VER, dev)


def minor(dev):
    return __minor(MKDEV_VER, dev)


FD_SETSIZE = 1024
NBBY = 8
HP_NOPOLICY = 0
HP_ADDOFF = 1
HP_MULOFF = 2
SEMA_NAMSZ = 8
SEMA_NOHIST = 1
SEMA_LIFO = 2
SEMA_MUTEX = 4
SEMA_METER = 8
SEMAOP_PSEMA = 1
SEMAOP_VSEMA = 2
SEMAOP_CPSEMA = 3
SEMAOP_CVSEMA = 4
SEMAOP_WSEMA = 5
SEMAOP_UNSEMA = 6
SEMAOP_INIT = 7
SEMAOP_FREE = 8
SSOP_PHIT = 1
SSOP_PSLP = 2
SSOP_PWAKE = 6
SSOP_PRESIG = 7
SSOP_POSTSIG = 8
SSOP_VNOWAKE = 3
SSOP_VWAKE = 4
SSOP_CPHIT = 1
SSOP_CPMISS = 5
SSOP_CVNOWAKE = 3
SSOP_CVWAKE = 4
SSOP_WMISS = 5
SSOP_WWAKE = 4
SSOP_RMV = 9
TZERO = 10
SEMA_NOP = 0
SEMA_WAKE = 1
SEMA_VSEMA = 2
SEMA_SPINOP = 3
MR_ACCESS = 1
MR_UPDATE = 2

def cv_signal(cv):
    return cvsema(cv)


def cv_destroy(cv):
    return freesema(cv)


def mutex_enter(m):
    return psema(m, PZERO | PNOSTOP)


def mutex_exit(m):
    return vsema(m)


def mutex_destroy(m):
    return freesema(m)


def MUTEX_HELD(m):
    return ownsema(m)


def MUTEX_HELD(m):
    return 1


RW_READER = MR_ACCESS
RW_WRITER = MR_UPDATE

def rw_exit(r):
    return mrunlock(r)


def rw_tryupgrade(r):
    return cmrpromote(r)


def rw_downgrade(r):
    return mrdemote(r)


def rw_destroy(r):
    return mrfree(r)


def RW_WRITE_HELD(r):
    return ismrlocked(r, MR_UPDATE)


def RW_READ_HELD(r):
    return ismrlocked(r, MR_ACCESS)


SPLOCKNAMSIZ = 8
SPLOCK_NONE = 0
SPLOCK_SOFT = 1
SPLOCK_HARD = 2
OWNER_NONE = -1
MAP_LOCKID = 0
SPLOCK_MAX = 98304
SPLOCK_MAX = 32768
MIN_POOL_SIZE = 256
MAX_POOL_SIZE = 16384
DEF_SEMA_POOL = 8192
DEF_VNODE_POOL = 1024
DEF_FILE_POOL = 1024

def ownlock(x):
    return 1


def splock(x):
    return 1


def io_splock(x):
    return 1


def apvsema(x):
    return vsema(x)


def apcpsema(x):
    return cpsema(x)


def apcvsema(x):
    return cvsema(x)


def mp_mrunlock(a):
    return mrunlock(a)


def apvsema(x):
    return 0


def apcpsema(x):
    return 1


def apcvsema(x):
    return 0


def mp_mrunlock(a):
    return 0


FNDELAY = 4
FAPPEND = 8
FSYNC = 16
FNONBLOCK = 128
FASYNC = 4096
FNONBLK = FNONBLOCK
FDIRECT = 32768
FCREAT = 256
FTRUNC = 512
FEXCL = 1024
FNOCTTY = 2048
O_RDONLY = 0
O_WRONLY = 1
O_RDWR = 2
O_NDELAY = 4
O_APPEND = 8
O_SYNC = 16
O_NONBLOCK = 128
O_DIRECT = 32768
O_CREAT = 256
O_TRUNC = 512
O_EXCL = 1024
O_NOCTTY = 2048
F_DUPFD = 0
F_GETFD = 1
F_SETFD = 2
F_GETFL = 3
F_SETFL = 4
F_GETLK = 14
F_SETLK = 6
F_SETLKW = 7
F_CHKFL = 8
F_ALLOCSP = 10
F_FREESP = 11
F_SETBSDLK = 12
F_SETBSDLKW = 13
F_DIOINFO = 30
F_FSGETXATTR = 31
F_FSSETXATTR = 32
F_GETLK64 = 33
F_SETLK64 = 34
F_SETLKW64 = 35
F_ALLOCSP64 = 36
F_FREESP64 = 37
F_GETBMAP = 38
F_FSSETDM = 39
F_RSETLK = 20
F_RGETLK = 21
F_RSETLKW = 22
F_GETOWN = 23
F_SETOWN = 24
F_O_GETLK = 5
F_O_GETOWN = 10
F_O_SETOWN = 11
F_RDLCK = 1
F_WRLCK = 2
F_UNLCK = 3
O_ACCMODE = 3
FD_CLOEXEC = 1
FD_NODUP_FORK = 4
FMASK = 37119
FOPEN = 4294967295L
FREAD = 1
FWRITE = 2
FNDELAY = 4
FAPPEND = 8
FSYNC = 16
FNONBLOCK = 128
FASYNC = 4096
FNONBLK = FNONBLOCK
FDIRECT = 32768
FCREAT = 256
FTRUNC = 512
FEXCL = 1024
FNOCTTY = 2048
IRIX4_FASYNC = 64
FMARK = 16384
FDEFER = 8192
FINPROGRESS = 1024
FINVIS = 256
FNMFS = 8192
FCLOSEXEC = 1
FDSHD = 1
FDNOMARK = 2
FDIGNPROGRESS = 4
LOCK_SH = 1
LOCK_EX = 2
LOCK_NB = 4
LOCK_UN = 8
F_OK = 0
X_OK = 1
W_OK = 2
R_OK = 4
L_SET = 0
L_INCR = 1
L_XTND = 2

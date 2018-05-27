#!/usr/bin/env python

import exceptions
class UsageError(exceptions.Exception): pass

import sys
import pkg_resources

def main():
    if len(sys.argv) <= 1:
        raise UsageError("USAGE: verinfo DISTRIBUTIONNAME [PACKAGENAME]")
    DISTNAME=sys.argv[1]
    if len(sys.argv) >= 3:
        PACKNAME=sys.argv[2]
    else:
        PACKNAME=DISTNAME
    print("pkg_resources.require('%s') => " % (DISTNAME,), end=' ')
    print(pkg_resources.require(DISTNAME))
    print("import %s;print %s => " % (PACKNAME, PACKNAME,), end=' ')
    x = __import__(PACKNAME)
    print(x)
    print("import %s;print %s.__version__ => " % (PACKNAME, PACKNAME,), end=' ')
    print(hasattr(x, '__version__') and x.__version__)

if __name__ == "__main__":
    main()

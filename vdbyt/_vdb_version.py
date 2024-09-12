from packaging.version import Version
from ._vdb_on_demand import pyopenvdb


def _get_vdb_version():
    v_str = ".".join([str(mmr) for mmr in pyopenvdb.LIBRARY_VERSION])
    return Version(v_str)


vdb_version = _get_vdb_version()

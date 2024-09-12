try:
    import pyopenvdb
except ImportError:
    msg = "vdbyt requires an installation of openvdb and the accompanying python " \
          "module, pyopenvdb. If using conda, you may be able to install openvdb " \
          "from conda-forge, check https://anaconda.org/conda-forge/openvdb for " \
          "supported architectures. Otherwise, your OS package manager (homebrew, " \
          "yum, apt, etc) may have a build available or you can build from source."
    raise ImportError(msg)

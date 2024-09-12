import yt.data_objects.static_output

from ._vdb_on_demand import pyopenvdb as vdb
from ._vdb_version import vdb_version
import numpy as np
from packaging.version import Version
from yt.data_objects.construction_data_containers import YTCoveringGrid


def _normalize_variable_data(data,
                             log_the_variable: bool = False,
                             variable_tol: float | None = None,
                             renorm: bool = True,
                             renorm_min: float | None = None,
                             renorm_max: float | None = None,
                             ):
    if renorm:
        if renorm_min is None:
            renorm_min = data.min()
        if renorm_max is None:
            renorm_max = data.max()

    if log_the_variable is True:
        data = np.log10(data)
        if variable_tol is not None:
            variable_tol = np.log10(variable_tol)
        if renorm:
            renorm_max = np.log10(renorm_max)
            renorm_min = np.log10(renorm_min)

    # rescale from 0->1 for plotting

    if renorm:
        data = (data - renorm_min) / (renorm_max - renorm_min)
        data[data < 0] = 0
        data[data > 1] = 1

        if variable_tol is not None:
            variable_tol = (variable_tol - renorm_min) / (renorm_max - renorm_min)

    # take out threshold data -> set to 0
    if variable_tol is not None:
        data[data < variable_tol] = 0.0

    return data


def _get_cg_point_data(covering_grid: YTCoveringGrid,
                       variable_out: tuple[str, str],
                       log_the_variable: bool = False,
                       variable_tol: float | None = None,
                       renorm: bool = True,
                       renorm_min: float | None = None,
                       renorm_max: float | None = None,
                       ):
    # extract and process data from a covering grid

    data = covering_grid[variable_out].v
    data = _normalize_variable_data(data,
                                    log_the_variable=log_the_variable,
                                    variable_tol=variable_tol,
                                    renorm=renorm,
                                    renorm_max=renorm_max,
                                    renorm_min=renorm_min,)
    return data


def covering_grid_to_float_grid(covering_grid: YTCoveringGrid,
                                variable_out: tuple[str, str],
                                log_the_variable: bool = False,
                                variable_tol: float | None = None,
                                renorm: bool = True,
                                renorm_box: bool = True,
                                renorm_box_size: float = 10.0) -> vdb.FloatGrid:
    """
    Convert a single convering grid to a vdb FloatGrid, applying data transformations
    """
    pointdata = _get_cg_point_data(covering_grid, variable_out, log_the_variable=log_the_variable,
                                   variable_tol=variable_tol, renorm=renorm)

    # generate vdb
    domain_box = vdb.FloatGrid()
    domain_box.background = 0.0

    domain_box.copyFromArray(pointdata, ijk=(0, 0, 0), tolerance=0)

    # rescale to voxel size
    if renorm_box:
        vsize = renorm_box_size / float(pointdata.shape[0])  # assumes square box/shifting to x-axis units!
        domain_box.transform = vdb.createLinearTransform(voxelSize=vsize)  # tolist is for formatting

    return domain_box


def write_covering_grid_to_vdb(covering_grid: YTCoveringGrid,
                               variable_out: tuple[str, str],
                                outfilename: str,
                               log_the_variable: bool = False,
                               variable_tol: float | None = None,
                               renorm: bool = True,
                               renorm_box: bool = True,
                               renorm_box_size: float = 10.0) -> str:
    """
    extract data from a yt covering grid and write it to a vdb file
    """

    domain_box = covering_grid_to_float_grid(covering_grid,
                                             variable_out,
                                             log_the_variable=log_the_variable,
                                             variable_tol=variable_tol,
                                             renorm=renorm,
                                             renorm_box=renorm_box,
                                             renorm_box_size=renorm_box_size)

    if vdb_version >= Version("11.0.0"):  # min version might be lower?
        grids = [domain_box, ]
    else:
        grids = domain_box

    if not outfilename.endswith(".vdb"):
        outfilename = f"{outfilename}.vdb"
    vdb.write(outfilename, grids=grids)
    print('... done with writing vdb file to ' + outfilename)

    return outfilename


def write_yt_amr_as_vdb(ds: yt.data_objects.static_output.Dataset,
                        min_level: int,
                        max_level: int,
                        variable_out: tuple[str, str],
                        outfilename: str,
                        variable_tol: float | None = None,
                        log_the_variable: bool = False,
                        renorm: bool = True,
                        renorm_max: float | None = None,
                        renorm_min: float | None = None,
                        ):

    # Keep track of level 0 voxel size
    largestVSize = None
    output = []
    for level in range(min_level, max_level + 1):

        # Select specific level of grids set from dataset
        gs = ds.index.select_grids(level)

        # Initiate OpenVDB FloatGrid
        maskCube = vdb.FloatGrid()
        dataCube = vdb.FloatGrid()

        # Go over all grids in current level
        for index in range(len(gs)):

            subGrid = gs[index]

            # Extract grid (without ghost zone) with specific varible
            # subGridVar = subGrid[variable_out]

            # Extract grid (with ghost zone) with specific variable
            grid_data = subGrid.retrieve_ghost_zones(n_zones=1, fields=variable_out)[variable_out]
            grid_data = _normalize_variable_data(grid_data.v,
                                                 log_the_variable=log_the_variable,
                                                 variable_tol=variable_tol,
                                                 renorm=renorm,
                                                 renorm_max=renorm_max,
                                                 renorm_min=renorm_min,
                                                 )

            # Extract mask grid (eg. {[1 0 0 1],[0 1 0 1]...})
            mask = subGrid.child_mask

            # ijkout is the global x,y,z index in OpenVDB FloatGrid
            ijkout = subGrid.get_global_startindex()

            # Copy data from grid to OpenVDB FloatGrid starting from global x,y,z index in OpenVDB FloatGrid
            maskCube.copyFromArray(mask, ijk=(int(ijkout[0]), int(ijkout[1]), int(ijkout[2])))
            dataCube.copyFromArray(grid_data, ijk=(int(ijkout[0]), int(ijkout[1]), int(ijkout[2])))

        # Calculate a reasonable voxel size
        resolution = ds.domain_dimensions * ds.refine_by ** level
        vSize = 1 / float(resolution[0])

        # Keep track of level 0 voxel size
        if level == min_level:
            largestVSize = vSize

        # Scale and translate
        dataMatrix = [[vSize, 0, 0, 0], [0, vSize, 0, 0], [0, 0, vSize, 0],
                      [-vSize / 2 - largestVSize, -vSize / 2 - largestVSize, -vSize / 2 - largestVSize, 1]]
        maskMatrix = [[vSize, 0, 0, 0], [0, vSize, 0, 0], [0, 0, vSize, 0],
                      [vSize / 2 - largestVSize, vSize / 2 - largestVSize, vSize / 2 - largestVSize, 1]]
        dataCube.transform = vdb.createLinearTransform(dataMatrix)
        maskCube.transform = vdb.createLinearTransform(maskMatrix)

        # Write out the generated VDB
        dataCube.name = f"density_{level}"
        maskCube.name = f"mask_{level}"
        output.append(maskCube)
        output.append(dataCube)

    vdb.write(outfilename, grids=output)


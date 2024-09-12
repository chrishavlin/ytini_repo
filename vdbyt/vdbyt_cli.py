import click
from vdbyt.vdbyt import write_covering_grid_to_vdb, write_yt_amr_as_vdb
import yt


@click.group()
def cli():
    pass


@click.command()
@click.argument("yt_ds_file", type=click.STRING)
@click.argument("outfilename", type=click.STRING)
@click.argument("variable_field_type", type=click.STRING)
@click.argument("variable_name", type=click.STRING)
@click.option("--level", default=0, type=click.INT, help="The grid level to create the covering grid for")
@click.option("--sample", is_flag=True, show_default=True, default=False,
              help="If set, use yt.load_sample instead of load")
@click.option("--log_var", is_flag=True, default=False, help="take the log?")
@click.option("--var_tol", default=None, type=click.FLOAT, help="variable tolerance")
@click.option("--renorm", is_flag=True, default=True, help="renormalize data to (0,1)")
@click.option("--renorm_box", is_flag=True, default=True, help="renormalize the vdb box size")
@click.option("--renorm_box_size", default=10.0, help="renormalized vdb box size")
def convert_cg(yt_ds_file,
               outfilename,
               variable_field_type,
               variable_name,
               level,
               sample,
               log_var,
               var_tol,
               renorm,
               renorm_box,
               renorm_box_size, ):
    """
    Convert a yt ds to a single covering grid and export to a vdb file. For example:

    vdbyt convert-cg --sample --level 1 IsolatedGalaxy iso_gal_lev_0.vdb gas density

    """

    if sample:
        ds = yt.load_sample(yt_ds_file)
    else:
        ds = yt.load(yt_ds_file)

    if level > ds.max_level:
        print(f"pinning level to max level, {ds.max_level}")
        level = ds.max_level

    cg = ds.covering_grid(level=level, left_edge=ds.domain_left_edge,
                          dims=ds.domain_dimensions * ds.refine_by ** level)


    write_covering_grid_to_vdb(cg,
                               (variable_field_type, variable_name),
                               outfilename,
                               log_the_variable=log_var,
                               variable_tol=var_tol,
                               renorm=renorm,
                               renorm_box=renorm_box,
                               renorm_box_size=renorm_box_size)


cli.add_command(convert_cg)

@click.command()
@click.argument("yt_ds_file", type=click.STRING)
@click.argument("outfilename", type=click.STRING)
@click.argument("variable_field_type", type=click.STRING)
@click.argument("variable_name", type=click.STRING)
@click.option("--min_level", default=0, type=click.INT, help="The min grid level")
@click.option("--max_level", default=2, type=click.INT, help="The max grid level")
@click.option("--sample", is_flag=True, show_default=True, default=False,
              help="If set, use yt.load_sample instead of load")
@click.option("--log_var", is_flag=True, default=False, help="take the log?")
@click.option("--var_tol", default=None, type=click.FLOAT, help="variable tolerance")
@click.option("--renorm", is_flag=True, default=True, help="renormalize data to (0,1)")
@click.option("--renorm_min", default=None, type=click.FLOAT, help="Lower threshold for normalizing.")
@click.option("--renorm_max", default=None, type=click.FLOAT, help="Upper threshold for normalizing.")
def convert_amr(yt_ds_file,
               outfilename,
               variable_field_type,
               variable_name,
               min_level,
               max_level,
               sample,
               log_var,
               var_tol,
               renorm,
               renorm_min,
               renorm_max, ):
    """
    Convert a yt ds to a single covering grid and export to a vdb file. For example:

    vdbyt convert-amr --sample --renorm_min 1e-30 --renorm_max 1e-24 --min_level 0 --max_level 4 IsolatedGalaxy iso_gal_amr_0_4.vdb gas density

    """

    if sample:
        ds = yt.load_sample(yt_ds_file)
    else:
        ds = yt.load(yt_ds_file)


    write_yt_amr_as_vdb(ds,
                        min_level,
                        max_level,
                               (variable_field_type, variable_name),
                        outfilename,
                               log_the_variable=log_var,
                               variable_tol=var_tol,
                               renorm=renorm,
                               renorm_max=renorm_max,
                               renorm_min=renorm_min,
                        )


cli.add_command(convert_amr)


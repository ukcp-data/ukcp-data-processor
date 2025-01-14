import difflib
from filecmp import cmp
import subprocess

import iris

from ukcp_dp._input_data import InputData
from ukcp_dp.constants import DataFormat
from ukcp_dp.file_writers import write_file
from ukcp_dp.vocab_manager import Vocab


def run_write_test(
    data,
    input_files,
    reference_files,
    output_file_index,
    plot_type=None,
    overlay_file_name=None,
    data_format="csv",
):

    vocab = Vocab()
    input_data = InputData(vocab)
    input_data.set_inputs(data)

    cube_list = iris.cube.CubeList()
    if isinstance(input_files, list):
        for file in input_files:
            cube_list.append(iris.load_cube(file))
    else:
        cube_list.append(iris.load_cube(input_files))

    if overlay_file_name is not None:
        overlay_cube = iris.load_cube(overlay_file_name)
    else:
        overlay_cube = None

    output_files = write_file(
        cube_list,
        overlay_cube,
        "/tmp/",
        data_format,
        input_data,
        plot_type,
        process_version="0.0.0TEST",
        vocab=vocab,
    )

    diff = ""
    for inx, reference_file_name in enumerate(reference_files):
        if data_format == DataFormat.CSV:
            diff = _cmp_csv_files(
                diff, output_files[output_file_index[inx]], reference_file_name
            )
        elif data_format == DataFormat.NET_CDF:
            diff = _check_nc_files(
                diff, output_files[output_file_index[inx]], reference_file_name
            )
        else:
            diff = _check_shp_files(
                diff, output_files[output_file_index[inx]], reference_file_name
            )
    return diff


def _cmp_csv_files(diff, output_file, reference_file_name):
    with open(output_file, "r") as generated_file:
        with open(reference_file_name, "r") as reference_file:

            # Find and print the diff:
            for line in difflib.unified_diff(
                reference_file.readlines(),
                generated_file.readlines(),
                fromfile=reference_file_name,
                tofile=output_file,
                lineterm="",
            ):
                diff += line
    return diff


def _check_nc_files(diff, output_file, reference_file_name):
    result = subprocess.run(["nccmp", "-dmgf", output_file, reference_file_name])
    if result.returncode > 0:
        print(f"Files differ: {output_file}, " f"{reference_file_name}\n")
        diff += f"Files differ: {output_file}, " f"{reference_file_name}\n"
    return diff


def _check_shp_files(diff, output_file, reference_file_name):
    result = cmp(output_file, reference_file_name, shallow=False)
    if result is False:
        print(f"Files differ: {output_file}, " f"{reference_file_name}\n")
        diff += f"Files differ: {output_file}, " f"{reference_file_name}\n"
    return diff

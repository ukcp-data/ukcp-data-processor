import difflib

import iris

from ukcp_dp._input_data import InputData
from ukcp_dp.constants import DataFormat
from ukcp_dp.file_writers._file_writer import write_file
from ukcp_dp.vocab_manager import Vocab
from filecmp import cmp


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

    if data_format == DataFormat.CSV:
        read_param = "r"

    else:
        read_param = "rb"

    diff = ""
    for inx, reference_file_name in enumerate(reference_files):
        if data_format == DataFormat.CSV:
            with open(
                output_files[output_file_index[inx]], read_param
            ) as generated_file:
                with open(reference_file_name, read_param) as reference_file:

                    if data_format == DataFormat.CSV:
                        # Find and print the diff:
                        for line in difflib.unified_diff(
                            reference_file.readlines(),
                            generated_file.readlines(),
                            fromfile=reference_file_name,
                            tofile=output_files[output_file_index[inx]],
                            lineterm="",
                        ):
                            diff += line
                    else:
                        differ = difflib.Differ()
                        try:
                            for line in list(
                                differ.compare(
                                    reference_file.readlines(),
                                    generated_file.readlines(),
                                )
                            ):
                                if line.startswith("+ ") or line.startswith("- "):
                                    diff += line
                        except TypeError:
                            diff += (
                                f"ERROR comparing {reference_file_name} and "
                                "{output_files[output_file_index[inx]]}"
                            )
        else:
            result = cmp(
                output_files[output_file_index[inx]], reference_file_name, shallow=False
            )
            if result is False:
                print(
                    f"Files differ: {output_files[output_file_index[inx]]}, "
                    f"{reference_file_name}\n"
                )
                diff += (
                    f"Files differ: {output_files[output_file_index[inx]]}, "
                    f"{reference_file_name}\n"
                )

    return diff

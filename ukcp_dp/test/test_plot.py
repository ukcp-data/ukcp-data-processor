import iris

from ukcp_dp._input_data import InputData
from ukcp_dp.constants import COLLECTION_PROB, InputType
from ukcp_dp.plotters import write_plot
from ukcp_dp.vocab_manager import Vocab
from filecmp import cmp
from ukcp_dp.utils import get_plot_settings


def run_plot_test(
    data,
    input_files,
    reference_file,
    plot_type,
    title,
    image_format,
    overlay_file_name=None,
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

    if (
        input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB
        and input_data.get_value(InputType.RETURN_PERIOD) is not None
    ):
        extreme = True
    else:
        extreme = False

    plot_settings = get_plot_settings(
        vocab,
        input_data.get_value(InputType.IMAGE_SIZE),
        input_data.get_font_size(),
        input_data.get_value(InputType.VARIABLE)[0],
        extreme,
        input_data.get_value(InputType.COLLECTION),
    )

    output_file = write_plot(
        plot_type,
        "/tmp",
        image_format,
        input_data,
        cube_list,
        overlay_cube,
        title,
        vocab,
        plot_settings,
    )

    diff = ""

    result = cmp(output_file, reference_file, shallow=False)
    if result is False:
        print(f"Files differ: {output_file}, {reference_file}\n")
        diff = f"Files differ: {output_file}, {reference_file}\n"

    return diff

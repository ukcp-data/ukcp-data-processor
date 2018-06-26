import os
from time import gmtime, strftime

from _cdf_plotter import CdfPlotter
from _jp_plotter import JpPlotter
from _pdf_plotter import PdfPlotter
from _plume_plotter import PlumePlotter
from _postage_stamp_map_plotter import PostageStampMapPlotter
from _three_map_plotter import ThreeMapPlotter
from ukcp_dp.constants import PlotType


def write_plot(plot_type, output_path, image_format, input_data, cube_list,
               overlay_cube, title, vocab):
    """
    Generate a plot based on the plot type.

    @param plot_type (PlotType): the type of plot to generate
    @param output_path (str): the full path to the file
    @param image_format (ImageFormat): the format of the image to create,
        i.e. jpg, png
    @param input_data (InputData): an object containing user defined values
    @param cubes (list(iris cube)): a list of cubes containing the
        selected data
    @param title (str): a title for the plot
    @param vocab (Vocab): an instance of the ukcp_dp Vocab class
    """

    image_file = _get_image_file(output_path, image_format, plot_type)

    if plot_type == PlotType.CDF_PLOT:
        plotter = CdfPlotter()
    elif plot_type == PlotType.JP_PLOT:
        plotter = JpPlotter()
    elif plot_type == PlotType.PDF_PLOT:
        plotter = PdfPlotter()
    elif plot_type == PlotType.PLUME_PLOT:
        plotter = PlumePlotter()
    elif plot_type == PlotType.POSTAGE_STAMP_MAPS:
        plotter = PostageStampMapPlotter()
    elif plot_type == PlotType.THREE_MAPS:
        plotter = ThreeMapPlotter()
    else:
        raise Exception('Invalid plot type: {}'.format(plot_type))

    plotter.generate_plot(input_data, cube_list, overlay_cube, image_file,
                          title, vocab)

    return image_file


def _get_image_file(output_path, image_format, plot_type):
    timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
    plot_type_string = ''
    if plot_type is not None:
        plot_type_string = '{}_'.format(plot_type.lower())
    file_name = '{plot_type}{timestamp}.{image_format}'.format(
        plot_type=plot_type_string, timestamp=timestamp,
        image_format=image_format)
    return os.path.join(output_path, file_name)

"""
This module provides the public entry point write_plot to the plotters package.

"""
import os
from time import gmtime, strftime

from ukcp_dp.constants import PlotType
from ukcp_dp.plotters._cdf_plotter import CdfPlotter
from ukcp_dp.plotters._jp_plotter import JpPlotter
from ukcp_dp.plotters._pdf_plotter import PdfPlotter
from ukcp_dp.plotters._plume_plotter import PlumePlotter
from ukcp_dp.plotters._postage_stamp_map_plotter import PostageStampMapPlotter
from ukcp_dp.plotters._single_map_plotter import SingleMapPlotter
from ukcp_dp.plotters._three_map_plotter import ThreeMapPlotter


def write_plot(
    plot_type,
    output_path,
    image_format,
    input_data,
    cube_list,
    overlay_cube,
    title,
    vocab,
    plot_settings,
):
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
    @param plot_settings (StandardMap): an object containing plot settings

    """

    image_file = _get_image_file(output_path, image_format, plot_type)

    if plot_type == PlotType.CDF_PLOT:
        plotter = CdfPlotter()
    elif plot_type == PlotType.JP_PLOT:
        plotter = JpPlotter()
    elif plot_type == PlotType.PDF_PLOT:
        plotter = PdfPlotter()
    elif plot_type == PlotType.PLUME_PLOT or plot_type == PlotType.TIME_SERIES:
        plotter = PlumePlotter()
    elif plot_type == PlotType.POSTAGE_STAMP_MAPS:
        plotter = PostageStampMapPlotter()
    elif plot_type == PlotType.SINGLE_MAP:
        plotter = SingleMapPlotter()
    elif plot_type == PlotType.THREE_MAPS:
        plotter = ThreeMapPlotter()
    else:
        raise Exception("Invalid plot type: {}".format(plot_type))

    plotter.generate_plot(
        input_data, cube_list, overlay_cube, image_file, title, vocab, plot_settings
    )

    return image_file


def _get_image_file(output_path, image_format, plot_type):
    timestamp = strftime("%Y-%m-%dT%H-%M-%S", gmtime())
    plot_type_string = ""
    if plot_type is not None:
        plot_type_string = "{}_".format(plot_type.lower())
    file_name = "{plot_type}{timestamp}.{image_format}".format(
        plot_type=plot_type_string, timestamp=timestamp, image_format=image_format
    )
    return os.path.join(output_path, file_name)

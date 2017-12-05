from _cdf_plotter import CdfPlotter
from _pdf_plotter import PdfPlotter
from _plume_plotter import PlumePlotter
from _postage_stamp_map_plotter import PostageStampMapPlotter
from _three_map_plotter import ThreeMapPlotter
from ukcp_dp.constants import PlotType


def write_plot(plot_type, output_path, input_data, cubes, title):
    """
    Generate a plot based on the plot type.

    @param plot_type (PlotType): the type of plot to generate
    @param output_path (str): the full path to the file
    @param input_data (InputData): an object containing user defined values
    @param cubes (list(iris data cube)): a list of cubes containing the
        selected data
    @param title (str): a title for the plot
    """

    if plot_type == PlotType.CDF_PLOT:
        plotter = CdfPlotter()
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

    plotter.generate_plot(input_data, cubes, output_path, title)

    return

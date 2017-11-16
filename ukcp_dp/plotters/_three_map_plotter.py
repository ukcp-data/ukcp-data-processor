from _map_plotter import MapPlotter
import iris
import ukcp_dp.ukcp_standard_plots.mapper as maps
import ukcp_dp.ukcp_standard_plots.plotting_general as plotgeneral


class ThreeMapPlotter(MapPlotter):
    """
    The three map plotter class.

    This class extends MapPlotter with a _generate_subplots(self, cube,
    plotsettings).
    """

    def _generate_subplots(self, cube, plotsettings, fig):
        """
        Override base class method.

        @param cube (iris data cube): a cube containing the selected data
        @param plotsettings (StandardMap): an object containing plot settings
        @param fig (matplotlib.figure.Figure)
        """

        titles = ['10th Percentile', '50th Percentile', '90th Percentile']
        # TODO need to plot something other than ensemble
        for i, ensemble in enumerate(cube.slices_over('Ensemble member')):
            # TODO
            if i > 2:
                break

            ax = fig.add_subplot(2, 2, i+1, projection=plotsettings.proj)

            # Setting bar_orientation="none" here to override (prevent) drawing
            # the colorbar:
            result = maps.plot_standard_map(ensemble, plotsettings, fig=fig,
                                            ax=ax, barlab=None,
                                            bar_orientation="none",
                                            outfnames=None)
            # TODO this should come directly from the file
            # add a title
            title = titles[i]
            ax.set_title(title, fontsize='smaller')

        # add the sub plot to contain the bar
        ax = fig.add_subplot(2, 2, 4)
        ax.axis('off')

        return result

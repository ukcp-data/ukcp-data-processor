import calendar
import logging

from _graph_plotter import GraphPlotter
import cf_units
import datetime as dt
import iris
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from ukcp_dp.constants import COLLECTION_PROB, \
    COLLECTION_MARINE, ENSEMBLE_COLOURS, ENSEMBLE_GREYSCALES, \
    ENSEMBLE_LOWLIGHT, PERCENTILE_LINE_COLOUR, PERCENTILE_FILL, \
    RETURN_PERIODS, InputType


log = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        log.debug('_generate_graph')
        ax = plt.gca()

        if (self.input_data.get_value(InputType.COLLECTION) ==
                COLLECTION_PROB or
                self.input_data.get_value(InputType.COLLECTION) ==
                COLLECTION_MARINE):
            # plot the percentiles
            self._plot_probability_levels(self.cube_list[0], ax, True)

        else:
            if self.overlay_cube is not None:
                # plot the ensemble members
                self._plot_ensemble(self.cube_list[0], ax)
                # add overlay
                self._plot_probability_levels(self.overlay_cube, ax, False)
            else:
                # plot the ensemble members
                self._plot_ensemble(self.cube_list[0], ax)

        if (self.input_data.get_value(InputType.COLLECTION) ==
                COLLECTION_MARINE and
                self.input_data.get_value(InputType.METHOD).startswith(
                'return-periods')):
            # add axis labels
            plt.xlabel('Return period (years)')
            # use a log scale for the x axis
            ax.set_xscale("log")
            labs3 = np.array(['1', '10', '100', '1000'])
            locs3 = [np.int(lab) for lab in labs3]
            plt.xticks(locs3, labs3)

        else:
            # set the limits on the x axis, time axis
            set_x_limits(self.cube_list[0], ax)
            # add axis labels
            plt.xlabel('Date')

        plt.ylabel(self.input_data.get_value_label(InputType.VARIABLE)[0])

    def _plot_probability_levels(self, cube, ax, plot_fifty):
        # plot a shaded area between the 10th and 90th percentiles

        if (self.input_data.get_value(InputType.COLLECTION) ==
                COLLECTION_MARINE and
                self.input_data.get_value(InputType.METHOD).startswith(
                RETURN_PERIODS)):
            t_points = get_return_periods(cube, 'percentile')
        else:
            t_points = get_time_series(cube, 'percentile')

        # plot a line for the 50th
        if plot_fifty is True:
            percentile_cube = cube.extract(
                iris.Constraint(percentile=50))
            if percentile_cube is None:
                raise Exception(
                    'Attempted to plot the 50th percentile, but no data found')

            ax.plot(t_points, percentile_cube.data, label='50th Percentile',
                    color=PERCENTILE_LINE_COLOUR)

        if (self.input_data.get_value(InputType.COLLECTION) ==
                COLLECTION_PROB):
            # fill between the 10th and 90th
            lovals = cube.extract(iris.Constraint(percentile=10))
            hivals = cube.extract(iris.Constraint(percentile=90))
            label = '10th to 90th Percentile'
        else:
            # fill between the 10th and 90th
            lovals = cube.extract(iris.Constraint(percentile=5))
            hivals = cube.extract(iris.Constraint(percentile=95))
            label = '5th to 95th Percentile'

        if lovals is None or hivals is None:
            raise Exception(
                'Attempted to plot the {}, but no data found'.format(label))

        ax.fill_between(t_points, lovals.data, y2=hivals.data,
                        edgecolor="none", linewidth=0,
                        facecolor=PERCENTILE_FILL, zorder=0,
                        label=label)

    def _plot_ensemble(self, cube, ax):
        # Line plots of ensembles, highlighting selected members
        highlighted_ensemble_members = []
        # need to convert to ints to compare to values in the cube
        for member in self.input_data.get_value(
                InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS):
            highlighted_ensemble_members.append(int(member))

        if self.input_data.get_value(InputType.COLOUR_MODE) == 'c':
            colours = ENSEMBLE_COLOURS
            linestyle = ['solid', 'solid', 'solid', 'solid', 'solid']
        else:
            colours = ENSEMBLE_GREYSCALES
            linestyle = ['solid', 'dashed', 'dotted', 'solid', 'dashed']

        t_points = get_time_series(cube, 'ensemble_member')

        highlighted_counter = 0
        for ensemble_slice in cube.slices_over('ensemble_member'):
            ensemble = ensemble_slice.coord('ensemble_member').points[0]
            ensemble_name = ensemble_slice.coord(
                'ensemble_member_id').points[0]

            # highlighted ensembles should be included in the legend
            if ensemble in highlighted_ensemble_members:
                ax.plot(t_points, ensemble_slice.data, label=ensemble_name,
                        linestyle=linestyle[highlighted_counter],
                        color=colours[highlighted_counter], zorder=2)
                highlighted_counter += 1
            else:
                ax.plot(t_points, ensemble_slice.data,
                        linestyle='dotted',
                        color=ENSEMBLE_LOWLIGHT, zorder=1)


def get_return_periods(cube, slice_and_sel_coord):
    tcoord = cube.slices_over(
        slice_and_sel_coord).next().coord('return_period')
    return tcoord.points


def get_time_series(cube, slice_and_sel_coord):
    # Convert the time coord into fractions of years,
    # so we can easily use it for plotting:
    tcoord = cube.slices_over(slice_and_sel_coord).next().coord('time')
    if tcoord.units.calendar is not None:
        tsteps = list(tcoord.units.num2date(tcoord.points))

        if (isinstance(tsteps[0], dt.date) or
                isinstance(tsteps[0], dt.datetime)):
            tpoints = [t.year + t.timetuple().tm_yday /
                       (366.0 if calendar.isleap(t.year) else 365.0)
                       for t in tsteps]

        elif (isinstance(tsteps[0], cf_units.netcdftime.datetime) or
                isinstance(tsteps[0],
                           cf_units.netcdftime._netcdftime.Datetime360Day)):
            if tcoord.units.calendar == "360_day":
                tpoints = [t.year + t.dayofyr / 360.0 for t in tsteps]
            else:
                raise Exception("Got time points as netcdftime objects, "
                                "but NOT on a 360-day calendar.")

        else:
            log.warn("Using num2date on the time coord points didn't give "
                     "standard or netcdf date/datetime objects. The time "
                     "coord units were:{units}, num2date gave objects of type "
                     "{type}".format(units=tcoord.units, type=type(tsteps[0])))
            raise Exception("Unrecognised time coord data type, cannot plot")

    else:
        # Non-date time coord, like a year! Simples!
        log.info("Time coord points are not date-like objects, ASSUMEING they "
                 "are in year-fractions.")
        tpoints = tcoord.points

    return tpoints


def set_x_limits(cube, ax):
    # Get x-axis limits from the Cube's time coord.
    tcoord = cube.coord('time')
    # Do this differently for datetime-like coords vs integer coords:
    if tcoord.units.calendar is not None:
        if tcoord.units.name.startswith('hour'):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            # Place the limits at +/-1 year around the first & last time points
            xlims = [tcoord.units.num2date(tcoord.points[0] - 24 * 360),
                     tcoord.units.num2date(tcoord.points[-1] + 24 * 360)]
        elif tcoord.units.name.startswith('day'):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            # Place the limits at +/-1 year around the first & last time points
            xlims = [tcoord.units.num2date(tcoord.points[0] - 360),
                     tcoord.units.num2date(tcoord.points[-1] + 360)]
        else:
            raise Exception("Time coord units are " + str(tcoord.units)
                            + " but I can only handle days and hours!")
    else:
        # x-axis will be in units of integer years.
        # Place the limits at +/-1 year around the first & last time points:
        log.info("Time coord points are not date-like objects, ASSUMEING they "
                 "are in year-fractions.")
        tsteps = tcoord.points
        xlims = [tsteps[0] - 1.0,
                 tsteps[-1] + 1.0]

    # Now we've got proposed x-axis limits (as some data type),
    # we convert those x-axis limits into fractions of years.
    if isinstance(xlims[0], dt.date) or isinstance(xlims[0], dt.datetime):
        xlims_touse = [t.year + t.timetuple().tm_yday /
                       (366.0 if calendar.isleap(t.year) else 365.0)
                       for t in xlims]

    elif (isinstance(xlims[0], cf_units.netcdftime.datetime) or
            isinstance(xlims[0],
                       cf_units.netcdftime._netcdftime.Datetime360Day)):
        # Strictly-speaking, this might not be on a 360-day calendar,
        # but in practice we're unlikely to get this kind of object
        # unless a 360-day calendar is involved.
        log.info("Time axis limits specified with netcdftime.datetime "
                 "objects, ASSUMEING they're on a 360-day calendar.")
        xlims_touse = [t.year + t.dayofyr / 360.0 for t in xlims]

    elif isinstance(xlims[0], float) or isinstance(xlims[0], int):
        xlims_touse = xlims

    else:
        raise Exception("Unacceptable format for x-limits! Please use "
                        "standard or netcdf date/datetime objects, or ints or "
                        "floats.")

    # Finally, apply the limits:
    ax.set_xlim(xlims_touse)

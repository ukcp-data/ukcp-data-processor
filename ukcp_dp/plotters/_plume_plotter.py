import calendar
import logging

from matplotlib.ticker import MaxNLocator

import cf_units
import datetime as dt
import iris
from labellines import labelLines
import matplotlib.pyplot as plt
import numpy as np
from ukcp_dp.constants import (
    COLLECTION_PROB,
    COLLECTION_MARINE,
    ENSEMBLE_COLOURS,
    ENSEMBLE_GREYSCALES,
    ENSEMBLE_LOWLIGHT,
    PERCENTILE_LINE_COLOUR,
    PERCENTILE_FILL,
    RETURN_PERIODS,
    InputType,
    SCENARIO_COLOURS,
    SCENARIO_GREYSCALES,
)
from ukcp_dp.plotters._graph_plotter import GraphPlotter


LOG = logging.getLogger(__name__)


class PlumePlotter(GraphPlotter):
    """
    The plume plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    PROB_LABELS = {
        COLLECTION_PROB: ["5th", "10th", "25th", "50th", "75th", "90th", "95th"],
        COLLECTION_MARINE: [
            "5th",
            "10th",
            "30th",
            "33rd",
            "50th",
            "67th",
            "70th",
            "90th",
            "95th",
        ],
    }

    PERCENTILES = {
        COLLECTION_PROB: [5, 10, 25, 50, 75, 90, 95],
        COLLECTION_MARINE: [5, 10, 30, 33, 50, 67, 70, 90, 95],
    }

    FILL_FADE = {
        COLLECTION_PROB: [0.1, 0.2, 0.3, 0.3, 0.2, 0.1],
        COLLECTION_MARINE: [0.075, 0.2, 0.315, 0.5, 0.5, 0.315, 0.2, 0.075],
    }

    PLOT_TITLE = {
        COLLECTION_PROB: "showing the 5th, 10th, 25th, 50th, 75th, 90th and 95th "
        "percentiles",
        COLLECTION_MARINE: "showing the 5th, 10th, 30th, 33rd, 50th, 67th, 70th, 90th "
        "and 95th percentiles",
    }

    def _generate_graph(self):
        """
        Override base class method.

        """
        LOG.debug("_generate_graph")
        ax = plt.gca()

        if (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_PROB
            or self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE
        ):
            # plot the percentiles
            self._plot_probability_levels(self.cube_list[0], ax, False)

        else:
            if self.overlay_cube is not None:
                # plot the ensemble members
                self._plot_ensemble(self.cube_list[0], ax)
                # add overlay
                self._plot_probability_levels(self.overlay_cube, ax, True)
            else:
                # plot the ensemble members
                self._plot_ensemble(self.cube_list[0], ax)

        if self.input_data.get_value(
            InputType.COLLECTION
        ) == COLLECTION_MARINE and self.input_data.get_value(
            InputType.METHOD
        ).startswith(
            "return-periods"
        ):
            # add axis labels
            plt.xlabel("Return period (years)")
            # use a log scale for the x axis
            ax.set_xscale("log")
            labs3 = np.array(["1", "10", "100", "1000"])
            locs3 = [np.int(lab) for lab in labs3]
            plt.xticks(locs3, labs3)

        else:
            # set the limits on the x axis, time axis
            set_x_limits(self.cube_list[0], ax)
            # add axis labels
            plt.xlabel("Date")

        if self.input_data.get_value(InputType.Y_AXIS_MAX) is not None:
            y_max = float(self.input_data.get_value(InputType.Y_AXIS_MAX))
            y_min = float(self.input_data.get_value(InputType.Y_AXIS_MIN))
            ax.set_ylim(y_min, y_max)

        plt.ylabel(self.input_data.get_value_label(InputType.VARIABLE)[0])

    def _plot_probability_levels(self, cube, ax, is_overlay):
        # plot a shaded area between the 10th and 90th percentiles

        if self.input_data.get_value(
            InputType.COLLECTION
        ) == COLLECTION_MARINE and self.input_data.get_value(
            InputType.METHOD
        ).startswith(
            RETURN_PERIODS
        ):
            t_points = get_return_periods(cube, "percentile")
        else:
            t_points = get_time_series(cube, "percentile")

        if not is_overlay:
            self._plot_fiftieth_percentile_line(cube, ax, t_points)

        if (
            self.input_data.get_value(InputType.COLLECTION) == COLLECTION_MARINE
            and self.input_data.get_value(InputType.METHOD).startswith(RETURN_PERIODS)
        ) or is_overlay:
            self._single_fill(cube, ax, t_points, is_overlay)
        else:
            self._multi_fills(cube, ax, t_points)

    def _plot_fiftieth_percentile_line(self, cube, ax, t_points):
        # plot a line for the 50th percentile
        percentile_cube = cube.extract(iris.Constraint(percentile=50))
        if percentile_cube is None:
            raise Exception("Attempted to plot the 50th percentile, but no data found")

        line_colour = PERCENTILE_LINE_COLOUR

        if self.input_data.get_value(
            InputType.COLLECTION
        ) == COLLECTION_MARINE and self.input_data.get_value(
            InputType.METHOD
        ).startswith(
            RETURN_PERIODS
        ):
            ax.plot(
                t_points,
                percentile_cube.data,
                label="50th Percentile",
                color=line_colour,
                linewidth=self.line_width,
            )

        else:

            if self.input_data.get_value(InputType.COLOUR_MODE) == "c":
                line_colour = SCENARIO_COLOURS[cube.attributes["scenario"]][0]

            ax.plot(
                t_points,
                percentile_cube.data,
                color=line_colour,
                linewidth=self.line_width,
            )

    def _single_fill(self, cube, ax, t_points, is_overlay):
        if is_overlay:
            # fill between the 10th and 90th
            lovals = cube.extract(iris.Constraint(percentile=10))
            hivals = cube.extract(iris.Constraint(percentile=90))
            label = "Probabilistic (25km) 10th to 90th Percentile"
        else:
            # fill between the 5th and 95th
            lovals = cube.extract(iris.Constraint(percentile=5))
            hivals = cube.extract(iris.Constraint(percentile=95))
            label = "5th to 95th Percentile"

        if lovals is None or hivals is None:
            raise Exception("Attempted to plot the {}, but no data found".format(label))

        ax.fill_between(
            t_points,
            lovals.data,
            y2=hivals.data,
            edgecolor="none",
            linewidth=0,
            facecolor=PERCENTILE_FILL,
            zorder=0,
            label=label,
        )

    def _multi_fills(self, cube, ax, t_points):
        # fill between the percentile bounds
        percentile_data = []
        for percentile in self.PERCENTILES[
            self.input_data.get_value(InputType.COLLECTION)
        ]:
            percentile_data.append(
                cube.extract(iris.Constraint(percentile=percentile)).data
            )

        if self.input_data.get_value(InputType.COLOUR_MODE) == "c":
            fill_colour = SCENARIO_COLOURS[cube.attributes["scenario"]][0]
        else:
            fill_colour = SCENARIO_GREYSCALES[cube.attributes["scenario"]][0]

        for i in range(0, (len(percentile_data) - 1)):
            ax.fill_between(
                t_points,
                percentile_data[i],
                y2=percentile_data[i + 1],
                edgecolor="none",
                linewidth=0,
                facecolor=fill_colour,
                zorder=0,
                alpha=self.FILL_FADE[self.input_data.get_value(InputType.COLLECTION)][
                    i
                ],
            )

        self.show_legend = False
        if self.input_data.get_value(InputType.PLOT_TITLE) is None:
            self.title = "%s, %s" % (
                self.title,
                self.PLOT_TITLE[self.input_data.get_value(InputType.COLLECTION)],
            )

        if self.input_data.get_value(InputType.SHOW_LABELS):
            self._add_line_labels(ax, t_points, percentile_data)

    def _add_line_labels(self, ax, t_points, percentile_data):
        """
        Add labels to the boundaries between percentiles.

        We need to draw invisible lines first and then add labels to the lines.

        @param ax (Axes): axes
        @param t_points ([float]): time points
        @param percentile_data ([numpy.ndarray]): a list of arrays, with each
            array representing a percentiles data
        """
        # Generate the lines so we can add labels
        for i, data in enumerate(percentile_data):
            plt.plot(
                t_points,
                data,
                label=self.PROB_LABELS[self.input_data.get_value(InputType.COLLECTION)][
                    i
                ],
                alpha=0,
            )

        # work out where to put the line labels along the x axis
        x_min, x_max = ax.get_xlim()
        x_range = x_max - x_min
        xvals = (x_max - (x_range / 100 * 45), x_max - (x_range / 100 * 5))

        labelLines(
            plt.gca().get_lines(),
            align=False,
            color="k",
            xvals=xvals,
            backgroundcolor=None,
        )

        # The line labels have been added as text boxes. Now set the
        # backgrounds of the text boxes to be transparent
        children = plt.gca().get_children()
        for child in children:
            try:
                child.set_bbox(dict(alpha=0))
            except AttributeError:
                pass

    def _plot_ensemble(self, cube, ax):
        # Line plots of ensembles, highlighting selected members
        highlighted_ensemble_members = []
        # need to convert to ints to compare to values in the cube
        for member in self.input_data.get_value(InputType.HIGHLIGHTED_ENSEMBLE_MEMBERS):
            highlighted_ensemble_members.append(int(member))

        if self.input_data.get_value(InputType.COLOUR_MODE) == "c":
            colours = ENSEMBLE_COLOURS
            linestyle = ["solid", "solid", "solid", "solid", "solid"]
        else:
            colours = ENSEMBLE_GREYSCALES
            linestyle = ["solid", "dashed", "dotted", "solid", "dashed"]

        t_points = get_time_series(cube, "ensemble_member")

        # Set plot line width
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 900:
            highlighted_line_width = 0.7
            lowlighted_line_width = 0.4
        if self.input_data.get_value(InputType.IMAGE_SIZE) == 1200:
            highlighted_line_width = 1
            lowlighted_line_width = 0.5
        elif self.input_data.get_value(InputType.IMAGE_SIZE) == 2400:
            highlighted_line_width = 2
            lowlighted_line_width = 1

        highlighted_counter = 0
        for ensemble_slice in cube.slices_over("ensemble_member"):
            ensemble = ensemble_slice.coord("ensemble_member").points[0]
            ensemble_name = ensemble_slice.coord("ensemble_member_id").points[0]

            # highlighted ensembles should be included in the legend
            if ensemble in highlighted_ensemble_members:
                ax.plot(
                    t_points,
                    ensemble_slice.data,
                    label=ensemble_name,
                    linestyle=linestyle[highlighted_counter],
                    color=colours[highlighted_counter],
                    zorder=2,
                    linewidth=highlighted_line_width,
                )
                highlighted_counter += 1
            else:
                ax.plot(
                    t_points,
                    ensemble_slice.data,
                    linestyle="dotted",
                    color=ENSEMBLE_LOWLIGHT,
                    zorder=1,
                    linewidth=lowlighted_line_width,
                )

        if highlighted_counter == 0:
            self.show_legend = False


def get_return_periods(cube, slice_and_sel_coord):
    tcoord = cube.slices_over(slice_and_sel_coord).next().coord("return_period")
    return tcoord.points


def get_time_series(cube, slice_and_sel_coord):
    # Convert the time coord into fractions of years,
    # so we can easily use it for plotting:
    tcoord = cube.slices_over(slice_and_sel_coord).next().coord("time")
    if tcoord.units.calendar is not None:
        tsteps = list(tcoord.units.num2date(tcoord.points))

        if isinstance(tsteps[0], (dt.date, dt.datetime)):
            tpoints = [
                t.year
                + t.timetuple().tm_yday / (366.0 if calendar.isleap(t.year) else 365.0)
                for t in tsteps
            ]

        elif isinstance(
            tsteps[0],
            (cf_units.cftime.datetime, cf_units.cftime._cftime.Datetime360Day),
        ):
            if tcoord.units.calendar == "360_day":
                tpoints = [t.year + t.dayofyr / 360.0 for t in tsteps]
            else:
                raise Exception(
                    "Got time points as cftime objects, "
                    "but NOT on a 360-day calendar."
                )

        else:
            LOG.warning(
                "Using num2date on the time coord points didn't give "
                "standard or netcdf date/datetime objects. The time "
                "coord units were:%s, num2date gave objects of type "
                "%s",
                units=tcoord.units,
                type=type(tsteps[0]),
            )
            raise Exception("Unrecognised time coord data type, cannot plot")

    else:
        # Non-date time coord, like a year! Simples!
        LOG.info(
            "Time coord points are not date-like objects, ASSUMEING they "
            "are in year-fractions."
        )
        tpoints = tcoord.points

    return tpoints


def set_x_limits(cube, ax):
    # Get x-axis limits from the Cube's time coord.
    tcoord = cube.coord("time")
    # Do this differently for datetime-like coords vs integer coords:
    if tcoord.units.calendar is not None:
        if tcoord.units.name.startswith("hour"):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            xlims = [
                tcoord.units.num2date(tcoord.points[0]),
                tcoord.units.num2date(tcoord.points[-1]),
            ]
        elif tcoord.units.name.startswith("day"):
            # Can't easily use dt.timedelta objects with netcdfdatetimes,
            # which is likely to be what these are.
            xlims = [
                tcoord.units.num2date(tcoord.points[0]),
                tcoord.units.num2date(tcoord.points[-1]),
            ]
        else:
            raise Exception(
                "Time coord units are "
                + str(tcoord.units)
                + " but I can only handle days and hours!"
            )
    else:
        # x-axis will be in units of integer years.
        LOG.info(
            "Time coord points are not date-like objects, ASSUMEING they "
            "are in year-fractions."
        )
        tsteps = tcoord.points
        xlims = [tsteps[0], tsteps[-1]]

    # Now we've got proposed x-axis limits (as some data type),
    # we convert those x-axis limits into fractions of years.
    if isinstance(xlims[0], (dt.date, dt.datetime)):
        xlims_touse = [
            t.year
            + t.timetuple().tm_yday / (366.0 if calendar.isleap(t.year) else 365.0)
            for t in xlims
        ]

    elif isinstance(
        xlims[0], (cf_units.cftime.datetime, cf_units.cftime._cftime.Datetime360Day)
    ):
        # Strictly-speaking, this might not be on a 360-day calendar,
        # but in practice we're unlikely to get this kind of object
        # unless a 360-day calendar is involved.
        LOG.info(
            "Time axis limits specified with cftime.datetime "
            "objects, ASSUMEING they're on a 360-day calendar."
        )
        xlims_touse = [t.year + t.dayofyr / 360.0 for t in xlims]

    elif isinstance(xlims[0], (float, int)):
        xlims_touse = xlims

    else:
        raise Exception(
            "Unacceptable format for x-limits! Please use "
            "standard or netcdf date/datetime objects, or ints or "
            "floats."
        )

    # Finally, apply the limits:
    ax.set_xlim(xlims_touse)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

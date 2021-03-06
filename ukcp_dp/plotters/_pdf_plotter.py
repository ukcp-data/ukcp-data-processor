import logging

import matplotlib.pyplot as plt
from ukcp_dp.constants import (
    COLLECTION_PROB,
    DataType,
    InputType,
    PDF_LABEL,
    SCENARIO_COLOURS,
    SCENARIO_GREYSCALES,
)
from ukcp_dp.plotters._graph_plotter import GraphPlotter


LOG = logging.getLogger(__name__)


class PdfPlotter(GraphPlotter):
    """
    The pdf plotter class.

    This class extends BasePlotter with a _generate_graph(self).
    """

    def _generate_graph(self):
        """
        Override base class method.

        """
        LOG.debug("_generate_graph")

        if self.input_data.get_value(InputType.COLOUR_MODE) == "c":
            colours = SCENARIO_COLOURS

        else:
            colours = SCENARIO_GREYSCALES

        if self.input_data.get_value(InputType.COLLECTION) != COLLECTION_PROB:
            raise Exception("A PDF plot requires probabilistic data")

        for scenario_cube in self.cube_list:
            if scenario_cube.attributes["prob_data_type"] == DataType.PDF:
                continue
            pdf_data = self._get_pdf_data_for_scenario(
                scenario_cube.attributes["scenario"]
            )

            label = self.vocab.get_collection_term_label(
                InputType.SCENARIO, scenario_cube.attributes["scenario"]
            )
            plt.plot(
                scenario_cube.data,
                pdf_data,
                label=label,
                linestyle=colours[scenario_cube.attributes["scenario"]][1],
                color=colours[scenario_cube.attributes["scenario"]][0],
                linewidth=self.line_width,
            )

        plt.xlabel(self.input_data.get_value_label(InputType.VARIABLE)[0])
        plt.ylabel(PDF_LABEL)

    def _get_pdf_data_for_scenario(self, scenario):
        for scenario_cube in self.cube_list:
            if (
                scenario_cube.attributes["prob_data_type"] == DataType.PDF
                and scenario_cube.attributes["scenario"] == scenario
            ):
                return scenario_cube.data

        return None

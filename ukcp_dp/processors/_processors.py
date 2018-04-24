import copy
import logging

import numpy

import iris
from ukcp_dp.constants import InputType, ANNUAL, MONTHLY, SEASONAL
from ukcp_dp.data_extractor import DataExtractor
from ukcp_dp.file_finder import get_file_lists


log = logging.getLogger(__name__)


class SamplingProcessor(object):
    """
    Extract sample data based on user selection criteria.
    """

    def __init__(self, cube_list, input_data, vocab):
        """
        Initialise the SamplingProcessor.

        @param cube_list(CubeList) an iris cube list
        @param input_data (InputData) an object containing user defined values
        @param vocab (Vocab): an instance of the ukcp_dp Vocab class
        """
        self.input_data = input_data
        self.vocab = vocab
        self.cubes = self._sample_cubes(cube_list)
        log.debug('Processor __init__ finished')

    def get_cubes(self):
        """
        Get an iris cube list.

        The data are based on the selection criteria from the input_data.

        @return an iris cube list, one cube per scenario, per variable
        """
        log.info('get_cubes')
        return self.cubes

    def _sample_cubes(self, cube_list):
        """
        Get an iris cube list based on the sampling selection criteria from the
        input_data.

        @param cube_list (iris cube list): a list of cubes containing the
            selected data, one cube per scenario, per variable. N.B. Only the
            first cube is used.
        @return an iris cube list containing the selected samples
        """
        log.debug('_sample_cubes')

        if self.input_data.get_value(InputType.SAMPLING_METHOD) == 'id':
            return self._sample_cubes_by_id(cube_list)
        elif self.input_data.get_value(InputType.SAMPLING_METHOD) == 'random':
            return self._sample_cubes_random(cube_list)
        elif self.input_data.get_value(InputType.SAMPLING_METHOD) == 'subset':
            return self._sample_cubes_by_subset(cube_list)
        else:  # self.input_data.get_value(InputType.SAMPLING_METHOD) == 'all':
            return self._sample_cubes_all(cube_list)

    def _sample_cubes_all(self, cube_list):
        log.debug('_sample_cubes_all')
        return cube_list

    def _sample_cubes_by_id(self, cube_list):
        """
        Get a cube that contains the samples listed in SAMPLING_ID.
        """
        log.debug('_sample_cubes_by_id')
        constraint = iris.Constraint(sample=self.input_data.get_value(
            InputType.SAMPLING_ID))
        selected_cubes = iris.cube.CubeList()

        for cube in cube_list:
            selected_cubes.append(cube.extract(constraint))
        return selected_cubes

    def _sample_cubes_random(self, cube_list):
        """
        Get a random selection of samples, the number of samples is
        RANDOM_SAMPLING_COUNT.
        """
        log.debug('_sample_cubes_random')
        random_sample_count = self.input_data.get_value(
            InputType.RANDOM_SAMPLING_COUNT)

        random_ids = self._get_random_ids(
            cube_list[0], random_sample_count, False)
        constraint = iris.Constraint(sample=random_ids)
        selected_cubes = iris.cube.CubeList()

        for cube in cube_list:
            selected_cubes.append(cube.extract(constraint))
        return selected_cubes

    def _sample_cubes_by_subset(self, cube_list):
        log.debug('_sample_cubes_by_subset')

        # Get a set of sample ids based on the first sampling variable
        # First get a new cube
        cube_s1 = self._get_cubes_for_subset(
            self.input_data.get_value(InputType.SAMPLING_VARIABLE_1),
            self.input_data.get_value(InputType.SAMPLING_TEMPORAL_AVERAGE_1))

        # Extract the ids based on the sampling percentile
        sample_ids = self._get_percentile_ids(
            cube_s1,
            self.input_data.get_value(InputType.SAMPLING_PERCENTILE_1))

        # If a second sampling variable was provided then further restrict the
        # ids
        if self.input_data.get_value(InputType.SAMPLING_SUBSET_COUNT) == '2':
            # First get a new cube
            cube_s2 = self._get_cubes_for_subset(
                self.input_data.get_value(InputType.SAMPLING_VARIABLE_2),
                self.input_data.get_value(
                    InputType.SAMPLING_TEMPORAL_AVERAGE_2))

            # Filter the cube based on the ids from the first sampling variable
            constraint = iris.Constraint(sample=sample_ids)
            cube_s2 = cube_s2.extract(constraint)

            # Extract the ids based on the sampling percentile
            sample_ids = self._get_percentile_ids(
                cube_s2,
                self.input_data.get_value(InputType.SAMPLING_PERCENTILE_2))

        constraint = iris.Constraint(sample=sample_ids)
        selected_cubes = iris.cube.CubeList()

        for cube in cube_list:
            selected_cubes.append(cube.extract(constraint))
        return selected_cubes

    def _get_cubes_for_subset(self, variable, time_period):
        """
        Get a list of cubes.
        A copy of self.get_input_data is used, which has had the variable,
        time_period and temporal_average_type updated.
        """
        input_data = self.get_input_data(variable, time_period)
        file_lists = get_file_lists(input_data)
        data_extractor = DataExtractor(file_lists, input_data)
        cubes = data_extractor.get_cubes()
        if len(cubes) > 1:
            log.error('Found more than 1 cube')
        return data_extractor.get_cubes()[0]

    def get_input_data(self, variable, time_period):
        """
        Make a deep copy of self.get_input_data then update variable,
        time_period and temporal_average_type
        """
        input_data = copy.deepcopy(self.input_data)
        input_data.set_values(InputType.VARIABLE, [variable])
        input_data.set_value(InputType.TIME_PERIOD, time_period)

        if time_period in self.vocab.get_collection_terms(MONTHLY):
            temporal_average_type = MONTHLY
        elif time_period == ANNUAL:
            temporal_average_type = ANNUAL
        else:
            temporal_average_type = SEASONAL
        input_data.set_value(
            InputType.TEMPORAL_AVERAGE_TYPE, temporal_average_type)

        return input_data

    def _get_percentile_ids(self, cube, sampling_percentile):
        """
        Get a list of sample ids from the cube that represent the
        sampling_percentile values + and - 10.
        """
        samples = []
        for sample_slice in cube.slices_over('sample'):
            sample_id = int(sample_slice.coord('sample').points[0])
            samples.append((sample_slice.data, sample_id))

        samples.sort()
        sample_count = len(samples)

        # Work out which indices must be used to subset the data for a range of
        # percentages
        low_index = (sampling_percentile - 10) * sample_count / 100
        high_index = (sampling_percentile + 10) * sample_count / 100

        sample_ids = [i[1] for i in samples[low_index:high_index]]
        return sample_ids

    def _get_random_ids(self, cube, random_sample_count,
                        random_seed_value=False):
        """
        Returns a list of randomly sampled sample ids from the cube sent
        in. The number of variants returned is of length
        random_sample_count and this may include repeats!

        If random_seed_value is not False, then it is an integer and we use
        it to set the numpy random seed which means the same arguments will
        always produce the same results.

        @param cube(an iris cube): a cube containing the sample data
        @param random_sample_count(int): the count of sample ids to produce
        @param random_seed_value(int): used to set the numpy random seed,
            may be False

        @return a list of sample ids
        """
        if random_seed_value is not False:
            numpy.random.seed(random_seed_value)

        num_of_samples = len(cube.coord('sample').points)
        ids = [i for i in numpy.random.randint(
            0, num_of_samples, random_sample_count)]
        ids.sort()
        return ids

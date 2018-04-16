import logging
import numpy

import iris

from ukcp_dp.constants import InputType

log = logging.getLogger(__name__)


class SamplingProcessor(object):
    """
    Extract sample data based on user selection criteria.
    """

    def __init__(self, cube_list, input_data):
        """
        Initialise the SamplingProcessor.

        @param cube_list(CubeList) an iris cube list
        @param input_data (InputData) an object containing user defined values
        """
        self.input_data = input_data
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

        # we are only using the first cube
        cube = cube_list[0]

        if self.input_data.get_value(InputType.SAMPLING_METHOD) == 'id':
            selected_cube = self._sample_cubes_by_id(cube)
        elif self.input_data.get_value(InputType.SAMPLING_METHOD) == 'random':
            selected_cube = self._sample_cubes_random(cube)
        elif self.input_data.get_value(InputType.SAMPLING_METHOD) == 'subset':
            selected_cube = self._sample_cubes_by_subset(cube)
        else:  # self.input_data.get_value(InputType.SAMPLING_METHOD) == 'all':
            selected_cube = self._sample_cubes_all(cube)

        # we need to return a cube list
        selected_cubes = iris.cube.CubeList()
        selected_cubes.append(selected_cube)
        return selected_cubes

    def _sample_cubes_all(self, cube):
        log.debug('_sample_cubes_all')
        return cube

    def _sample_cubes_by_id(self, cube):
        """
        Get a cube that contains the samples listed in SAMPLING_ID.
        """
        log.debug('_sample_cubes_by_id')
        constraint = iris.Constraint(sample=self.input_data.get_value(
            InputType.SAMPLING_ID))
        cube = cube.extract(constraint)
        return cube

    def _sample_cubes_random(self, cube):
        """
        Get a random selection of samples, the numer of samples is
        RANDOM_SAMPLING_COUNT.
        """
        log.debug('_sample_cubes_random')
        random_sample_count = self.input_data.get_value(
            InputType.RANDOM_SAMPLING_COUNT)

        random_ids = self._get_random_ids(cube, random_sample_count, False)
        constraint = iris.Constraint(sample=random_ids)
        cube = cube.extract(constraint)
        return cube

    def _sample_cubes_by_subset(self, cube):
        log.debug('_sample_cubes_by_subset')
        #  TODO
        constraint = iris.Constraint(sample=[1, 3, 5])
        cube = cube.extract(constraint)
        return cube

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

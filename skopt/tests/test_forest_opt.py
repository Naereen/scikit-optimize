from functools import partial

import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.testing import assert_less
from sklearn.utils.testing import assert_raise_message

from skopt import gbrt_minimize
from skopt import forest_minimize
from skopt.benchmarks import bench1
from skopt.benchmarks import bench2
from skopt.benchmarks import bench3
from skopt.benchmarks import bench4
from skopt.benchmarks import branin
from skopt.benchmarks import hart6


MINIMIZERS = [("et", partial(forest_minimize, base_estimator='et')),
              ("rf", partial(forest_minimize, base_estimator='rf')),
              ("gbrt", gbrt_minimize)]


def test_forest_minimize_api():
    # invalid string value
    assert_raise_message(ValueError,
                         "Valid values for the base_estimator parameter",
                         forest_minimize, lambda x: 0., [],
                         base_estimator='abc')

    # not a string nor a regressor
    assert_raise_message(ValueError,
                         "The base_estimator parameter has to either",
                         forest_minimize, lambda x: 0., [],
                         base_estimator=42)

    assert_raise_message(ValueError,
                         "The base_estimator parameter has to either",
                         forest_minimize, lambda x: 0., [],
                         base_estimator=DecisionTreeClassifier())


def check_minimize(minimizer, func, y_opt, dimensions, margin,
                        n_calls, n_random_starts=10, x0=None):
    for n in range(3):
        r = minimizer(
            func, dimensions, n_calls=n_calls, random_state=n,
            n_random_starts=n_random_starts, x0=x0)
        assert_less(r.fun, y_opt + margin)

def test_tree_based_minimize():
    rng = np.random.RandomState(0)
    for name, minimizer in MINIMIZERS:
        yield (check_minimize, minimizer, bench1, 0.,
               [(-2.0, 2.0)], 0.05, 25, 5)

        # This benchmark contains 2 different functions
        # when x < 0 and otherwise.
        # Hence sample uniformly from [-6, 0] and
        # [0, 6] and provide a warm-start.
        X1 = (-6 + 6 * rng.rand(5, 1)).tolist()
        X2 = (6 * rng.rand(5, 1)).tolist()
        X0 = X1 + X2
        yield (check_minimize, minimizer, bench2, -5,
               [(-6.0, 6.0)], 0.05, 100, 0, X0)

        yield (check_minimize, minimizer, bench3, -0.9,
               [(-2.0, 2.0)], 0.05, 25)
        yield (check_minimize, minimizer, bench4, 0.0,
               [("-2", "-1", "0", "1", "2")], 0.05, 10)
        yield (check_minimize, minimizer, hart6, -3.32,
               np.tile((0.0, 1.0), (6, 1)), 1.0, 50)

        if name == "et":
            yield (check_minimize, minimizer, branin, 0.39,
                   [(-5.0, 10.0), (0.0, 15.0)], 0.15, 125)
        else:
            yield (check_minimize, minimizer, branin, 0.39,
                   [(-5.0, 10.0), (0.0, 15.0)], 0.15, 200)

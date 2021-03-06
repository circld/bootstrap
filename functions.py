#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools as it
import numpy as np
import pandas as pd


def binomial(n, r):
    """ Binomial coefficient, nCr, aka the "choose" function
        n! / (r! * (n - r)!)
    """
    p = 1
    for i in xrange(1, min(r, n - r) + 1):
        p *= n
        p //= i
        n -= 1
    return p


def estimate(data_gen, estimators):
    """
    For every statistic in `estimators`, that statistic will be calculated
    for every sample in `data_gen`. In order to support variable number of
    estimators, for each estimator an itertools.tee object is created.
    Returns a dictionary of the form
        statistic: sampling distribution of the statistic
    Args:
        data_gen (PyGenObject): generator of samples (usually np.array)
        estimators (iterable of callables): the functions of the data to calc
    Returns:
        (dict): keys = names of estimators; values = resulting arrays of calc
    """
    tees = it.tee(iterable=data_gen, n=len(estimators) + 1)
    # 1 more than specified is created to get the length of `data_gen`; i.e. #
    # of samples in `data_gen`
    len_gen, sample_gens = tees[0], tees[1:]
    del tees
    num_samples = sum(1 for _ in len_gen)
    estimators_and_sample_generators = it.izip(estimators, sample_gens)
    # izip object of (callable, tee object)
    # TODO: look into imap with a lambda here
    estimators_and_distributions = ((estimator.__name__,
                                     it.imap(estimator, sample_gen))
                                    for estimator, sample_gen in
                                    estimators_and_sample_generators)
    # generator of tuples of (estimator_name, estimator.__call__(sample_gens))
    return {estimator: np.fromiter(sampling_dist_el, dtype=float,
                                   count=num_samples)
            for estimator, sampling_dist_el in estimators_and_distributions}


def resample(data, B):
    """
    Return `B` bootstrap samples of `data` as a generator. The motivation for
    this is that it may be desirable to calculate several statistics of the
    data; returning as a generator lends itself to itertools.tee.
    """
    to_be_sampled = data.ravel()
    for _ in xrange(0, B):
        yield np.random.choice(a=to_be_sampled,
                               size=data.shape[0],
                               replace=True)

#!/usr/bin/env python

"""Segment recordings."""

import logging
import pkg_resources
import os
import pickle
import json

# hwrt modules
from . import segmentation as se

nn = None
stroke_segmented_classifier = None
single_stroke_clf = None
single_clf = None


def load_nn_classifier():
    """Load nn segmentation classifier.
    """
    model_path = pkg_resources.resource_filename('hwrt', 'misc/')
    nn_pickled_filename = os.path.join(model_path,
                                       "is_one_symbol_classifier.pickle")
    logging.info("Model for segmentation classifier: %s", nn_pickled_filename)

    if os.path.isfile(nn_pickled_filename):
        with open(nn_pickled_filename, 'rb') as handle:
            try:
                get_output = pickle.load(handle)
            except ImportError as e:
                logging.error("Import error in load_nn_classifier()")
                logging.error(e)
                return None
    else:
        logging.error('"is_one_symbol_classifier" not found.')
        return None
    return get_output


def segment_recording(pointlist):
    """
    Parameters
    ----------
    pointlist : json-formatted string

    Returns
    -------
    List of tuples :
        The first element of the tuple is the segmentation, the second one the
        probability

    Examples
    --------
    >>> segment_recording([[{'x': 0, 'y': 0, 'time': 0}],
    ...  [{'x': 42, 'y': 42, 'time': 12}]])
    [([[0], [1]], 0.75), ([[0, 1]], 0.24)]
    """
    global nn, stroke_segmented_classifier, single_stroke_clf, single_clf
    assert isinstance(pointlist, basestring), \
        ("Expected string, but was %s" % type(pointlist))
    try:
        if nn is None or stroke_segmented_classifier is None:
            nn = load_nn_classifier()
            stroke_segmented_classifier = lambda X: nn(X)[0][1]
        if single_clf is None:
            single_clf = se.single_classifier()
        pointlist = json.loads(pointlist)
        seg_predict = se.get_segmentation(pointlist,
                                          single_clf,
                                          single_stroke_clf,
                                          stroke_segmented_classifier)
    except:
        logging.warning("Couldn't load segmenters. "
                        "Fallback to no segmentation.")
        seg_predict = [([[i for i in range(len(pointlist))]], 1.0)]
    return seg_predict

# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2017 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

    Compatible with QGIS 2.18 and below
    Test identify large geometry changes qgis user processing script,
    using test data of two versions of roads layers.

 ******************************************************************************/
"""

import sys
import os
import unittest
import processing
from shutil import copy
from qgis.utils import plugins, QGis
from qgis.core import QgsVectorLayer
from processing import runalg
from processing.core.Processing import Processing
from processing.script.ScriptUtils import ScriptUtils

# # set global variables
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

test_dir = os.path.join(__location__, 'testdata')
file_path = os.path.abspath(os.path.join(
    __location__, '..', 'identify_large_geometry_changes.py'))

# Set up test layers
original_layer = QgsVectorLayer(
    r"{}/original_roads.shp".format(test_dir),
    'original_roads',
    'ogr')
if not original_layer.isValid():
    raise ImportError('Input Layer failed to load!')

updated_layer = QgsVectorLayer(
    r"{}/updated_roads.shp".format(test_dir),
    'updated_roads',
    'ogr')
if not updated_layer.isValid():
    raise ImportError('Updated Layer failed to load!')

# QGIS 2.14 has ScriptUtils.scriptsFolder()
if QGis.QGIS_VERSION_INT < 21800:
    copy(file_path, ScriptUtils.scriptsFolder())
# QGIS 2.18 has ScriptUtils.scriptsFolders()
elif QGis.QGIS_VERSION_INT >= 21800:
    copy(file_path, ScriptUtils.scriptsFolders()[0])

# Refresh Processing Toolbox plugin
plugins['processing'].toolbox.updateProvider('script')
Processing.initialize()

# QGIS 2.14 has Processing.updateAlgsList()
if QGis.QGIS_VERSION_INT < 21800:
    Processing.updateAlgsList()
# QGIS 2.18 has algList.reloadProvider(('script')
elif QGis.QGIS_VERSION_INT >= 21800:
    from processing.core.alglist import algList
    algList.reloadProvider('script')


class TestProcessingScript(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        cls.algorithm_not_found = False
        try:
            result = runalg(
                "script:identifylargegeometrychanges",
                original_layer,
                updated_layer,
                "t50_fid",
                "t50_fid",
                25,
                50,
                None,
                None
            )

            cls.original_output = processing.getObject(result['QA_Large_Changes_Original'])
            cls.updated_output = processing.getObject(result['QA_Large_Changes_Updated'])

        except TypeError:
            cls.algorithm_not_found = True

    def setUp(self):
        """Runs before every test"""
        if self.algorithm_not_found:
            self.fail("Could not load geoalgorithm script")

    def test_count_features_original_layer(self):
        """Does the output layer contain the expected number of features"""
        self.assertEqual(self.original_output.featureCount(), 4)

    def test_count_features_updated_layer(self):
        """Does the output layer contain the expected number of features"""
        self.assertEqual(self.updated_output.featureCount(), 4)

    def test_fid_original_layer(self):
        """Does the output layer contain the expected features"""
        valid = [3, 5, 6, 17]
        error = False
        feats = self.original_output.getFeatures()
        for feat in feats:
            if feat['t50_fid'] not in valid:
                error = True
            else:
                valid.remove(feat['t50_fid'])
        self.assertEqual(error, False)

    def test_fid_updated_layer(self):
        """Does the output layer contain the expected features"""
        valid = [3, 5, 6, 17]
        error = False
        feats = self.updated_output.getFeatures()
        for feat in feats:
            if feat['t50_fid'] not in valid:
                error = True
            else:
                valid.remove(feat['t50_fid'])
        self.assertEqual(error, False)

    def test_count_part_original_layer(self):
        """Does the output features match expected geometry type"""
        error = False
        feats = self.original_output.getFeatures()
        for feat in feats:
            count_part = len(feat.geometry().asMultiPolyline())
            if feat['t50_fid'] == 3:
                if count_part != 0:  # 0 because it's single polyline
                    error = True
            if feat['t50_fid'] == 5:
                if count_part != 2:
                    error = True
            if feat['t50_fid'] == 6:
                if count_part != 4:
                    error = True
            if feat['t50_fid'] == 17:
                if count_part != 0:
                    error = True
        self.assertEqual(error, False)

    def test_count_part_updated_layer(self):
        """Does the output features match expected geometry type"""
        error = False
        feats = self.updated_output.getFeatures()
        for feat in feats:
            count_part = len(feat.geometry().asMultiPolyline())
            if feat['t50_fid'] == 3:
                if count_part != 0:  # 0 because it's single polyline
                    error = True
            if feat['t50_fid'] == 5:
                if count_part != 2:
                    error = True
            if feat['t50_fid'] == 6:
                if count_part != 5:
                    error = True
            if feat['t50_fid'] == 17:
                if count_part != 0:
                    error = True
        self.assertEqual(error, False)


def suite():
    """
    A test suite is a collection of test cases, test suites, or both.
    It is used to aggregate tests that should be executed together.
    """
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestProcessingScript, 'test'))
    return suite


def run_tests():
    """
    Implements a TextTestRunner, which is a basic test runner implementation
    that prints results on standard error.
    """
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())

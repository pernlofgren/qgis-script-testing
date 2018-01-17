## Testing QGIS Scripts


[![LICENSE](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/pernlofgren/qgis-script-testing/blob/master/LICENSE) [![](https://travis-ci.org/pernlofgren/qgis-script-testing.svg?branch=master)](https://travis-ci.org/pernlofgren/qgis-script-testing)

This repo has been set up as a resource for automated testing of QGIS processing script tools. The goal is to simply demonstrate ways of incorporating testing into qgis scripting workflows.

### Contents

- `script_tools/identify_large_geometry_changes.py`: a geoprocessing script identifying changes between two versions of data.
- `script_tools/tests/test_script.py`: a script that runs the above geoprocessing script tool and tests the output.
- `script_tools/tests/testdata`:  two shapefiles to test on

In this example we used the `unittest` module to write our tests. The basic structure of the test case is to run the script tool and query the output on specific criteria.


### Local Testing

Run script in QGIS Python Consule, requires hard coding certain file paths and calling run_tests() method.

There is also a handy plugin called [Script Assistant](https://github.com/linz/qgis-scriptassistant-plugin), that allows developers to reload and run tests from a  configured test folder. With this plugin, a single test or a collection of tests can be run and the results appear in the QGIS Python consule.


### Travis Continuous Integration

There are some great tools out there for continuous integration processes, allowing us to integrate new code regularly and locate problems easier. Thanks to [Boundless QGIS Testing Environment](https://boundlessgeo.com/2016/07/qgis-continuous-integration-testing-environment-for-python-plugins/), testing inside a real QGIS session via a docker container is now possible! Another benefit of this type of automated testing, is the ability to run tests on multiple platforms and QGIS versions.

The **.travis.yml** file in this repo customizes the steps for the testing environment and tells Travis what to do. All thats needed to trigger a new build is adding .travis.yml file, commit and push to the remote repo. In this example, builds only get triggered on master branch.


Although not shown here, the docker tests can also be run on your local machine. This can be done through installing docker and pulling the qgis-testing-environment docker image. This is well documented in the qgis-testing-environment-docker [github repo](https://github.com/boundlessgeo/qgis-testing-environment-docker).


### Resources

- [Travis CI docs](https://docs.travis-ci.com/)
- [Unittest docs](https://docs.python.org/2/library/unittest.html)
- [qgis-plugin-testing](https://github.com/pernlofgren/qgis-plugin-testing): plugin ui/workflow testing

### Things to note

- The `.travis.yml` file is read from the root of the repository
- Travis only runs builds on the commits you push after you’ve enabled the repository in Travis CI.
- `__file__` does not work in the QGIS Python consule.

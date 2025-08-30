"""Plugin that implements probtest on top of pytest.

Given a specification of the program under test, automatically computes
the number to run the tests. According to this number, creates a number
of identical copies (subtests) of each test with dependencies between the 
subtests using the pytest-dependency library.

Author: Katrine Christensen <katch@itu.dk>
"""

import pytest
import re
import sys
from pathlib import Path
sys.path.insert(1, './src')
import ccp_upper_bound
from pytest import Config

def pytest_addoption(parser):
    """Adds pytest options to pytest. Enables us to write for example
    pytest --probtest --p 0.5,0.5 which reads the provided values (the 
    specification) to run probtest given these."""

    group = parser.getgroup('probtest')

    group.addoption(
        "--probtest", 
        action="store_true",
        help="Enable to test probabilistic programs")
    
    group.addoption(
        "--epsilon", 
        action="store", 
        default=0.05, 
        type=float,
        help="Set coverage guarantee of 1-epsilon (optional). Default is 0.05")

    group.addoption(
        "--p", 
        action="store", 
        type=str,
        help="Specify distribution of outcomes as floats seperated by commas, e.g. 0.5,0.5")
    
    group.addoption(
        "--minp", 
        action="store", 
        type=float,
        help="Specify the probability of the least likely outcome as float. N must also be specified")
    
    group.addoption(
        "--N", 
        action="store", 
        type=int,
        help="Specify the number of outcomes")
    
    group.addoption(
        "--Pbug", 
        action="store", 
        type=float,
        help="Specify the probability of a bug occurring")

@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    """Given a specification when the --probtest flag is enabled, checks
    whether the specification is valid and, if valid, computes the number of times k
    to run each test using results from the coupon collector's problem."""

    if config.getoption('probtest'):
        global k #number of times to run each test

        # Add a marker that is later used when adding dependencies between subtests.
        # The last subtest of a number of subtests of a test (identical copies
        # of the original test) has no other tests dependent on this.
        config.addinivalue_line("markers", 
                        "last_subtest():"
                        "mark a test as the last test of a repeated test")

        # Argument error handling:
        if (not config.getoption('p')) and not config.getoption('minp') and not config.getoption('Pbug'):
            pytest.exit("Please provide a specification of the program.")

        if (config.getoption('p') and (config.getoption('minp') or config.getoption('Pbug'))) or (
            config.getoption('minp') and config.getoption('Pbug')):
            pytest.exit("Please provide either p, minp or Pbug.")

        if config.getoption('p'):
            if re.search("(\\d,)*\\d",config.option.p)==None:
                pytest.exit(
                    "Please provide p as a string of floats separated by "+
                    "commas, e.g. --p 0.1,0.9"
                )
        if config.getoption('minp') and not config.getoption('N'):
            pytest.exit(
                "Please provide the number of possible outcomes N "+
                "when providing p_min. For example: --minp 0.01 --N 10"
            )

        # Computing k:
        if config.getoption('minp') and config.getoption('N'):
            config.option.p = [config.option.minp]*config.option.N
        elif config.getoption('p'):
            # if p is provided, e.g. as --p "0.1,0.2", we save p as a list of floats
            p = []
            config.option.N=len(config.option.p.split(","))
            for s in config.option.p.split(","):
                try:
                    p += [string_to_float(s)]
                except ValueError:
                    pytest.exit("Please provide p as a vector of floats or fractions, e.g. 0.5,0.5 or 1/2,1/2.")
            config.option.p = p
        elif config.getoption('Pbug'):
            if float(config.option.Pbug)==1:
                config.option.p = [float(config.option.Pbug)]
            else:
                config.option.p = [float(config.option.Pbug),1-float(config.option.Pbug)]
            config.option.N = len(config.option.p)

        try:
            k = ccp_upper_bound.ccp(
                config.getoption('epsilon'),
                config.getoption('N'),
                config.getoption('p'))
        except ValueError as e:
            pytest.exit(e)

def string_to_float(str):
    try:
        return float(str)
    except ValueError:
        num, denom = str.split('/')
        return float(num) / float(denom)

def pytest_report_header(config):
    """Prints useful information for the test session when using probtest."""
    if config.getoption('probtest'):
        header = "\nThanks for using probtest!\n"

        approach = "Your tests are being run "+str(k)+" times.\n"

        parameters = "\nEpsilon: "+ str(config.option.epsilon) +"\n"
        if config.getoption('p'):
            # p_formatted = [ '%.4f' % p_i for p_i in config.option.p ]
            p_formatted = list(map(lambda x: round(x, ndigits=4), config.option.p))
            parameters += "p: "+ str(p_formatted) +"\n"
        if config.getoption('minp'):
            parameters += "min p: "+ str(config.option.minp) +"\n"
        if config.getoption('N'):
            parameters += "N: "+ str(config.option.N) +"\n"
        if config.getoption('Pbug'):
            parameters += "P(bug): "+ str(config.option.Pbug) +"\n"
        return header+approach+parameters

def pytest_generate_tests(metafunc):
    """Generates k copies of each test."""
    if metafunc.config.getoption('probtest'):
        metafunc.fixturenames.append('repeat')
        metafunc.parametrize('repeat', range(k),indirect=True)

def pytest_collection_modifyitems(session,config,items):
    """Modifies the tests generated in pytest_generate_tests:
    Adds dependencies (using pytest-dependency) between the subtests 
    so that if the jth subtest fails, the consecutive subtests of this type
    will be skipped."""

    if config.getoption('probtest'):
        current_main_test = ""
        previous_sub_test = ""
        previous_item=None

        i=0
        for item in items:
            if item.name.__contains__("[0]"):
                current_main_test = item.name
                item.add_marker(pytest.mark.dependency())
                if previous_item!=None: previous_item.add_marker(pytest.mark.last_subtest)
                previous_sub_test = current_main_test
                previous_item = item
            else:
                item.add_marker(pytest.mark.dependency(depends=[previous_sub_test]))
                previous_sub_test = item.name
                previous_item = item
            if i==len(items)-1:previous_item.add_marker(pytest.mark.last_subtest)
            i+=1

@pytest.hookimpl
def pytest_report_teststatus(report):
    """Modifies the reporting of the test after they have been run.
    If not in verbose, does not report tests that are skipped due to 
    dependencies, and only reports passing a test if it is the last 
    subtest of a type."""

    if report.skipped and report.keywords.__contains__('dependency'):
        return "", "", ("SKIPPED", {"yellow": True})
    if report.when=='call':
        if report.passed and report.keywords.__contains__('dependency'):
            if not report.keywords.__contains__('last_subtest'):
                return "", "", ("PASSED", {"green": True})

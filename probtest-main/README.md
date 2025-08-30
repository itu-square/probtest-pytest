# ProbTest

Probtest is a plugin for [pytest](https://docs.pytest.org/) that efficiently tests probabilistic programs by running a test repeatedly. 

To use the plugin to test a program, one must provide a specification of the program's output. Given a correct specification, the plugin guarantees coverage of the program's outcome with probability $1-\epsilon$ for an $\epsilon >0$. The default $\epsilon$ is 0.05.

## Installation

The plugin can be installed via pip:

```
pip install .
```

It requires Python 3.9+ and pytest 7 or newer. 

When the library is installed, it additionally installs the library [pytest-dependency](https://pytest-dependency.readthedocs.io/). This library enables dependencies between tests in pytest.

The plugin can be uninstalled by the command:

```
pip uninstall probtest
```

Tests of the plugin can be run by:

```
pytest
```

## Usage

To use the method, one must provide one of the following three kinds of specification of the program's output. The examples below are equivalent, so that they result in the same number of runs of each test.

```
pytest --probtest --p 0.5,0.5
pytest --probtest --minp 0.5 --N 2
pytest --probtest --Pbug 0.5
```

The result of running the tests in a test suite with two test cases are as follows:

```
======================== test session starts ========================

Thanks for using probtest!
Your tests are being run 6 times.

Epsilon: 0.05
p: [0.5, 0.5]
N: 2

collected 12 items                                                                                                                                    
test_f.py F.                                                  [100%]

====================== short test summary info ======================
FAILED test_temp.py::test_01[0] - assert 1 == 0
==================== 1 failed, 1 passed in 1.86s ====================
```

The verbosity can be increased to reveal what happens under-the-hood:

```
$ pytest --probtest --p 0.5,0.5 -v

...

test_01[0] PASSED                                                  [  8%]
test_01[1] FAILED                                                  [ 16%]
test_01[2] SKIPPED (test_01[2] depends on test_01[1])              [ 25%]
test_01[3] SKIPPED (test_01[3] depends on test_01[2])              [ 33%]
test_01[4] SKIPPED (test_01[4] depends on test_01[3])              [ 41%]
test_01[5] SKIPPED (test_01[5] depends on test_01[4])              [ 50%]
test_02[0] PASSED                                                  [ 58%]
test_02[1] PASSED                                                  [ 66%]
test_02[2] PASSED                                                  [ 75%]
test_02[3] PASSED                                                  [ 83%]
test_02[4] PASSED                                                  [ 91%]
test_02[5] PASSED                                                  [100%]

...
```

The plugin creates 6 copies of each test case and adds dependencies between them. As soon as we meet a failure in a repeated run of test, we stop and skip the rest.

To change the value of $\epsilon$ from the default 0.05, set the value using the `--epsilon` flag:

```
pytest --probtest --p 0.5,0.5 --epsilon 0.01
```

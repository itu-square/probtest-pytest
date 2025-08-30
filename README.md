# Supplementary material for article: <i>Probtest: A Method for Effective Testing of Probabilistic Programs</i>
Author: Katrine Christensen <katch@itu.dk>

This repository contains the source code for the paper <i>ProbTest: Unit Testing for Probabilistic Programs</i>.

The repository is structured into two folders: 

- <i>case_studies</i>: Includes source code and test suites for the two case studies in chapters 6 and 7, i.e., the case studies on the randomized data structure, the skip list, and on the frozen lake environment.

- <i>probtest-main</>: The implementation of the testing method _probtest_ as a pytest plugin.

In the remainder of this readme, we will describe more details about <i>case_studies</i> folders and how to run the code.

The following steps assume you have installed pytest and the probtest plugin installed.

## Case study I: The skip list

We consider two implementations of the skip list data structure: one without errors (presumably) and one with injected bugs.

To run the test suite for the error-free implementation of the skip list data structure, one can run it using probtest:

```
cd case_studies/skip_list
pytest --probtest --Pbug 0.25 --epsilon 0.05
```

To change the number of inserted nodes and skip list parameters, one must manually change these (in lines 32-34 in [test_skip_list.py](/case_studies/skip_list/tests/test_skip_list.py)).

We describe below how to perform mutation testing and inject bugs in the implementation as done in the paper.

### Mutation testing

To perform mutation testing of the skip list implementation using [mutmut](.readthedocs.io/en/latest/), one must first install mutmut:

```
pip install mutmut
```

Then the mutation testing can be run (note that it is important to change directory as shown):

```
cd case_studies/skip_list
mutmut run
```

Mutmut is set up to run pytest with [probtest](./probtest-main). The specification provided to probtest can be changed in the [setup.cfg](/case_studies/skip_list/setup.cfg) file:

```
[mutmut]
paths_to_mutate=src/
backup=False
runner=pytest --probtest --Pbug 0.25 --epsilon 0.05
tests_dir=tests/
```

Be aware that mutmut makes changes to the script when it injects mutants. If suddenly stopped, mutmut may have failed to reverse them back to the original version. For more details, see the [documentation](https://mutmut.readthedocs.io/en/latest/) of mutmut.

### Injecting bugs

To run the test suite with the injected bugs as in the paper, one must first in [test_skip_list.py](/case_studies/skip_list/tests/test_skip_list.py) import the buggy version of the skip list instead of the correct (in lines 22-23):

```
# sys.path.insert(1, './src')
sys.path.insert(1, './src_bugs')
```

Then, in the [buggy implemenetation](/case_studies/skip_list/src_bugs/skip_list.py), one can inject the 8 bugs one by one by changing the value of the variable ```bug``` in line 14:

```
global bug; bug=1
```

Finally, the test suite can be run as usual:

```
cd case_studies/skip_list
pytest skip_list --probtest --Pbug 0.25 --epsilon 0.05
```


## Case study II: Frozen lake environment

To run the experiments considered in the paper, one must run the test suite using [probtest](./probtest-main) by providing the probability of errors occurring, for example:

```
pytest case_studies/frozen_lake --probtest --Pbug 0.1
```

To change the number of episodes of training, one must change it manually in the source code (line 47 in [test_frozen_laky.py](/case_studies/frozen_lake/test_frozen_lake.py)).

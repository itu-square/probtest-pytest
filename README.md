# ProbTest - Effective testing of probabilistic programs with statistical guarantees

ProbTest is a Pytest plugin to test probabilistic programs. This testing plugin runs repeatedly the probabilistic program under test and ensures that bugs are found with high probability. The folder [probtest-main](probtest-main/) contains installation and usage instructions for the plugin.

This repository accompanies the research article <i>ProbTest: Unit Testing for Probabilistic Programs</i>; to appear at [SEFM'25](https://sefm-conference.github.io/2025/). The article describes the theoretical underpinnings of ProbTest.

This repository also contains an evaluation of ProbTest in several case studies including a randomized data structure and several reinforcement learning (RL) systems. The folder [case-studies](case-studies/) contains the source code and results of all experiments. The extended version of the article (available in ArXiV) includes the details about the test suit and injected bugs for the skip list case study and a complete table with all RL experiment results.





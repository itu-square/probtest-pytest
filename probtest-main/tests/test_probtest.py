import pytest

############## Testing input errors ##############
def test_error_handling_01(pytester):
    result = pytester.runpytest('--probtest')
    result.stdout.fnmatch_lines(['*Exit: Please provide*'])

def test_error_handling_02(pytester):
    result = pytester.runpytest('--probtest','--epsilon','0.05')
    result.stdout.fnmatch_lines(['*Exit: Please provide*'])

def test_error_handling_03(pytester):
    result = pytester.runpytest('--probtest','--p','0.5,0.6')
    result.stdout.fnmatch_lines(['*Exit: Probabilities must sum to ≤ 1*'])

def test_error_handling_04(pytester):
    result = pytester.runpytest('--probtest','--p','0.5,0.5','--Pbug','0.1')
    result.stdout.fnmatch_lines(['*Exit: Please provide either*'])

def test_error_handling_05(pytester):
    result = pytester.runpytest('--probtest','--p','0.5,0.5','--minp','0.1')
    result.stdout.fnmatch_lines(['*Exit: Please provide either*'])

def test_error_handling_06(pytester):
    result = pytester.runpytest('--probtest','--minp','0.1')
    result.stdout.fnmatch_lines(['*Exit: Please provide the number of possible outcomes N*'])

def test_error_handling_07(pytester):
    result = pytester.runpytest('--probtest','--minp','0.1','--N','11')
    result.stdout.fnmatch_lines(['*Exit: Probabilities must sum to ≤ 1*'])


############## Testing correct number of repeats ##############
def test_single_run_01(pytester):
    result = pytester.runpytest('--probtest','--p','1')
    result.stdout.fnmatch_lines(['Your tests are being run 1 times.'])

def test_single_run_02(pytester):
    result = pytester.runpytest('--probtest','--minp','1','--N','1')
    result.stdout.fnmatch_lines(['Your tests are being run 1 times.'])

def test_single_run_03(pytester):
    result = pytester.runpytest('--probtest','--Pbug','1.0')
    result.stdout.fnmatch_lines(['Your tests are being run 1 times.'])

def test_6_runs_01(pytester):
    result = pytester.runpytest('--probtest','--p','0.5,0.5')
    result.stdout.fnmatch_lines(['Your tests are being run 6 times.'])

def test_6_runs_02(pytester):
    result = pytester.runpytest('--probtest','--Pbug','0.5')
    result.stdout.fnmatch_lines(['Your tests are being run 6 times.'])

def test_6_runs_03(pytester):
    result = pytester.runpytest('--probtest','--minp','0.5','--N','2')
    result.stdout.fnmatch_lines(['Your tests are being run 6 times.'])

def test_29_runs_01(pytester):
    result = pytester.runpytest('--probtest','--p','0.1,0.9')
    result.stdout.fnmatch_lines(['Your tests are being run 29 times.'])

def test_29_runs_02(pytester):
    result = pytester.runpytest('--probtest','--Pbug','0.1')
    result.stdout.fnmatch_lines(['Your tests are being run 29 times.'])

##############  ##############
def test_01(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 0

        def test_a_f1(): 
            assert f()==0

        def test_a_f2(): 
            assert f()==1
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5')
    result.assert_outcomes(passed=1,failed=1)

def test_01(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 0

        def test_a_f1(): 
            assert f()==0

        def test_a_f2(): 
            assert f()!=1
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5')
    result.assert_outcomes(passed=2)

def test_verbose_01_pass(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 1

        def test_f(): 
            assert f()==1
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5','-v')
    result.stdout.fnmatch_lines([
        '*::test_f[[]0[]] PASSED*', 
        '*::test_f[[]1[]] PASSED*', 
        '*::test_f[[]2[]] PASSED*', 
        '*::test_f[[]3[]] PASSED*', 
        '*::test_f[[]4[]] PASSED*', 
        '*::test_f[[]5[]] PASSED*', 
        '*1 passed*',
    ])

def test_verbose_02_fail(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 1

        def test_f(): 
            assert f()!=1
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5','-v')
    result.stdout.fnmatch_lines([
        '*::test_f[[]0[]] FAILED*', 
        '*::test_f[[]1[]] SKIPPED*', 
        '*::test_f[[]2[]] SKIPPED*', 
        '*::test_f[[]3[]] SKIPPED*', 
        '*::test_f[[]4[]] SKIPPED*', 
        '*::test_f[[]5[]] SKIPPED*', 
        '*1 failed*',
    ])

def test_verbose_03_multiple_tests(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 1

        def test_f_01(): 
            assert f()==1

        def test_f_02():
            assert f()!=2
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5','-v')
    result.stdout.fnmatch_lines([
        '*::test_f_01[[]0[]] PASSED*', 
        '*::test_f_01[[]1[]] PASSED*', 
        '*::test_f_01[[]2[]] PASSED*', 
        '*::test_f_01[[]3[]] PASSED*', 
        '*::test_f_01[[]4[]] PASSED*', 
        '*::test_f_01[[]5[]] PASSED*', 
        '*::test_f_02[[]0[]] PASSED*', 
        '*::test_f_02[[]1[]] PASSED*', 
        '*::test_f_02[[]2[]] PASSED*', 
        '*::test_f_02[[]3[]] PASSED*', 
        '*::test_f_02[[]4[]] PASSED*', 
        '*::test_f_02[[]5[]] PASSED*', 
        '*2 passed*',
    ])

def test_verbose_03_multiple_tests(pytester):
    pytester.makepyfile(
        """
        import pytest

        def f(): return 1

        def test_f_01(): 
            assert f()==1

        def test_f_02():
            assert f()==2
    """)

    result = pytester.runpytest('--probtest','--p','0.5,0.5','-v')
    result.stdout.fnmatch_lines([
        '*::test_f_01[[]0[]] PASSED*', 
        '*::test_f_01[[]1[]] PASSED*', 
        '*::test_f_01[[]2[]] PASSED*', 
        '*::test_f_01[[]3[]] PASSED*', 
        '*::test_f_01[[]4[]] PASSED*', 
        '*::test_f_01[[]5[]] PASSED*', 
        '*::test_f_02[[]0[]] FAILED*', 
        '*::test_f_02[[]1[]] SKIPPED*', 
        '*::test_f_02[[]2[]] SKIPPED*', 
        '*::test_f_02[[]3[]] SKIPPED*', 
        '*::test_f_02[[]4[]] SKIPPED*', 
        '*::test_f_02[[]5[]] SKIPPED*', 
        '*1 failed, 1 passed*',
    ])
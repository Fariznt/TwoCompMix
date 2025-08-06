from TwoCompMix.api import core, fit_glm

def test_testing():
    assert 2*2 == 4

def test_core_exports_fit_glm():
    assert hasattr(core, "fit_glm"), \
        f"Available functions: {[n for n in dir(core) if not n.startswith('_')]}"

def test_fit_glm():
    results = fit_glm(
        formulas = "y ~ X1 + X2",
        p_family = "linear",
        data = "random",
        iterations = 10,
        warmup_iterations = 5,
        chains = 1, 
        seed = 123,
    )
    print(results)




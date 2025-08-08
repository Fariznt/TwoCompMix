from TwoCompMix.api import core, fit_glm
import pandas as pd

# Basic smoke tests to check types being converted correctly for wrapper

def test_fit_glm():
    results = fit_glm(
        formulas = "y ~ X1 + X2",
        p_family = "linear",
        data = "random",
        iterations = 10,
        warmup_iterations = 5,
        chains = 1, 
        seed = 123,
        diagnostics = True
    )

def test_fit_glm_basic_prior():
    results = fit_glm(
        formulas = "y ~ X1 + X2",
        p_family = "linear",
        data = "random",
        priors = {
            'beta1_sigma': pd.DataFrame([[2, 1], [1, 2]]), # Square, symmetric matrix
            'beta1_loc': (7, 8),
            'beta1': 'multi_normal(beta1_loc, beta1_sigma)',
            'mu1': 'normal(0,5)',
            'mu2_loc': 0,
            'mu2_scale': 6,
            'mu2': 'normal(mu2_loc, mu2_scale)'
        },
        iterations = 10,
        warmup_iterations = 5,
        chains = 1, 
        seed = 123,
        diagnostics = True
    )





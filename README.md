**A thin python wrapper around R package LinksMixtureModeling**

TwoCompMix exposes the core functionality of the original [LinksMixtureModeling](https://github.com/Fariznt/Links-Mixture-Modeling) package written in R and stan via a Pythonic API. Refer to the original package for detailed documentation---function and argument names are identical. 

This package is currently under development and not available on PyPI. To use, see the Development/Contributing section.

---

## Table of Contents

1. [Installation](#installation)  
2. [Usage](#usage)  
3. [Development/Contributing](#development--contributing)  
4. [License](#license)

---

## Installation

This package is currently under development and not available on PyPI. To use, see the Development/Contributing section.

## Usage

This package exposes fit_glm() and fit_survival_glm() of the original package. The functionality is equivalent, but adapted for python types.
Named lists are now dictionaries, vectors are python sequences (ex. tuples), and matrices and R dataframes are Pandas dataframes.

```python
def fit_glm(formulas, 
            p_family: str, 
            data, 
            priors: dict = None, 
            iterations: int = 10000, 
            warmup_iterations: int = 1000,
            chains: int = 2,
            seed: int = None,
            diagnostics: bool = False):
    """
    Fits a two-component Bayesian mixture model and returns processed results.

    Parameters
    ----------
    formula: str or list
        Either a model formula in format 'response ~ predictor_1 + predictor_2' or list of such formula strings for jointly modeling responses.
    p_family: str
        Distribution family ("linear", "logistic", "poisson", or "gamma")
    data: pandas.Dataframe or str
        A Pandas dataframe where each column name represents a response or predictor, and each row is an observation. 
        Alternatively, input the str "random" if you want synthetic data generated for you (used for testing).
    priors: dict or None
        A dictionary, where keys are hyperparameter names or prior parameter names (str), and values define the corresponding values. Values can be 
        ints, Pandas dataframes, tuples, or other python sequences for hyperparameter values, and strings for prior definition (eg. 'normal(0,5)' 
        or multi_normal(beta1_loc, beta1_sigma) where hyperparameters beta1_loc and beta1_sigma are defined in the dictionary).
        If None, weakly-informative defaults are triggered. Undefined prior parameter names in the dictionary also take on default values.
        See documentation for example(s).
    iterations: int 
        Total number of MCMC iterations
    warmup_iterations: int 
        Number of burn-in iterations
    chains: int 
        Number of MCMC chains
    seed: int or None 
        Seed integer, or None for randomly generated seed
    diagnostics: bool
        If True, returns original results in a list that also contains compile/sampling times as well as latent values from 
        which synthetic data was generated, if applicable.

    Returns
    -------
    An organized nested dictionary of processed results and summaries.~
    """
```

Examples
```python
fit = fit_glm(
    formulas = "y ~ X1 + X2",
    p_family = "linear",
    data = my_pandas_dataframe,
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
    # diagnostics takes on default value, False
)

joint_fit = fit_glm(
    formulas = list("y1 ~ X1 + X2", "y2 ~ X1 + X2 + X3"), # notice multiple formulas for jointly modeling responses
    p_family = "poisson",
    data = "random", # "random" triggered synthetic data generation
    # priors, iterations, warmup_iterations, and chains are taking on default values here
    diagnostics = True # Triggers returning of sampling time, compile time, and latent values form which synthetic data was generated
)

# These objects contain nested dictionaries of information, including parameter summaries and mixture component membership probabilities.
print(fit) # prints everything
print(joint_fit['results']) # because joint_fit had diagnostics = True, we must index into results
```
[To be written --- will mostly copy paste docs from both functions. Main point of this section is to make types clear.]

## Development/Contributing

1. git clone https://github.com/yourusername/twocompmix.git
2. Move to root directory
3. pip install -e

Test suite uses pytest. Run tests with
- pytest

## License

MIT-licensed. See [LICENSE](LICENSE) for details.
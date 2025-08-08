import pandas as pd
from rpy2.robjects import pandas2ri, r, default_converter, Formula, NULL
from rpy2.robjects.vectors import StrVector, ListVector, IntVector, BoolVector, FloatVector, DataFrame
from rpy2.robjects.packages import importr
from collections.abc import Sequence
from rpy2.robjects.conversion import localconverter
from rpy2.rlike.container import NamedList

_cv = default_converter + pandas2ri.converter

# load R package
r('if (!requireNamespace("devtools", quietly=TRUE)) install.packages("devtools")')
r('library(devtools)')
# r('if (!requireNamespace("LinksMixtureModeling", quietly=TRUE)) '
#      'devtools::install_github("fariznt/Links-Mixture-Modeling")') 
r('devtools::install_github("fariznt/Links-Mixture-Modeling")')
r('library(LinksMixtureModeling)')
# Dev note: When/if this wrapper is ready for distribution, instead of loading from github, 
# consider storing the final R package as package data within this Python package, 
# or loading directly from CRAN with importr(). Wrap in if (!requireNamespace("LinksMixtureModeling", quietly=TRUE)) 
# to prevent reloading.

core = importr("LinksMixtureModeling")

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

    # Convert from python types to R
    r_formulas = _convert_formulas(formulas)
    r_data = _convert_data(data)
    r_priors = _convert_priors(priors)
    r_seed = _convert_seed(seed)
    with localconverter(_cv):
        r_p_family = StrVector([p_family]) # string to string converstion is automatic
        r_iterations = IntVector([iterations])
        r_warmup_iterations = IntVector([warmup_iterations])
        r_chains = IntVector([chains])
        r_diagnostics = BoolVector([diagnostics])

    # call core R package
    output = core.fit_glm(
        formulas = r_formulas,
        p_family = r_p_family,
        data = r_data,
        priors = r_priors,
        iterations = r_iterations,
        warmup_iterations = r_warmup_iterations,
        chains = r_chains,
        seed = r_seed,
        diagnostics = r_diagnostics
    )
    print(output)
    return pythonify(output) # convert output to python types and return


def fit_survival_model():
    """
    TODO
    """
    
def _convert_formulas(formulas):
    """
    Takes Python input and converts to R list of formulas
    """
    with localconverter(_cv):
        if isinstance(formulas, (list, tuple)):
            return [Formula(f) for f in formulas]
        elif isinstance(formulas, str):
            return Formula(formulas)


def _convert_data(data):
    """
    Takes Python input (String or Pandas dataframe) and converts to R dataframe
    """
    with localconverter(_cv):
        if isinstance(data, pd.DataFrame): 
            return pandas2ri.py2rpy(data)
        elif isinstance(data, str) and data == "random":
            return StrVector([data])
        else:
            raise TypeError("Invalid argument for 'data': Pass Pandas dataframe or string 'random'")
    
def _convert_priors(priors):
    """
    Iterates over a list of prior definitions in python types and converts to R types to call fit functions
    """
    if priors == None: 
        return NULL 
    else:
        r_priors_dict = dict()
        
        for k, v in priors.items():
            if isinstance(v, str): # prior passed as python string
                r_priors_dict[k] = StrVector([v])
            elif isinstance(v, int): # scalar passed as python int
                r_priors_dict[k] = FloatVector([v])
            elif isinstance(v, Sequence): # vector passed as python sequence (tuple, list, etc.)
                r_priors_dict[k] = FloatVector(tuple(v))
            elif isinstance(v, pd.Series): # vector passed as pandas series
                r_priors_dict[k] = FloatVector(v.astype(float).tolist())
            elif isinstance(v, pd.DataFrame): # matrix passed as pandas dataframe
                with localconverter(_cv):
                    R_v = _cv.py2rpy(v)
                r_priors_dict[k] = r['as.matrix'](R_v)
            else: # could add more type friendliness here
                raise TypeError(f'Invalid value for element of list "priors".\nKey of invalid value: {str(k)}\nValue: {str(v)}')

        return ListVector(r_priors_dict)
    
def _convert_seed(seed):
    if seed == None:
        return StrVector(["random"])
    else:
        return IntVector([seed])

def pythonify(obj):
    """
    Recursively traverses list of named or unnamed lists and R objects and converts them into native python types.
    """
    with localconverter(_cv):
        if isinstance(obj, ListVector):
            return {var_name: pythonify(var) for var_name, var in obj.items()}
        elif isinstance(obj, NamedList):
            list_keys = [_cv.rpy2py(name) for name in obj.names()]
            list_values = [pythonify(value) for value in obj]
            return dict(zip(list_keys, list_values))
        else:
            return _cv.rpy2py(obj)
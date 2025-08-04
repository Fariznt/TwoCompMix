import pandas as pd
from rpy2.robjects import pandas2ri, r, Formula, default_converter
from rpy2.robjects.vectors import StrVector, ListVector, IntVector, BoolVector, FloatVector, DataFrame
from rpy2.robjects.packages import importr
from collections.abc import Sequence
from rpy2.robjects.conversion import localconverter

pandas2ri.activate() # active R-pandas conversions

# load R package
r('if (!requireNamespace("devtools", quietly=TRUE)) install.packages("devtools")')
r('library(devtools)')
r('if (!requireNamespace("LinksMixtureModeling", quietly=TRUE)) '
     'devtools::install_github("fariznt/Links-Mixture-Modeling")')
r('library(LinksMixtureModeling)')
# Dev note: When/if this wrapper is ready for distribution, instead of loading from github, 
# consider storing the final R package as package data within this Python package, 
# or loading directly from CRAN with importr()

core = importr("LinksMixtureModeling")

def fit_glm(formulas, 
            p_family: str, 
            data, 
            priors: dict = None, 
            iterations: int = 10000, 
            warmup_iterations: int = 1000,
            chains: int = 2,
            seed: int = 123,
            diagnostics = False):
    """
    TODO
    """
    r_p_family = StrVector([p_family]) # string to string converstion is automatic
    r_formulas = _convert_formulas(formulas)
    r_data = _convert_data(data)
    r_priors = _convert_priors(priors)
    r_iterations = IntVector([iterations])
    r_warmup_iterations = IntVector([warmup_iterations])
    r_chains = IntVector([chains])
    r_seed = IntVector([seed])
    r_diagnostics = BoolVector([diagnostics])

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

    return pythonify(output)


def fit_survival_model():
    # dont forget to check a list is not being passed to survival_model rn
    pass

def _convert_formulas(formulas):
    """
    Takes Python input and converts to R list of formulas
    """
    if isinstance(formulas, (list, tuple)):
        return [Formula(f) for f in formulas]
    elif isinstance(formulas, str):
        return Formula(formulas)


def _convert_data(data):
    """
    Takes Python input (String or Pandas dataframe) and converts to R dataframe
    """
    if isinstance(data, pd.DataFrame): 
        return pandas2ri.py2rpy(data)
    elif isinstance(data, str) and data == "random":
        return StrVector([data])
    else:
        raise TypeError("Invalid argument for 'data': Pass Pandas dataframe or string 'random'")
    
def _convert_priors(priors):
    """
    TODO
    """
    r_priors_dict = dict()
    for k, v in priors.items():
        if isinstance(v, str):
            r_priors_dict[k] = StrVector([v])
        elif isinstance(v, int):
            r_priors_dict[k] = FloatVector([v])
        elif isinstance(v, Sequence): # vector passed as python sequence (tuple, list, etc.)
            r_priors_dict[k] = FloatVector(tuple(v))
        elif isinstance(v, pd.Series): # vector passed as pandas series
            r_priors_dict[k] = FloatVector(v.astype(float).tolist())
        elif isinstance(v, pd.DataFrame): # matrix passed as pandas dataframe
            r_priors_dict[k] = r['as.matrix'](pandas2ri.py2rpy(v))
        else: # could add more type friendliness here
            raise TypeError(f'Invalid value for element of list "priors".\nKey of invalid value: {str(k)}\nValue: {str(v)}')

    return ListVector(r_priors_dict)
    
def pythonify(obj):
    """
    If given an R dataframe, returns pandas dataframe. If given a nested R list of R lists and dataframes, recursively traverses 
    the object structure to generate and return a nested python list of lists and Pandas dataframes.
    """
    if isinstance(obj, DataFrame):
        return pandas2ri.rpy2py(obj)
    elif isinstance(obj, ListVector):
        return {key: pythonify(value) for key, value in obj.items()}
    else:
        raise TypeError(f'Invalid type returned from core LinksMixtureModeling package.')
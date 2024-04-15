__use_cupy__ = False

if __use_cupy__:
    import cupy as np
    import cupyx.scipy as sci
else:
    import numpy as np
    import scipy as sci

from Management import *

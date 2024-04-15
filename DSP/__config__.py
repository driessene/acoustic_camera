from __config__ import  __use_cupy__

if __use_cupy__:
    import cupy as np
    import cupyx.scipy as sci
else:
    import numpy as np
    import scipy as sci

from Management import *
import logging

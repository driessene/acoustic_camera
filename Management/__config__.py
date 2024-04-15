from __config__ import  __use_cupy__

if __use_cupy__:
    import cupy as np
else:
    import numpy as np
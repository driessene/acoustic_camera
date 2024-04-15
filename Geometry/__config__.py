__use_cupy__ = False

if __use_cupy__:
    import cupy as np
else:
    import numpy as np
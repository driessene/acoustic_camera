import pandas as pd


def array_to_csv(array, path):
    df = pd.DataFrame(array)
    df.to_csv(path, header=False, index=False)

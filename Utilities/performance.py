from time import perf_counter

def measure_execution_time(func):
    def timed_execution(*args, **kwargs):
        start_timestamp = perf_counter()
        result = func(*args, **kwargs)
        end_timestamp = perf_counter()
        execution_duration = end_timestamp - start_timestamp
        print(f"Function {func.__name__} took {execution_duration:.2f} seconds to execute")
        return result
    return timed_execution
import json
import jsonschema
import random
from schema import schema
from multiprocessing import Process, Pipe
import pandas as pd
import argparse

def load_input(inp: str) -> dict:
    """The "setup" step for reading and validating input data.
    Input should be provided as JSON string following schema in schema.py 

    Args:
        inp (str): JSON data

    Returns:
        dict: Parsed input data
    """
    print("Loading JSON data...")
    data = json.loads(inp)
    validate_input(data)
    print("Input is valid")
    return data

def validate_input(inp: dict) -> None:
    """Validates

    Args:
        inp (dict): JSON converted to dict

    Raises:
        e: raised if input is not matching the schema  
    """
    try:
        jsonschema.validate(inp, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        raise e

def generate_rng_results(data: dict) -> list[dict]:
    """The "map" step, takes the input provided and returns generated results

    Args:
        data (dict): Input data, contains seed for random generator (random_seed), 
            number of workers which should perform the task (n_workers), and number of samples
            to collect (n_sims).

    Returns:
        list[dict]: A list of two generated results, first: for each worker separately, 
            second: for all workers cumulatively.
    """
    print("Assigning tasks to workers...")
    workers_occupancy = get_evenly_split_workers(data["n_sims"], data["n_workers"])
    results_workers, results_total = run_workers(workers_occupancy, data["random_seed"])
    print("Mapping finished")
    return [results_workers, results_total]

def rand_num_generator(seed: float):
    """Random number generator

    Args:
        seed (float): seed used by generator

    Yields:
        Iterator[float]: randomly generated number, from 0 to 1
    """
    random.seed(seed)
    while True:
        yield random.random()
        
def run_generator(connection, seed: float, n_sims: int):
    """Performs the simulation for a single worker and sends the results to the adult node

    Args:
        connection: Child of pipe connection for the computation process 
        seed (float): seed used by generator
        n_sims (int): number of samples to collect
    """
    gen = rand_num_generator(seed)
    
    connection.send(pd.Series([next(gen) for _ in range(n_sims)]))
    connection.close()

def get_evenly_split_workers(n_sims: int, n_workers: int) -> list[int]:
    """
    Checks if n_sims is divisible by n_workers. If n_sims % n_workers == 0,
    then each worker can handle the same amount of simulations. If not,
    number of simulations is assigned to workers for the least difference between them.
    
    Example: n_sims = 11, n_workers = 3
    amount_1 = n_sims//n_workers = 3 
    amount_2 = n_sims//n_workers + 1 = 4
    n_sims % n_workers == 2, which is the number of workers with amount_1
    the rest of the list is filled with amount_2
    therefore the resulting split is [4, 4, 3]
    
    Args:
        n_sims (int): total number of samples to collect
        n_workers (int): total number of workers
        
    Returns:
        list[int]: amount of samples to collect by each worker
    """
    if n_sims % n_workers == 0:
        worker_sims = [n_sims//n_workers for _ in range(n_workers)]
    else:
        worker_sims = []
        remainder = n_sims % n_workers
        for _ in range(remainder):
            worker_sims.append(n_sims//n_workers + 1)
        for _ in range(n_workers - remainder):
            worker_sims.append(n_sims//n_workers)
    return worker_sims
        
def run_workers(workers: list[int], seed: float) -> [pd.DataFrame, pd.DataFrame]:
    """Main process for running the computation. Creates separate processes for every worker.
    Every worker uses different seed, but for the same seed in input the results are deterministic.

    Args:
        workers (list[int]): amount of samples to collect by each worker
        seed (float): seed used by generators

    Returns:
        [pd.DataFrame, pd.DataFrame]: A list of two dataframes, 
            first: all workers' results split into separate columns named worker_{i}, 
            second: all workers' results in a single column "Total".
    """
    processes = []
    parent_connections = []
    results, results_collective = pd.DataFrame(), pd.DataFrame()
    for i, worker in enumerate(workers):
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)
        
        # increment the seed for each worker by 1, so the results are
        # deterministic, but each worker uses different seed to get different numbers
        process = Process(target=run_generator, args=(child_conn, seed+i, worker))
        processes.append(process)
    # starting, collecting and terminating processes
    for process in processes:
        process.start()
    for i, par_conn in enumerate(parent_connections):
        worker_res = par_conn.recv()
        results[f"worker_{i}"] = worker_res
        results_collective = pd.concat([results_collective, worker_res])
    for process in processes:
        process.join()
        
    results_collective.columns = ["Total"]
        
    return results, results_collective

def parse_results(data: dict, results: pd.DataFrame, results_collective: pd.DataFrame) -> str:
    """Save the results of computation into JSON summary in total and for each worker.

    Args:
        data (dict): input data, containing title of the summary and optional threshold field
        results (pd.DataFrame): all workers' results split into separate columns named worker_{i}
        results_collective (pd.DataFrame): all workers' results in a single column "Total"

    Returns:
        str: summary of calculations in JSON
    """
    outp = {"title": data["title"], "statistics": {}}
    stats = outp["statistics"]
    for res in results.columns:
        current_col = res
        stats[current_col] = reduce_col(results, current_col, data.get("threshold", 0))
        
    stats["Total"] = reduce_col(results_collective, "Total", data.get("threshold", 0))
    
    return json.dumps(stats)
        
def reduce_col(df: pd.DataFrame, colname: str, threshold: float) -> dict:
    """Generate statistics for calculations' results

    Args:
        df (pd.DataFrame): dataframe of calculations' results 
        colname (str): name of the column to generate statistics for, 
            either "worker_{i}" or "Total"
        threshold (float, optional): a limit for counting computed values 
            greater or equal to threshold.
    Returns:
        dict: statistics for given column in dataframe
    """
    stats = {}
    stats["numof_samples"] = int(df[colname].count())
    stats["numof_samples_thresh"] = int(df[df[colname]>=threshold][colname].count())
    stats["max_result"] = float(df[colname].max())
    stats["min_result"] = float(df[colname].min())
    stats["median"] = float(df[colname].median())
    stats["count_distinct"] = int(df[colname].nunique())
    stats["sum"] = float(df[colname].sum())
    
    return stats
        
def full_computation(inp: str) -> dict:
    """Performs full computation in three steps:
    1. Setup - read input data, preparation.
    2. Map - generate random numbers.
    3. Reduce - provide summary statistics.

    Args:
        inp (str): JSON data

    Returns:
        dict: summar of calulations in JSON
    """
    inp_data = load_input(inp)
    results = generate_rng_results(inp_data)
    # results[0] - results per worker
    # results[1] - results collective
    return parse_results(inp_data, results[0], results[1])
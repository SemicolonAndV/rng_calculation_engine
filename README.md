# RNG calculation engine

This engine allows to generate piles of random numbers based on the JSON input and provide summary statistics.

## Input requirements
The input should be provided as JSON string following the schema below:
```json
{
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "n_workers": {
            "type": "integer"
        },
        "random_seed": {
            "type": "number"
        },
        "n_sims": {
            "type": "integer"
        },
        "threshold": {
            "type": "number"
        }
    },
    "required": [
        "title",
        "n_workers",
        "random_seed",
        "n_sims"
    ]
}
```

## Engine specifications

The engine consists of 3 steps:  
1. Setup - read input data, preparation.
2. Map - generate random numbers.
3. Reduce - provide summary statistics.

Every step can be performed separately by using methods given below:
 - Setup:  `load_input(inp: str) -> dict`
 - Calculate: `generate_rng_results(data: dict) -> list[dict]`
 - Reduce:  `parse_results(data: dict, results: pd.DataFrame, results_collective: pd.DataFrame) -> str`

 Output of the step can be provided as an input to the following step.  
 Also, all steps can also be performed in one line by using `full_computation(input: str) -> dict`

 Engine components can be tested by running:  
 `python -m unittest test_calculator.py`
 
 More info about the steps and components can be found in the source code.

 ## Example usage

`full_computation('{"title": "mocktitle", "n_workers": 4, "random_seed": 5, "n_sims": 6, "threshold": 0}')`
 
output:
```
{
    "title": "mocktitle", 
    "statistics": {
        "worker_0": {
            "numof_samples": 2,
            "numof_samples_thresh": 2, 
            "max_result": 0.7417869892607294, 
            "min_result": 0.6229016948897019, 
            "median": 0.6823443420752157, 
            "count_distinct": 2,
            "sum": 1.3646886841504313
        }, 
        "worker_1": {
            "numof_samples": 2,
            "numof_samples_thresh": 2, 
            "max_result": 0.8219540423197268, 
            "min_result": 0.793340083761663, 
            "median": 0.8076470630406949, 
            "count_distinct": 2, 
            "sum": 1.6152941260813898
        }, 
        "worker_2": {
            "numof_samples": 1, 
            "numof_samples_thresh": 1, 
            "max_result": 0.32383276483316237, 
            "min_result": 0.32383276483316237, 
            "median": 0.32383276483316237, 
            "count_distinct": 1, 
            "sum": 0.32383276483316237
        }, 
        "worker_3": {
            "numof_samples": 1,  
            "numof_samples_thresh": 1, 
            "max_result": 0.2267058593810488, 
            "min_result": 0.2267058593810488, 
            "median": 0.2267058593810488, 
            "count_distinct": 1, 
            "sum": 0.2267058593810488
        }, 
        "Total": {
            "numof_samples": 6, 
            "numof_samples_thresh": 6, 
            "max_result": 0.8219540423197268, 
            "min_result": 0.2267058593810488, 
            "median": 0.6823443420752157, 
            "count_distinct": 6, 
            "sum": 3.5305214344460323
        }
    }
}
```


 Created by Kuba Pająk
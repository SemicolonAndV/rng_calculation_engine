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
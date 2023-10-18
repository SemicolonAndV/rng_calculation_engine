schema = {
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
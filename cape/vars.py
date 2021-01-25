JOB_TYPE_MULT = "MULTIPLICATION"
JOB_TYPE_LR = "LINEAR_REGRESSION"

JOB_TYPES = [
    JOB_TYPE_MULT,
    JOB_TYPE_LR,
]

# Mapping of pandas datatypes to json datatypes
# dtypes object -> string
# dtypes int64 -> integer
# dtypes float64 -> number
# dtypes datetime64[ns] -> datetime
# dtypes category -> any
PANDAS_TO_JSON_DATATYPES = {
    "object": "string",
    "int64": "integer",
    "float64": "number",
    "datetime64[ns]": "datetime",
    "category": "any",
}

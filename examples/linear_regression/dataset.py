from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

np.random.seed(123)


def generate_dataset(nb_days, day_frequency, states):
    nb_records = nb_days * day_frequency * len(states)

    datelist = pd.date_range(date(2020, 1, 1), periods=nb_days).tolist()
    datelist = day_frequency * datelist

    data = pd.DataFrame()
    for state in states:
        one_state = pd.DataFrame({"transaction_date": datelist, "state": state,})
        data = pd.concat([data, one_state])

    x = np.random.randint(5, 15, size=nb_records)
    y = 1 + 2 * x + np.random.randint(0, 2, size=nb_records)
    data["ms_transaction_amount"] = x.reshape(nb_records)
    data["sw_transaction_amount"] = y.reshape(nb_records)

    path = Path("data")
    path_ms = path / "ms"
    path_sw = path / "sw"

    path.mkdir(exist_ok=True)
    path_ms.mkdir(exist_ok=True)
    path_sw.mkdir(exist_ok=True)

    ms_data = data[["transaction_date", "state", "ms_transaction_amount"]]
    sw_data = data[["transaction_date", "state", "sw_transaction_amount"]]

    print(f"Save MS Dataset: {ms_data.shape}")
    ms_data.to_csv(path_ms / "ms_data.csv", index=False)
    print(f"Save sw Dataset: {sw_data.shape}")
    sw_data.to_csv(path_sw / "sw_data.csv", index=False)
    return path_ms, path_sw

def make_aggregate_csv(csv_path, prefix):
    data = pd.read_csv(csv_path / f"{prefix}_data.csv")
    vec_name = f"{prefix}_total_estimated_sales"
    agg = data.groupby(["transaction_date", "state"]) \
        .agg({f"{prefix}_transaction_amount": "sum"}) \
        .rename(columns={f"{prefix}_transaction_amount": vec_name})
    agg.to_csv(csv_path / f"{prefix}_aggregate_data.csv")
    agg.to_csv(csv_path / f"{prefix}_rawvec_aggregate_data.csv", index=False, header=False)

if __name__ == "__main__":
    states = ["CA", "NY"]
    nb_days = 100
    day_frequency = 10

    path_ms, path_sw = generate_dataset(nb_days, day_frequency, states)
    make_aggregate_csv(path_ms, "ms")
    make_aggregate_csv(path_sw, "sw")

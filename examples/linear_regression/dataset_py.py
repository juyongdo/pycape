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

    x = np.random.randint(50, 150, size=nb_records)
    y = 10 + 2 * x + np.random.randint(0, 20, size=nb_records)
    data["rh_transaction_amount"] = x.reshape(nb_records)
    data["gme_transaction_amount"] = y.reshape(nb_records)

    path = Path("data")
    path_rh = Path("data/rh")
    path_gme = Path("data/gme")

    if not path.is_dir():
        path.mkdir()
        path_rh.mkdir()
        path_gme.mkdir()

    rh_data = data[["transaction_date", "state", "rh_transaction_amount"]]
    gme_data = data[["transaction_date", "state", "gme_transaction_amount"]]

    print(f"Save RH Dataset: {rh_data.shape}")
    rh_data.to_csv(path_rh / "rh_data.csv", index=False)
    print(f"Save GME Dataset: {gme_data.shape}")
    gme_data.to_csv(path_gme / "gme_data.csv", index=False)
    return path_rh, path_gme

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

    path_rh, path_gme = generate_dataset(nb_days, day_frequency, states)
    make_aggregate_csv(path_rh, "rh")
    make_aggregate_csv(path_gme, "gme")

import pandas as pd
from random import random, randint


FAKE_HOST = "http://cape.com"
FAKE_TOKEN = "abc,123"
FAKE_COLUMNS = ["height", "age", "first_name", "dob"]

def fake_csv_dob_date_field():
    csv_data = []

    for i in range(0, 100):
        height = random()
        age = randint(0, 100)
        fname = "test" + str(i)
        dob = "199{a}-{a}-0{a}".replace("{a}", str(len(str(i))))
        csv_data.append((height, age, fname, dob))

    return pd.DataFrame(data=csv_data, columns=FAKE_COLUMNS)


def fake_dataframe():
    d = {"col1": [1, 2], "col2": [3, 4]}
    return pd.DataFrame(data=d)

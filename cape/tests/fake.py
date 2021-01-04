import pandas as pd


FAKE_HOST = "http://cape.com"
FAKE_TOKEN = "abc,123"


def fake_csv_dob_date_field():
    csv_data = []

    for i in range(0, 100):
        fname = "test" + str(i)
        lname = "test" + str(i)
        dob = "199{a}-{a}-0{a}".replace("{a}", str(len(str(i))))
        csv_data.append((fname, lname, dob))

    columns = ["first_name", "last_name", "dob"]

    return pd.DataFrame(data=csv_data, columns=columns)


def fake_dataframe():
    d = {"col1": [1, 2], "col2": [3, 4]}
    return pd.DataFrame(data=d)

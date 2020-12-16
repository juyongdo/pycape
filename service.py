import os
from cape import Cape


if __name__ == "__main__":
    c = Cape(os.environ.get('TEST_TOKEN',
                            '01ESHK5C9CQ8QXSBX43G19VQVW,ATSb2T2nLKosrsX33B9qoYBqg6PWI4osHA'))
    c.login()

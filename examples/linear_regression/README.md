# Linear Regression

This example shows how you can run a linear regression example against cape. You will need to use the UI to setup
the beginnings of your project.

## Project Setup

### Create Organizations

To run a linear regression task, you must have two orgs to partake in the computation.

You can create an org using [cape-ui](https://github.com/capeprivacy/cape-ui) or your account on [demo.capeprivacy.com](https://demo.capeprivacy.com)

![](../img/create_org.gif)

_Repeat this process for a second org_.

You'll also need to create tokens for your organizations and manually run two workers. See the cape-worker repo
for more details [here](https://github.com/capeprivacy/cape-worker#production-docker-compose).

### Create a Project

Next, create a project within one of the orgs you just created.

![](../img/create_project.gif)

Then, add one of the other orgs you created.

![](../img/add_org.gif)

Copy the project id from the URL and save it for later.

### Get a User Token

Finally, we will need a user token to use with cape-ds. From the home page, ensure you are
working within your user context and navigate to settings to create a token.

![](../img/create_user_token.gif)

Take note of this value as you cannot recover it after you reload the page.

That is it for the UI. We can use cape-ds for the rest of the tutorial.

### cape-ds

[`liner_regression_project.py`](linear_regression_project.py). Provides the functionality needed
to create a linear regression task within your project.

```
python examples/linear_regression/linear_regression_project.py --token=<TOKEN> \
    --project=<PROJECT ID> \
    --coordinator https://demo.capeprivacy.com
```

Fill in the `<TOKEN>` and the `<PROJECT ID>` from earilier and paste it into the above command.

Once the computation completes you should see some output like:

```
Login successful
Project(id=01EY3Y5T3RDGBGYRCW319KDBZ8, name=my-proj, label=my-proj)

Orgs:
	<Organization (id=01EY3W9X6323RZ34XGBA4PRZB6, name=alice_org)>
	<Organization (id=01EY3W9X6WGMZTXMBN9BT8WBB1, name=bob_org)>

Data Views:
	DataView(id=01EY8QX1CT5DDWBTXV9YCCA1J8, name=alice_org-data, location=None)
	DataView(id=01EY8QX1DARH6CME93W511BE1Q, name=bob_org-data, location=None)

Submitted job VerticalLinearRegressionJob(id=01EY8S9V7VATVQ1Y1JX46QZFPW, job_type=LINEAR_REGRESSION, status=Initialized) to run
Waiting for job completion...
Received status Completed. Exitting...
```

If it errored the last line will be:

```
Received status Error. Exitting...
```

Recommend reaching out to platform for help debugging!

**P.S. After running the computation check out your project again to see lots of other goodies about
your job. For example, you'll see whether it succeeded or not, the metrics, how long and ran for,
and history of any other jobs that were run. You're also see a list of activity on your project outlining
every event that has occurded.**

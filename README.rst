commcare-perf
#############

This repository stores performance benchmarking scripts for apps on
`CommCareHQ <https://github.com/dimagi/commcare-hq/>`_,
based on `LocustIO <https://locust.io/>`_.

Installation and setup
^^^^^^^^^^^^^^^^^^^^^^

``pip install -r requirements.txt``

A CommCareHQ web user who is a member of the test domain is required. This user's
username and password should be specified as the environment variables ``LOCUST_USERNAME``
and ``LOCUST_PASSWORD``.

Domain and application, both required, are specified in ``config.yaml``.
Username to login as may also be included.

Configuring and running
^^^^^^^^^^^^^^^^^^^^^^^

Basic usage, for a single test user:

``env LOCUST_USERNAME=$LOCUST_USERNAME env LOCUST_PASSWORD=$LOCUST_PASSWORD locust -f poc.py --headless -u 1 -r 1``

Leave off ``--headless`` to view results in the Locust web UI. See
`docs <https://docs.locust.io/en/stable/running-locust-without-web-ui.html>`_ for options to set number of users,
run time, etc.

Usage for commcarehq.py
^^^^^^^^^^^^^^^^^^^^^^

``env project=us-covid-performance locust -f commcarehq.py --headless  -u 1 -r 1 -t 10m --csv=[csv_location_and_name] --logfile=[log_location_and_name] --tags all``

tags for projects:

covid-ny-staging — tags: home_screen all_cases_case_list all_open_cases_case_list all_closed_cases_case_list ci-form id-form register-new-contact-form

us-covid-performance — tags: home_screen all_cases_case_list all_open_cases_case_list all_closed_cases_case_list new-case-search new-contact-search 

us-covid-performance-bulk — tags: bulk-update-form

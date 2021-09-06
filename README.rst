commcare-perf
#############

This repository stores performance benchmarking scripts for apps on
`CommCareHQ <https://github.com/dimagi/commcare-hq/>`_,
based on `LocustIO <https://locust.io/>`_.

Installation and setup
^^^^^^^^^^^^^^^^^^^^^^

 ::

    $ pip install -r requirements.txt

The following environment variables are required:

* CCHQ_DOMAIN: The test domain name
* CCHQ_APP_ID: The ID of the test app
* CCHQ_USERNAME: The username of a CommCare HQ mobile worker who is a
  member of the test domain. e.g. "j.doe@test-domain.commcarehq.org"
* CCHQ_PASSWORD: Their password

You can use the Locust environment variable ``LOCUST_HOST`` to set the
base URL of the CommCare HQ instance, e.g.
``LOCUST_HOST=https://staging.commcarehq.org``. Alternatively, use
the ``-H`` or ``--host`` command line option.

Environment variables are stored in ``config.env``, which uses the same
format as ``/etc/environment`` or a Docker Compose `env_file`_.

Configuring and running
^^^^^^^^^^^^^^^^^^^^^^^

Basic usage, for a single test user::

    $ export $(grep -v '^#' config.env | xargs)
    $ locust -f form_submission.py --headless -u 1 -r 1

Leave off ``--headless`` to view results in the Locust web UI. See
`docs`_ for options to set number of users, run time, etc.


.. _env_file: https://docs.docker.com/compose/env-file/
.. _docs: https://docs.locust.io/en/stable/running-locust-without-web-ui.html

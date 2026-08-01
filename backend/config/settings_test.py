"""Test settings.

Imports the real configuration and overrides only what must not reach external
infrastructure, so the suite runs without Docker, a reachable PostgreSQL, or —
and this one matters here — the Binance API.

`agents.md §3 local_testing` requires the database to be instantiated in RAM
rather than against the native URL. Everything else stays as production defines
it, so the tests exercise the real stack.
"""

from .settings import *  # noqa: F403

# In-RAM database (agents.md §3 local_testing).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# The breach-corpus validator performs an outbound HTTPS request to the Have I
# Been Pwned range API. The suite must not depend on network reachability.
AUTH_PASSWORD_VALIDATORS = [  # noqa: F405
    validator
    for validator in AUTH_PASSWORD_VALIDATORS  # noqa: F405
    if 'PwnedPasswords' not in validator['NAME']
]

# Argon2 is deliberately slow and the suite does not measure hashing strength.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# DEBUG selects between `new_order_test` and a live `new_order`
# (`docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md`, *Execution mode*). Tests mock
# the SDK client rather than relying on this, but a test run must never be one
# misplaced mock away from a real order, so the dry-run branch is pinned here.
DEBUG = True

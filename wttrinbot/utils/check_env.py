import os
import sys


def check_env():
    lst = [
        "TOKEN",
        "POSTGRES_HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
    ]
    has_error = False
    for env_var in lst:
        if not os.getenv(env_var):
            print(
                f"ERROR: no `{env_var}` environment variable supplied!", file=sys.stderr
            )
            has_error = True
    if has_error:
        sys.exit(1)

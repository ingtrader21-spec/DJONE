import os
import psycopg
from contextlib import contextmanager
DSN=os.getenv("DATABASE_URL","postgresql://djone:djone@postgres:5432/djone")
@contextmanager
def conn():
    with psycopg.connect(DSN) as c:
        yield c

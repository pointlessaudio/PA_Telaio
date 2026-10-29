"""uuid deterministici dello schema: stessi nomi, stessi uuid a ogni rigenerazione (usato anche da test_schema.py)"""
import uuid

NS = uuid.UUID("6f1c2a0e-4b7d-4c1e-9a55-7e3b2d8f0a11")


def uid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))

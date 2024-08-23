from fastapi import Depends, HTTPException, status
import uuid

def generate_random_uuid():
    random_uuid = uuid.uuid4()
    return random_uuid.bytes

def uuid_to_bytes(user_id):
    id = uuid.UUID(user_id)
    return id.bytes


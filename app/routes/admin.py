from pydantic import BaseModel
from enum import Enum
from fastapi import APIRouter, status, Body
from app.services.redis_handler import redis_client, get_rule_key
from fastapi import HTTPException
from app.services.rate_limiters.algo_types import RateLimitingAlgoType


class IdentifierType(Enum):
    IDENTIFIER_IP = 1
    IDENTIFIER_API_KEY = 2
    IDENTIFIER_USER_ID = 3
    IDENTIFIER_ROUTE = 4
    IDENTIFIER_ORG_ID = 5


router = APIRouter()


class RateLimitModel(BaseModel):
    identifier_type: int
    identifier_value: str
    rate_limit: int
    refill_rate: int
    algorithm: str


@router.get('/rule/{identifier}', response_model=RateLimitModel)
def get_rule(identifier: str):
    key = get_rule_key(identifier)
    data = redis_client.hgetall(key)

    if not data:
        raise HTTPException(
            status_code=404, detail='Rate limit rule not found')

    try:
        return RateLimitModel(
            identifier_type=(int(data['identifier_type'])),
            identifier_value=identifier,
            rate_limit=int(data['rate_limit']),
            refill_rate=int(data['refill_rate']),
            algorithm=data['algorithm']
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail='Invalid data in Redis')


@router.post('/rule/', status_code=status.HTTP_201_CREATED)
def add_rule(rate_limit_rule: RateLimitModel):
    key = get_rule_key(rate_limit_rule.identifier_value)

    if redis_client.exists(key):
        raise HTTPException(
            status_code=409, detail='Rate limit rule already exists')

    redis_client.hset(key, mapping={
        'identifier_type': rate_limit_rule.identifier_type,
        'rate_limit': rate_limit_rule.rate_limit,
        'refill_rate': rate_limit_rule.refill_rate,
        'algorithm': rate_limit_rule.algorithm
    })

    return {'msg': 'Rate limit rule created', 'identifier': rate_limit_rule.identifier_value}


@router.put('/rule/{identifier}', status_code=status.HTTP_200_OK)
def modify_rule(identifier: str, rate_limit_rule: RateLimitModel = Body(...)):
    key = get_rule_key(identifier)
    if rate_limit_rule.identifier_value != identifier:
        raise HTTPException(
            status_code=422, detail='identifier in path does not match identifier_value in body')

    if not redis_client.exists(key):
        raise HTTPException(
            status_code=404, detail='Rate limit rule not found')

    redis_client.hset(key, mapping={
        'identifier_type': rate_limit_rule.identifier_type,
        'rate_limit': rate_limit_rule.rate_limit,
        'refill_rate': rate_limit_rule.refill_rate,
        'algorithm': rate_limit_rule.algorithm
    })

    return {'msg': 'Rate limit rule updated', 'identifier': identifier}


@router.delete('/rule/{identifier}', status_code=status.HTTP_200_OK)
def delete_rule(identifier: str):
    key = get_rule_key(identifier)

    if not redis_client.exists(key):
        raise HTTPException(
            status_code=404, detail='Rate limit rule not found')

    redis_client.delete(key)

    return {'msg': 'Rate limit rule deleted', 'identifier': identifier}


@router.post('/rule/default', status_code=status.HTTP_201_CREATED)
def add_default_rule(rate_limit_rule: RateLimitModel):
    key = get_rule_key('default')

    if redis_client.exists(key):
        raise HTTPException(
            status_code=409, detail='Default rate limit rule already exists'
        )

    redis_client.hset(key=key, mapping={
        'identifier_type': IdentifierType.IDENTIFIER_ROUTE,
        'rate_limit': rate_limit_rule.rate_limit,
        'refill_rate': rate_limit_rule.refill_rate,
        'algorithm': rate_limit_rule.algorithm
    })

    return {'msg': 'Default rate limit rule created'}

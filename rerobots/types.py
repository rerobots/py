from typing import Literal, TypedDict


Capability = Literal['CAP_NO_INSTANTIATE', 'CAP_INSTANTIATE']
InstanceStatus = Literal['INIT', 'INIT_FAIL', 'READY', 'TERMINATING', 'TERMINATED']


class AccessRule(TypedDict):
    id: int
    date_created: str
    user: str
    wdeployment_id: str
    capability: Capability
    param: int


class AccessRules(TypedDict):
    rules: list[AccessRule]


class CamImage(TypedDict, total=False):
    success: bool
    message: str
    format: Literal['JPEG', 'ndarray']
    coding: Literal[None, 'base64']
    data: str

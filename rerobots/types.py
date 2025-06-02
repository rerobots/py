from typing import Literal, NotRequired, TypedDict


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


class CamImage(TypedDict):
    success: bool
    message: NotRequired[str]
    format: NotRequired[Literal['JPEG', 'ndarray']]
    coding: NotRequired[Literal[None, 'base64']]
    data: NotRequired[str]

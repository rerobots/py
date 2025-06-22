from typing import Literal, TypedDict


AddonStatus = Literal['active', 'notfound', 'starting']
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


class PortForward(TypedDict, total=False):
    ipv4: str
    port: int


class DeploymentInfo(TypedDict, total=False):
    id: str
    type: str
    type_version: int
    supported_addons: list[str]
    desc: str
    region: str
    icounter: int
    created: str
    queuelen: int
    lockout: bool
    online: bool


class InstanceInfo(TypedDict, total=False):
    id: str
    deployment: str
    type: str
    status: InstanceStatus
    region: str
    starttime: str
    fwd: PortForward
    hostkeys: list[str]


class CameraAddon(TypedDict, total=False):
    status: AddonStatus


class MistyProxyAddon(TypedDict, total=False):
    status: AddonStatus
    url: list[str]

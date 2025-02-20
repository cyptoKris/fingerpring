import random
from typing import Literal, Optional
from pydantic import BaseModel, Field

windows_webgl = [
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Ti Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Ti Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 2080 Ti Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 Super Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 2080 Super Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
    [
        "Google Inc.(NVIDIA)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Super Direct3D12 vs_5_0 ps_5_0, D3D12)",
    ],
]
mac_webgl = [
    ["Google Inc. (Apple)", "ANGLE (Apple, Apple M1, OpenGL 4.1)"],
    [
        "Google Inc. (ATI Technologies Inc.)",
        "ANGLE (ATI Technologies Inc., AMD Radeon Pro 5300M OpenGL Engine, OpenGL 4.1)",
    ],
    [
        "Google Inc. (Intel Inc.)",
        "ANGLE (Intel Inc., Intel(R) Iris(TM) Plus Graphics 655, OpenGL 4.1)",
    ],
    ["Google Inc. (Apple)", "ANGLE (Apple, Apple M2, OpenGL 4.1)"],
]


class FingerprintModel(BaseModel):
    red: int = Field(default=3)
    green: int = Field(default=3)
    blue: int = Field(default=3)
    alpha: int = Field(default=3)

    proxy_scheme: Optional[str] = Field(default="http")
    proxy_host: Optional[str] = Field(default=None)
    proxy_port: int = Field(default=1080)
    proxy_password: str = Field(default="123456")

    platform: str = Field(default="macos")
    chrome_version: str = Field(default="122")
    webgl_vendor: str = Field(default="Google Inc. (ATI Technologies Inc.)")
    webgl_renderer: str = Field(
        default="ANGLE (ATI Technologies Inc., AMD Radeon Pro 555X OpenGL Engine, OpenGL 4.1)"
    )
    timezone: str = Field(default="Asia/Singapore")
    tools_url: Optional[str] = Field(default=None)


def random_fingerprint(
    proxy_host: str,
    proxy_port: int,
    chrome_version: str,
    platform: Literal["macos", "windows"],
) -> FingerprintModel:
    if platform == "macos":
        webgl_info = random.choice(mac_webgl)
    else:
        webgl_info = random.choice(windows_webgl)
    info = {
        "red": random.randint(-5, 5),
        "green": random.randint(-5, 5),
        "blue": random.randint(-5, 5),
        "alpha": random.randint(-5, 5),
        "proxy_scheme": "socks5",
        "proxy_host": proxy_host,
        "proxy_port": proxy_port,
        "platform": platform,
        "chrome_version": chrome_version,
        "webgl_vendor": webgl_info[0],
        "webgl_renderer": webgl_info[1],
    }
    return FingerprintModel.model_validate(info)


def check_fingerprint(fp_info: dict) -> FingerprintModel:
    return FingerprintModel.model_validate(fp_info)

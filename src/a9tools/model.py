from email.policy import default
from typing import Optional

from pydantic import BaseModel, Field


class WalletInfo(BaseModel):
    private_key: str = Field(default="", description="钱包私钥 ")
    address: str = Field(default="", description="钱包地址")
    name: str = Field(default="", description="钱包名称")
    mnemonic: str = Field(default="", description="钱包助记词 ")


class DiscordInfo(BaseModel):
    account: Optional[str] = Field(default="", description="账号")
    password: Optional[str] = Field(default="", description="密码")
    discord_token: Optional[str] = Field(default="", description="discord token")


class EmailInfo(BaseModel):
    address: str = Field(default="", description="邮箱地址")
    password: str = Field(default="", description="邮箱密码")
    server: str = Field(default="", description="邮箱IMAP地址")


class TwitterInfo(BaseModel):
    username: str = Field(default="", description="twitter用户名")
    password: str = Field(default="", description="twitter密码")
    email: str = Field(default="", description="邮箱地址")
    token: str = Field(default="", description="twitter token")
    p2fa: str = Field(default="", description="2fa")


class Fingerprint(BaseModel):
    red: int = Field(default=0)
    green: int = Field(default=0)
    blue: int = Field(default=0)
    alpha: int = Field(default=0)
    platform: str = Field(default="windows")
    chrome_version: str = Field(default="")
    webgl_renderer: str = Field(default="")
    webgl_vendor: str = Field(default="")
    timezone: str = Field(default="")
    user_agent: str = Field(default="")


class InputInfoBase(BaseModel):
    wallet: WalletInfo = Field(..., description="钱包信息")
    fingerprint: Optional[Fingerprint] = Field(None, description="指纹信息")  # 设置默认值为 None
    twitter_token: Optional[str] = Field(default="", description="twitter token")
    discord: Optional[DiscordInfo] = Field(default=None, description="discord信息")
    twitter: Optional[TwitterInfo] = Field(default=None, description="twitter信息")
    email: Optional[EmailInfo] = Field(default=None, description="邮箱信息")
    user_data_path: str = Field(..., description="用户数据目录")

    proxy_scheme: str = Field(default="socks5")
    proxy_host: str = Field(default="127.0.0.1")
    proxy_port: int = Field(default=1080)
    proxy_password: str = Field(default="123456")

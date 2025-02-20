# HandlerBase

## 定义

```python
from a9tools import HandlerBase


class Handler(HandlerBase):

    @override
    def start_url(self) -> str:
        """
        项目启动链接
        必须实现，初始化完指纹插件以后会自动打开这个地址
        """
        return "https://airdrop.liquidswap.com/"

    def run(self):
        self.driver = self.init_driver()
        # 完成后面的任务逻辑
```


## 使用

```python

from contextlib import contextmanager
from typer import Typer
from src.handler import Handler


app = Typer()


@contextmanager
def main(path):
    """
    自定义上下文，任务结束以后调用 finish，保存初始化的指纹信息
    如果不这么写，那必须自己的任务逻辑结束的时候调用一次 self.finish()
    """
    ctrl = Handler(path)
    yield ctrl
    ctrl.finish()


@app.command("run")
def run(path):
    """
    定义启动命令
    """
    # 使用with 语句自动管理上下文
    with main(path) as handler:
        handler.run()




if __name__ == "__main__":
    app()
```


## 常用方法

- 等待新窗口打开

```python
new_tab = self.wait_new_tab() # timeout 默认为 10 秒，十秒未打开即抛出异常
```

## MetaMask 使用示例

钱包插件默认密码为 `localpwd`

```python
from a9tools.metamask import MetaMask

# 默认 self.driver 为主窗口

wallet = MetaMask()

# 等待签名等弹窗出现
wallet_tab = self.wait_new_tab()

# 初始化钱包扩展程序
wallet.init_wallet_extension(wallet_tab)

# 创建扩展程序密码
wallet.create_extension_pwd(tab)

# 进入首页
wallet.into_home_page(tab)

# 导入钱包
wallet.import_wallet(pk, tab)
```

## Twitter 常用方法


相关方法以`self.twitter_` 开始，包括 token 登录，点赞，关注，转发。

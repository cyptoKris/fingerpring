# a9tools

项目的 python 依赖包

使用示例：[HandlerBase](handler_demo.md)

## 实现功能

- 初始化浏览器加载指纹信息

## 用法

1. 将本项目 clone 到本地

```
git clone git@github.com:luluhunters/a9tools.git
```

2. 需要使用的项目放在和 `a9tools` 同级目录下。

```
❯ tree -L 1                                                                                                                                      🅒 pontem  v3.12.3 
.
├── Pontem
├── a9tools
└── ...(其他项目)
```

3. 将本项目作为依赖配置到其他项目。以 `Pontem` 作为示例。

```
pdm add ../a9tools
```

这样即可在代码中导入使用

```python
from a9tools import HandlerBase
```

项目的依赖文件变动如下，a9tools 会指向本地的目录

```toml
dependencies = [
    "web3>=6.18.0",
    "eth-account>=0.11.2",
    "a9tools @ file:///${PROJECT_ROOT}/../a9tools",
]
```

增加其他依赖

```
pdm add [其他依赖]
```

## 如何初始化一个新项目

1. 创建项目目录

```bash
mkdir project_a
cd project_a
pdm init
```

一路回车。

2. 添加`a9tools`到项目依赖中。

```bash
pdm add ../a9tools
```

3. 添加必要的两个指纹浏览器扩展程序

```bash
git init
git submodule add git@github.com:luluhunters/tools-extension.git extensions/tools
git submodule add git@github.com:luluhunters/webrtc-control.git extensions/webrtc-control
```

https
```bash
git init
git submodule add https://github.com/luluhunters/tools-extension.git extensions/tools
git submodule add https://github.com/luluhunters/webrtc-control.git extensions/webrtc-control
```

4. 指纹插件更新以后怎么办？

```bash
git submodule update --rebase --remote
```

5. 我 `clone` 一个项目跑的时候，`git submodule add` 已存在的插件的时候报错怎么办？

`git submodule add`的作用是给项目添加新的 git 依赖，会在项目目录下的`.gitmodules`中增加依赖，如果已经存在，当然会报错。
这时候应该使用

```
git submodule update
```

## 如何启动一个存在的项目

以`Pontem` 作为示例。

1. `clone` 项目并安装依赖。

```bash
git clone git@github.com:luluhunters/Pontem.git
cd Pontem
pdm install
```

2. 安装必要的浏览器扩展程序(tools、webrtc)

```bash
git submodule update --init --recursive
```

3. 安装项目需要的钱包插件。

``` bash
python load_extensions.py
```


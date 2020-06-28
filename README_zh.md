# JILL.py

_跨平台的 Julia 一键安装脚本_

![](https://img.shields.io/badge/system-Windows%7CmacOS%7CLinux%7CFreeBSD-yellowgreen)
![](https://img.shields.io/badge/arch-i686%7Cx86__64%7CARMv7%7CARMv8-yellowgreen)

[![py version](https://img.shields.io/pypi/pyversions/jill.svg?logo=python&logoColor=white)](https://pypi.org/project/jill)
[![version](https://img.shields.io/pypi/v/jill.svg)](https://github.com/johnnychen94/jill.py/releases)
[![Actions Status](https://github.com/johnnychen94/jill.py/workflows/Unit%20test/badge.svg
)](https://github.com/johnnychen94/jill.py/actions)
[![codecov](https://codecov.io/gh/johnnychen94/jill.py/branch/master/graph/badge.svg)](https://codecov.io/gh/johnnychen94/jill.py)
[![release-date](https://img.shields.io/github/release-date/johnnychen94/jill.py)](https://github.com/johnnychen94/jill.py/releases)
[![README](https://img.shields.io/badge/README-English-blue)](README.md)

为什么使用 `jill.py`? 常见的包管理工具有时会因为依赖版本的原因（例如提供一个错误的LLVM版本）安装一个不能正常使用的 Julia，
因此推荐的安装方式是从 [Julia 下载](https://julialang.org/downloads/) 中下载并解压 Julia 官方提供的 Julia 二进制程序。
`jill.py` 的目的是为了让这一操作变得尽可能简单。

用 Python 安装 Julia? 因为 Python 现在已经成为了一个主流的运维工具，因此使用 Python 可以带来一个跨平台的统一安装程序。 “要用魔法打败魔法” -- 老爹

使用 `jill.py` 安全吗？是的，`jill` 会使用 GPG 来检查每一个下载的包。

## 特性

* 从最近的镜像站下载 Julia
* 自动发现新的 Julia 版本
* 跨平台
* 安装并管理多个 Julia 版本

## 安装 jill

首先你要通过 pip 来安装`jill`: `pip install jill --user -U`，并且需要 `3.6` 以上的 Python 版本


## 使用帮助

简而言之，`jill install [version]` 能满足你绝大部分要求

<details>
<summary>安装 demo</summary>
<img class="install" src="screenshots/install_demo.png"/>
</details>

当你输入 `jill install` 的时候，它其实做了以下几件事:

1. 找到最新的稳定版(目前是`1.4.2`)
2. 下载、验证并安装Julia
3. 创建一些别名，例如：`julia`, `julia-1`, `julia-1.4`
  * 对于每日构建版，别名则只会绑定到 `julia-latest`

其中 `version` 是可选的，支持的语法为：

- `stable`: 最新稳定版
- `1`: 最新的`1.y.z`稳定版本
- `1.2`: 最新的`1.2.z`稳定版本
- `1.2.3`/`1.2.3-rc1`: 如其所是
- `nightly`/`latest`: 每天从源码中构建的版本

除此之外还有一些额外的命令和参数可以使用：

* 仅下载：
    - `jill download`
    - 下载其他系统及平台的安装包：`jill download --sys linux --arch i686`
* 安装：
    - (Linux only) 所有用户都可以使用：`sudo jill install`
    - 从旧的 Julia 版本“升级”： `jill install --upgrade`
    - 不需要交互确认直接安装：`jill install --confirm`
* 下载源：
    - 列出所有下载源
    - 指定从官网下载：`jill download --upstream Official`
    - 从局域网私有源下载：创建一个类似的[配置文件](jill/config/sources.json)并存放在：
        * Linux, MacOS and FreeBSD: `~/.config/jill/sources.json`
        * Windows: `~/AppData/Local/julias/sources.json`

更多的参数及其作用请查看帮助文档: `jill [COMMAND] -h` (例如`jill install -h`)


## 案例 -- Cron

通过使用`cron`，`jill` 还能够保证在你的服务器上提供一个最新版本的每日构建版：

```bash
# /etc/cron.d/jill
PATH=/usr/local/bin:/usr/sbin:/usr/sbin:/usr/bin:/sbin:/bin

# install a fresh nightly build every day
* 0 * * * root jill install latest --confirm
```

类似地，你也可以通过加一个 `jill install --confrim` 来保证 `julia` 永远是最新地稳定发行版。一旦有新的 Julia 版本
发布了，`jill` 就能够下载到它 -- 你甚至不需要更新`jill`。

## 镜像源的搭建

Check the [English version](README.md) :)

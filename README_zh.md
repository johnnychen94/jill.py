# JILL.py

![](https://img.shields.io/badge/system-Windows%7CmacOS%7CLinux%7CFreeBSD-yellowgreen)
![](https://img.shields.io/badge/arch-i686%7Cx86__64%7CARMv7%7CARMv8-yellowgreen)

[![py version](https://img.shields.io/pypi/pyversions/jill.svg?logo=python&logoColor=white)](https://pypi.org/project/jill)
[![version](https://img.shields.io/pypi/v/jill.svg)](https://github.com/johnnychen94/jill.py/releases)
[![Actions Status](https://github.com/johnnychen94/jill.py/workflows/Unit%20test/badge.svg
)](https://github.com/johnnychen94/jill.py/actions)
[![codecov](https://codecov.io/gh/johnnychen94/jill.py/branch/master/graph/badge.svg)](https://codecov.io/gh/johnnychen94/jill.py)
[![release-date](https://img.shields.io/github/release-date/johnnychen94/jill.py)](https://github.com/johnnychen94/jill.py/releases)

跨平台的Julia一键安装脚本

## 特性

* 从最近的镜像站下载最新的Julia版本
* 跨平台
* 安装并管理多个Julia版本

## 安装 jill

首先你要通过 pip 来安装`jill`: `pip install jill --user -U`，并且需要3.6以上的 Python 版本


## 使用帮助

简而言之，`jill install [version]` 能满足你绝大部分要求

<details>
<summary>安装 demo</summary>
<img class="install" src="screenshots/install_demo.png"/>
</details>

当你输入`jill install`的时候，它其实做了以下几件事:

1. 找到最新的稳定版(目前是`1.3.1`)
2. 下载、验证并安装Julia
3. 创建一些别名：`julia-1`, `julia-1.3`

`version`是可选的：

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
    - 从旧版本“升级”： `jill install --upgrade`
    - 不需要交互：`jill install --confirm`
* 下载源：
    - 列出所有下载源
    - 指定从官网下载：`jill download --upstream Official`
    - 从局域网私有源下载：创建一个类似的[配置文件](jill/config/sources.json)并存放在：
        * Linux, MacOS and FreeBSD: `~/.config/jill/sources.json`
        * Windows: `~/AppData/Local/julias/sources.json`

更多的参数及其作用请查看帮助文档: `jill [COMMAND] -h` (例如`jill install -h`)

## 镜像源的搭建

Check the [English version](README.md) :)

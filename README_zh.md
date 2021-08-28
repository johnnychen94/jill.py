# JILL.py

<p>
  <img width="150" align='right' src="logo.png">
</p>

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

## 特性

* 从最近的镜像站下载 Julia
* 支持所有系统及架构
* 安装并管理多个 Julia 版本
* 简单易用的命令行工具

[![asciicast](https://asciinema.org/a/432654.svg)](https://asciinema.org/a/432654)

## 安装 JILL

首先你要通过 pip 来安装`jill`: `pip install jill --user -U`， 并且需要 `3.6` 以上的 Python 版本。 更新 JILL 也可以通过这条命令来得到。

> "我们要用魔法打败魔法" -- 老爹

## 安装 Julia

当你输入 `jill install` 的时候， 在背后实际上发生了这样三件事：

1. 查询最新的 Julia 版本
2. 下载、 验证及安装 Julia
3. 创建一些别名 （符号链接）， 例如 `julia`、 `julia-1`、 以及 `julia-1.6`

对于一般的 Julia 用户来说：

* 安装最新稳定版: `jill install`
* 安装最新稳定的 1.x 版本： `jill install 1`
* 安装最新稳定的 1.6.x 版本: `jill install 1.6`
* 安装特定版本： `jill install 1.6.2`, `jill install 1.7.0-beta3`
* 安装包括测试版在内的最新版本： `jill install --unstable`

对 Julia 开发者和维护者来说：

* 安装每日构建版本 (nightly builds)： `jill install latest`。 对应的别名为 `julia-latest`.
* 安装 Julia 仓库中指定 commit 的 CI 构建: `jill install 1.8.0+cc4be25c`. (遵照 `<major>.<minor>.<patch>+<build>` 形式并且提供 HASH 的至少前 7 位。) 对应的别名为 `julia-dev`。

一些可能用得到的参数：

* 跳过安装确认： `jill install --confirm`
* 从 Julia 官方上游而非镜像站进行下载： `jill install --upstream Official`
* 在安装完成之后保留 Julia 安装程序： `jill install --keep_downloads`
* 强制重新安装： `jill install --reinstall`

## 别名和符号链接

启动 Julia 的话是通过 JILL 创建的别名 (例如 `julia`, `julia-1`) 来启动的， `jill install` 采用下述规则来确保你始终在使用最新稳定版本的 Julia。

稳定版：

* `julia` 指向最新稳定版 Julia
* `julia-1` 指向最新稳定版 Julia 1.y.z
* `julia-1.6` 指向最新稳定版 Julia 1.6.z

对于不稳定的测试版 （例如 `1.7.0-beta3`）， 通过 `jill install 1.7 --unstable` 或者 `jill install 1.7.0-beta3` 来安装的话， 都只会创建 `julia-1.7` 这个别名而不会修改 `julia` 或者 `julia-1`.

想在每日构建及开发版本疯狂试探？

* `julia-latest` 指向通过 `jill install latest` 安装的每日构建版本
* `julia-dev` 指向通过 `jill install 1.8.0+cc4be25c` 这种方式安装的特定commit上构建的版本。

### 列举所有的别名和对应的版本

`jill list [version]` 可以给出所有的别名和它们所指向的 Julia 版本。

![list](https://user-images.githubusercontent.com/8684355/131207375-8b355e2b-3a67-4b70-8d2d-83623ae1e451.png)

### 更改别名所指向的版本

对于非 Windows 系统来说， JILL 别名实际上就是符号链接 (symlink)， 所以你完全可以通过 `ln` 命令来修改它。 对于 Windows 系统来说， JILL 使用了 `.cmd` 文件作为入口因此需要对对应文件进行调整。 另一方面， `jill swtich` 命令提供了一种简单统一的方式来实现这一功能：

* `jill switch 1.6`: 让 `julia` 指向 Julia 1.6.z 版本
* `jill switch <其他的 Julia 可执行文件路径>`: 让 `julia` 指向其他的可执行文件作为 Julia 的入口。
* `jill switch 1.6 --target julia-1`: 让 `julia-1` 指向 Julia 1.6.z 版本。

## 关于下载源

默认情况下， JILL 会从最近的上游下载数据。 你可以通过 `jill upstream` 来查询所有的上游信息。

![upstream](https://user-images.githubusercontent.com/8684355/131207372-03220bc4-bf79-408d-b386-ef9b41524ccd.png)

如果需要暂时关闭这一功能， 你可以通过 `--upstream <server_name>` 来指定具体的下载源， 例如 `jill install --upstream Official` 会确保从官方源下载数据。

如果需要永久关闭这一功能的话， 你可以设置环境变量 `JILL_UPSTREAM`.

需要注意的是， `--upstream` 的优先级比环境变量要高。 例如， 如果设置 `JILL_UPSTREAM="TUNA"`， 那么 `jill install --upstream Official` 依然会从官方源下载数据。

## 关于安装位置及别名的创建位置

下表列举了不同系统下的默认安装位置以及别名的存放位置：

| 系统            | 安装位置                   | 别名存放位置                   |
| -------------- | ------------------------- | ---------------------------- |
| macOS          | `/Applications`           | `~/.local/bin`               |
| Linux/FreeBSD  | `~/packages/julias`       | `~/.local/bin`               |
| Windows        | `~\AppData\Local\julias`  | `~\AppData\Local\julias\bin` |

例如， 在 Linux 系统上 `jill install 1.6.2` 会创建一个文件夹 `~/packages/julias/julia-1.6` 并且创建一些符号链接 `julia`、 `julia-1`、 以及 `julia-1.6` 在 `~/.local/bin` 下面。

特别地， 如果你以 `root` 用户的身份在使用 `jill` 的话， 安装好的 Julia 可以被所有用户使用：

* 对于 Linux/FreeBSD 来说， 安装位置为 `/opt/julias`。
* 对于 Linux/FreeBSD/macOS 来说， 符号链接会创建在 `/usr/local/bin` 下面。

如果想要改变默认的 JILL 安装位置以及符号链接创建的位置， 你可以设置环境变量 `JILL_INSTALL_DIR` 以及 `JILL_SYMLINK_DIR`.

**（弃用）** `jill install` 也提供 `--install_dir <dirpath>` 和 `--symlink_dir <dirpath>` 来调整位置。 他们比环境变量 `JILL_INSTALL_DIR` 和 `JILL_SYMLINK_DIR` 的优先级要高。

## JILL 环境变量

`jill` 被设计为一个方便使用的命令行工具， 频繁输入一些特定的参数可能会非常繁琐， 因此 `jill` 预设了一些环境变量来改变默认的值：

* 指定默认的下载源 `JILL_UPSTREAM`: `--upstream`
* 指定默认的符号链接创建的位置 `JILL_SYMLINK_DIR`： `--symlink_dir`
* 指定默认的安装位置 `JILL_INSTALL_DIR`: `--install_dir`

手动的参数输入 (例如 `--upstream`) 要比预设的环境变量的优先级更高。

---

关于其他更多的说明， 请参考[英文版本](README.md)

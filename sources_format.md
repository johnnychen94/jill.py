# The sources.json format

In the registry config file, a new mirror is a dictionary in the `upstream` field:

* `name`: a distinguishable mirror name.
* `urls`: URL template to retrive Julia release.
* `latest_urls`: URL template to retrive the nightly build of Julia release. If the server doesn't
  provide contents for `jill install latest`, then leave this as blank.
* `versions`: URL to get the `versions.json` file. By default it uses
  `https://julialang-s3.julialang.org/bin/versions.json`.

## Placeholders

Placeholders are used to register new mirrors. For example, the stable release url of
the "Official" release server provided by [Julialang.org](https://julialang.org/) is
`"https://julialang-s3.julialang.org/bin/$sys/$arch/$minor_version/$filename"`

There're several predefined placeholders for various systems and architectures:

* `system`: `windows`, `macos`, `linux`, `freebsd`
* `sys`: `winnt`, `mac`, `linux`, `freebsd`
* `os`: `win`, `mac`, `linux`, `freebsd`
* `architecture`: `x86_64`, `i686`, `ARMv7`, `ARMv8`
* `arch`: `x86`, `x64`, `armv7l`, `aarch64`
* `osarch`: `win32`, `win64`, `mac64`, `linux-armv7l`, `linux-aarch64`
* `osbit`: `win32`, `win64`, `linux32`, `linux64`, `linuxaarch64`
* `bit`: `32`, `64`
* `extension`: `exe`, `tar.gz`, `dmg` (no leading `.`)

There're also placeholders for versions:

* `patch_version`: `1.2.3`, `latest`
* `minor_version`: `1.2`, `latest`
* `major_version`: `1`
* `version`: `1.2.3-pre`, `latest` (no leading `v`)
* `vpatch_version`: `v1.2.3`, `latest`
* `vminor_version`: `v1.2`, `latest`
* `vmajor_version`: `v1`, `latest`

To keep consistent names with official releases, you can use predefined name placeholders:

* stable release `filename`: `julia-$version-$osarch.$extension`
* nightly release `latest_filename`: `"julia-latest-$osbit.$extension"`

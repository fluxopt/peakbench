# Changelog

## [0.2.0](https://github.com/fluxopt/pytest-benchmem/compare/v0.1.0...v0.2.0) (2026-06-13)


### ⚠ BREAKING CHANGES

* mirror memray's metrics — add total memory allocated ([#39](https://github.com/fluxopt/pytest-benchmem/issues/39))
* memory regression gate, @pytest.mark.benchmem, bytes blob migration ([#32](https://github.com/fluxopt/pytest-benchmem/issues/32))

### Features

* empirical scaling fit — report O(n^x) over a size sweep ([#36](https://github.com/fluxopt/pytest-benchmem/issues/36)) ([4bc6e46](https://github.com/fluxopt/pytest-benchmem/commit/4bc6e4683142c46c9c60765dbf1f8e39adb3388f))
* memory regression gate, [@pytest](https://github.com/pytest).mark.benchmem, bytes blob migration ([#32](https://github.com/fluxopt/pytest-benchmem/issues/32)) ([654c582](https://github.com/fluxopt/pytest-benchmem/commit/654c582a15a8f8ef8e79a7c1d41767660d5f962a))
* mirror memray's metrics — add total memory allocated ([#39](https://github.com/fluxopt/pytest-benchmem/issues/39)) ([0b6fad6](https://github.com/fluxopt/pytest-benchmem/commit/0b6fad6f90ef124b1c80ca368c1d4db6fe5b34af))


### Bug Fixes

* correct release-please pre-major key so feat! bumps 0.2.0 not 1.0.0 ([#41](https://github.com/fluxopt/pytest-benchmem/issues/41)) ([fac21e0](https://github.com/fluxopt/pytest-benchmem/commit/fac21e08bfaf5816f067fd78da57aa623c1b563d))

## [0.1.0](https://github.com/fluxopt/pytest-benchmem/compare/v0.1.0...v0.1.0) (2026-06-13)


### ⚠ BREAKING CHANGES

* rename package peakbench → pytest-benchmem ([#10](https://github.com/fluxopt/pytest-benchmem/issues/10))
* pivot to the memory companion to pytest-benchmark ([#7](https://github.com/fluxopt/pytest-benchmem/issues/7))

### Features

* --benchmark-memory flag to augment existing benchmark() calls ([#16](https://github.com/fluxopt/pytest-benchmem/issues/16)) ([aff17c7](https://github.com/fluxopt/pytest-benchmem/commit/aff17c76ad742cedc963e7914bd575846ddc6035))
* pivot to the memory companion to pytest-benchmark ([#7](https://github.com/fluxopt/pytest-benchmem/issues/7)) ([52f2b6b](https://github.com/fluxopt/pytest-benchmem/commit/52f2b6b56af1ee61f84fcd0ab9dc0947004fd31d))
* resolve [#2](https://github.com/fluxopt/pytest-benchmem/issues/2) — drop select=, bless filter-before-convert ([89fbfcd](https://github.com/fluxopt/pytest-benchmem/commit/89fbfcdde439eb6f1535df8e65d2295b2ea69add))


### Miscellaneous Chores

* release pytest-benchmem as 0.1.0 ([#13](https://github.com/fluxopt/pytest-benchmem/issues/13)) ([8e51760](https://github.com/fluxopt/pytest-benchmem/commit/8e51760d7bdfe4e44ea77856e8a0c4e158de0099))


### Code Refactoring

* rename package peakbench → pytest-benchmem ([#10](https://github.com/fluxopt/pytest-benchmem/issues/10)) ([1e48259](https://github.com/fluxopt/pytest-benchmem/commit/1e482590bef2767df1619bcae15a6d132f4cc610))

## [0.1.0](https://github.com/fluxopt/pytest-benchmem/compare/v0.0.1...v0.1.0) (2026-06-13)


### ⚠ BREAKING CHANGES

* rename package peakbench → pytest-benchmem ([#10](https://github.com/fluxopt/pytest-benchmem/issues/10))
* pivot to the memory companion to pytest-benchmark ([#7](https://github.com/fluxopt/pytest-benchmem/issues/7))

### Features

* pivot to the memory companion to pytest-benchmark ([#7](https://github.com/fluxopt/pytest-benchmem/issues/7)) ([52f2b6b](https://github.com/fluxopt/pytest-benchmem/commit/52f2b6b56af1ee61f84fcd0ab9dc0947004fd31d))


### Miscellaneous Chores

* release pytest-benchmem as 0.1.0 ([#13](https://github.com/fluxopt/pytest-benchmem/issues/13)) ([8e51760](https://github.com/fluxopt/pytest-benchmem/commit/8e51760d7bdfe4e44ea77856e8a0c4e158de0099))


### Code Refactoring

* rename package peakbench → pytest-benchmem ([#10](https://github.com/fluxopt/pytest-benchmem/issues/10)) ([1e48259](https://github.com/fluxopt/pytest-benchmem/commit/1e482590bef2767df1619bcae15a6d132f4cc610))

## 0.0.1 (2026-06-13)


### Features

* resolve [#2](https://github.com/fluxopt/pytest-benchmem/issues/2) — drop select=, bless filter-before-convert ([89fbfcd](https://github.com/fluxopt/pytest-benchmem/commit/89fbfcdde439eb6f1535df8e65d2295b2ea69add))

# Release procedure

* Fill out `Changelog`
* Check copyright year in `LICENSE`
* Change version in `gradools/__init__.py`
* `git tag -s 0.1a1`
* `git clean -fxd`
* `flit build`
* `flit publish`

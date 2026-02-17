#!/usr/bin/env python3
#
# Date:    2026/02/03
# Author:  andyp3r3z
#
# Fabric configuration file.

from importlib import import_module, util
from os import environ
from pathlib import Path
from types import ModuleType
from typing import Any

from fabric.core.application import Application
from fabric.utils import get_relative_path


def load_config() -> dict[str, Any]:
	"""
	Loads config from $XDG_CONFIG_HOME/fabric/config.py
	Creates it if not there already.
	"""
	# This is where the real config lives (more declarative).
	config_module: Path = Path(
		environ.get("XDG_CONFIG_HOME", Path.home()/".config")
	)/"felt"/"config.py"
	config_module.parent.mkdir(exist_ok=True, parents=True)
	if not config_module.exists():
		with open(config_module, "w") as f:
			f.write("")
	spec = util.spec_from_file_location("config", config_module)
	module: ModuleType = util.module_from_spec(spec) # type: ignore
	assert spec and spec.loader
	spec.loader.exec_module(module)
	return getattr(module, "CONFIG", {})


# This imports all modules declared in `PARAMS` dict.
# You should be able to import your modules as if you were using
# `from module_name import main`, where `main` is the function that will be
# executed with the params given.

def main() -> None:
	CONFIG: dict[str, Any] = load_config()
	app: Application = Application("shell")
	for module_name, module_config in CONFIG.items():
		module: ModuleType = import_module(f"{module_name}.main")
		func: Any | None = getattr(module, "main", None)
		if not callable(func):
			raise ValueError(f"`from {module_name}.main import main` failed.")
		app.add_window(func(**module_config))
	app.set_stylesheet_from_file(get_relative_path("./style/main.css"))
	app.run()

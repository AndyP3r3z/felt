#!/usr/bin/env python3
#
# Date:    2026/02/03
# Author:  andyp3r3z
#
# Fabric configuration file.

from importlib import util
from importlib.machinery import ModuleSpec
from os import environ
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from fabric.core.application import Application

CONFIG_PATH: Path = Path(
	environ.get("XDG_CONFIG_HOME", Path.home()/".config")
)/"felt"

def get_module_path(name: str) -> Path:
	"""
	Resolves the module path inside the XDG_CONFIG_HOME folder.
	"""
	if name == "config":
		return CONFIG_PATH/"config.py"
	mod_path: Path = CONFIG_PATH/name
	mod_path.mkdir(parents=True, exist_ok=True)
	return mod_path/"main.py"

def import_config_module(name: str) -> ModuleType:
	"""
	Imports and returns the module inside XDG_CONFIG_HOME.
	"""
	path: Path = get_module_path(name)
	path.touch(exist_ok=True)
	module_name: str = name
	spec: ModuleSpec | None = util.spec_from_file_location(module_name, path)
	assert spec and spec.loader
	module: ModuleType = util.module_from_spec(spec)
	sys.path.insert(0, str(path.parent))
	# try:
		# spec.loader.exec_module(module)
	# finally:
		# Clean up sys.path to prevent cluttering global imports
		# sys.path.pop(0)
	spec.loader.exec_module(module)
	return module

def load_config(module_name: str = "config", attribute: str = "CONFIG") -> Any:
	"""
	Loads config from $XDG_CONFIG_HOME/felt/config.py
	Creates it if not there already.
	"""
	module: ModuleType = import_config_module(module_name)
	return getattr(module, attribute, None)

def get_css_file() -> str:
	style_dir: Path = CONFIG_PATH/"style"
	style_dir.mkdir(exist_ok=True, parents=True)
	if not (css:=style_dir/"main.css").exists():
		with open(css, "w") as f:
			f.write("")
	return str(css)

# This imports all modules declared in `PARAMS` dict.
# You should be able to import your modules as if you were using
# `from module_name import main`, where `main` is the function that will be
# executed with the params given.

def main() -> None:
	CONFIG_PATH.mkdir(exist_ok=True, parents=True)
	CONFIG: dict[str, Any] = load_config() or {}
	app: Application = Application("shell")
	for module_name, module_config in CONFIG.items():
		func: Any | None = load_config(module_name, attribute="main")
		if not callable(func):
			raise ValueError(f"`from {module_name}.main import main` failed.")
		app.add_window(func(**module_config))
	app.set_stylesheet_from_file(get_css_file())
	app.run()

if __name__ == "__main__": main()

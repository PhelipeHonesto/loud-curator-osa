import importlib, sys
_backend = importlib.import_module('backend.agents')
sys.modules[__name__] = _backend

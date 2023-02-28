from __future__ import annotations

from typing import List, Dict, Any, NoReturn, Optional

from plank import logger
from plank.context import Context
from plank.service import ServiceManager


class Plugin:
    """
    Abstract class to define what should be imp.
    """
    __inherited__: List[Plugin] = []

    class Delegate:
        def application_did_launch(self, plugin: Plugin, launch_options: Dict[str, Any]):
            pass

        def plugin_did_install(self, plugin: Plugin):
            pass

        def plugin_did_discover(self, plugin: Plugin):
            pass

        def plugin_did_load(self, plugin: Plugin):
            pass

        def plugin_did_unload(self, plugin: Plugin):
            pass

    @classmethod
    def discover(cls, *args, **kwargs) -> List[Plugin]:
        raise NotImplementedError(f"The name of Plugin({cls.__name__}) did not implement.")

    @classmethod
    def construct_parameters(cls, plugin_info: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError(f"The construct_parameters method of Plugin({cls.__name__}) did not implement.")

    @classmethod
    def installed(cls) -> List[Plugin]:
        context = Context.standard(cls.__qualname__)
        return list(context.values())

    @classmethod
    def plugin(cls, name: str) -> Plugin:
        context = Context.standard(cls.__qualname__)
        if name not in context.keys():
            raise KeyError(f"Any plugin can be found with name: {name}, by type of plugin: {cls.__qualname__}.")
        return context.get(key=name)


    @property
    def services(self)->ServiceManager:
        manager_scope = f"{self.__class__.__name__}.{self.name}"
        return ServiceManager.shared(scope=manager_scope)

    @classmethod
    def current(cls) -> Optional[Plugin]:
        for subclass in Plugin.__inherited__:
            plugin = subclass.current()
            if plugin is not None:
                return plugin
        return None

    def __init_subclass__(cls, **kwargs):
        if cls not in Plugin.__inherited__:
            Plugin.__inherited__.append(cls)

    @property
    def name(self) -> str:
        return self._name()

    @property
    def delegate(self) -> Plugin.Delegate:
        return self._delegate()

    def _name(self) -> str:
        raise NotImplementedError(f"The name of Plugin({self.__class__.__name__}) not imp.")

    def _delegate(self) -> Plugin.Delegate:
        raise NotImplementedError(f"The delegate of Plugin({self.__class__.__name__}) not imp.")

    def install(self, context: Context, *args, **kwargs):
        context.set(key=self._name(), value=self)
        self.did_install()
        logger.info(f"[Plugin] {self.name} installed.")

    def _loading(self) -> NoReturn:
        pass

    def load(self) -> NoReturn:
        self._loading()
        self.delegate.plugin_did_load(plugin=self)
        logger.debug(f"[Plugin] {self.name} loaded.")

    def unload(self):
        pass

    def did_install(self):
        pass

    def did_discover(self):
        pass

from typing import Dict, Union, Type
_COMMAND_ROUTES: Dict[str, str] = {}
_FALLBACK_ROUTE: str = None
def route(command: str, controller: Union[str, Type]):
    if isinstance(controller, str):
        if not controller.startswith('app.'):
            controller = f"app.Bot.Controllers.{controller.replace('/', '.')}"
    _COMMAND_ROUTES[command.lower()] = controller
def fallback(controller: Union[str, Type]):
    global _FALLBACK_ROUTE
    if isinstance(controller, str):
        if not controller.startswith('app.'):
            controller = f"app.Bot.Controllers.{controller.replace('/', '.')}"
    _FALLBACK_ROUTE = controller
def get_command_routes() -> Dict[str, str]:
    return _COMMAND_ROUTES.copy()
def get_fallback_route() -> str:
    return _FALLBACK_ROUTE
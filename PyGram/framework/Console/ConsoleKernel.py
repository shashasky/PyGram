# framework/console/ConsoleKernel.py
import sys
from pathlib import Path
from typing import List, Dict, Callable
import importlib
_USE_COLOR = False
_Fore_GREEN = ""
_Fore_RED = ""
_Style_RESET = ""
try:
    import colorama
    colorama.init()
    _USE_COLOR = True
    _Fore_GREEN = colorama.Fore.GREEN
    _Fore_RED = colorama.Fore.RED
    _Style_RESET = colorama.Style.RESET_ALL
except ImportError:
    pass
_CONSOLE_COMMANDS: Dict[str, Callable] = {}
def _camel_to_kebab(camel_str):
    result = []
    for i, char in enumerate(camel_str):
        if char.isupper() and i > 0:
            result.append('-')
        result.append(char.lower())
    return ''.join(result)
def _auto_discover_framework_commands():
    commands_dir = Path("framework/Console/Commands")
    if not commands_dir.exists():
        return
    for py_file in commands_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        filename = py_file.stem
        try:
            module_path = f"framework.Console.Commands.{filename}"
            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                if attr_name.startswith('handle_'):
                    handler_func = getattr(module, attr_name)
                    if callable(handler_func):
                        command_name = attr_name[7:].replace('_', ':')
                        _CONSOLE_COMMANDS[command_name] = handler_func
        except Exception:
            continue
def _auto_discover_app_commands():
    commands_dir = Path("app/Bot/Commands")
    if not commands_dir.exists():
        return
    for py_file in commands_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        filename = py_file.stem
        if not filename.endswith('Command'):
            continue
        command_name = _camel_to_kebab(filename[:-7])
        try:
            module_path = f"app.Bot.Commands.{filename}"
            module = importlib.import_module(module_path)
            if hasattr(module, 'handle') and callable(module.handle):
                _CONSOLE_COMMANDS[command_name] = module.handle
        except Exception:
            continue
def register_console_command(name: str, handler: Callable) -> None:
    _CONSOLE_COMMANDS[name] = handler
def handle_console(argv: List[str]) -> int:
    if not _CONSOLE_COMMANDS:
        try:
            import routes.cli
        except ImportError:
            pass
        _auto_discover_framework_commands()
        _auto_discover_app_commands()
    if not argv:
        _show_usage()
        return 1
    command_name = argv[0]
    handler = _CONSOLE_COMMANDS.get(command_name)
    if handler is None:
        _write_error(f"未找到命令 '{command_name}'")
        return 1
    try:
        result = handler(argv[1:])
        if result is not None:
            _write_success(str(result))
        return 0
    except Exception as e:
        _write_error(str(e))
        return 1
def _write_success(message: str):
    icon = "✔" if _USE_COLOR else "[OK]"
    color = _Fore_GREEN if _USE_COLOR else ""
    reset = _Style_RESET if _USE_COLOR else ""
    print(f"{color}{icon} {message}{reset}")
def _write_error(message: str):
    icon = "✘" if _USE_COLOR else "[ERROR]"
    color = _Fore_RED if _USE_COLOR else ""
    reset = _Style_RESET if _USE_COLOR else ""
    print(f"{color}{icon} {message}{reset}", file=sys.stderr)
def _show_usage():
    print("用法：./pygram <命令> [选项]")
    if _CONSOLE_COMMANDS:
        print("可用命令：")
        for name in sorted(_CONSOLE_COMMANDS.keys()):
            print(f"  {name}")
    else:
        print("暂无可用命令")
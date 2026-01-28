# bootstrap/Foundation/RouteValidator.py
import importlib
import importlib.util


def validate_routes(project_root):
    routes_file = project_root / "routes" / "telegram.py"
    if not routes_file.exists():
        return

    spec = importlib.util.spec_from_file_location("telegram_routes", routes_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    from framework.Bot.routing.Router import get_command_routes
    routes = get_command_routes()

    if not routes:
        return

    for cmd, ctrl_path in routes.items():
        module_name = ctrl_path
        class_name = ctrl_path.split('.')[-1]
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        instance = cls(bot=None)

        if not hasattr(instance, 'commands'):
            raise ValueError(f"控制器 {ctrl_path} 缺少 commands 声明")

        declared_commands = [c.lower() for c in instance.commands]
        if cmd not in declared_commands:
            raise ValueError(
                f"路由冲突: 注册命令 '{cmd}' 但控制器 {ctrl_path} 的 commands 中未包含它"
            )

    # 自动加载其他路由文件
    routes_dir = project_root / "routes"
    if routes_dir.exists():
        for route_file in routes_dir.glob("*.py"):
            if route_file.name != "__init__.py":
                importlib.import_module(f"routes.{route_file.stem}")
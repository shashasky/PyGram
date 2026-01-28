import re
from pathlib import Path
def _read_lines(file_path):
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f]
    return []
def _write_lines(file_path, lines, route_line):
    if route_line in lines:
        return
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
        f.write(route_line + '\n')
def handle_make_controller(args):
    if not args:
        raise ValueError("用法：make:controller <名称> [--command=<命令名>] [--fallback]")
    path_spec = args[0].strip()
    command_name = None
    is_fallback = False
    i = 1
    while i < len(args):
        arg = args[i]
        if arg == '--command':
            if i + 1 >= len(args):
                raise ValueError("--command 后必须指定命令名")
            command_name = args[i + 1].strip().lower()
            i += 2
        elif arg.startswith('--command='):
            parts = arg.split('=', 1)
            if len(parts) != 2 or not parts[1].strip():
                raise ValueError("--command= 后必须指定命令名")
            command_name = parts[1].strip().lower()
            i += 1
        elif arg == '--fallback':
            is_fallback = True
            i += 1
        else:
            raise ValueError(f"未知参数：'{arg}'，支持 --command 或 --fallback")
    if command_name and is_fallback:
        raise ValueError("不能同时指定 --command 和 --fallback")
    if not path_spec:
        raise ValueError("控制器名称不能为空")
    path_spec = path_spec.replace('\\', '/')
    if path_spec.startswith('/') or '..' in path_spec:
        raise ValueError("控制器路径不能包含绝对路径或 '..'")
    parts = [p for p in path_spec.split('/') if p]
    if not parts:
        raise ValueError("无效的控制器路径")
    class_name = parts[-1]
    sub_dirs = parts[:-1]
    if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', class_name):
        raise ValueError("控制器类名必须以大写字母开头，且仅包含字母、数字、下划线")
    base_dir = Path("app") / "Bot" / "Controllers"
    target_file = base_dir.joinpath(*sub_dirs) / f"{class_name}.py"
    try:
        target_file.resolve().relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError("只能在 app/Bot/Controllers/ 目录内创建控制器")
    target_file.parent.mkdir(parents=True, exist_ok=True)
    if target_file.exists():
        raise ValueError(f"控制器 '{target_file}' 已存在")
    if is_fallback:
        content = f'''class {class_name}:
    def handle(self, update: dict, mode: str) -> str:
        text = update['message']['text']
        # TODO: 实现你的 AI 或文本处理逻辑
        return "回复: " + text
'''
        route_line = f"fallback('{class_name}')"
    else:
        commands_list = f"['{command_name}']" if command_name else "[]"
        content = f'''class {class_name}:
    commands = {commands_list}
    def handle(self, update: dict, command_name: str) -> str:
        return "Hello from {class_name}!"
'''
        if command_name:
            controller_path = ".".join(sub_dirs + [class_name]) if sub_dirs else class_name
            route_line = f"route('{command_name}', '{controller_path}')"
        else:
            route_line = None
    target_file.write_text(content, encoding='utf-8')
    if route_line:
        routes_file = Path("routes") / "telegram.py"
        routes_file.parent.mkdir(exist_ok=True)
        lines = _read_lines(routes_file)
        import_line = "from framework.Bot import route, fallback"
        has_import = any(import_line in line for line in lines)
        if not has_import:
            route_import = any("from framework.Bot import" in line and "route" in line for line in lines)
            fallback_import = any("from framework.Bot import" in line and "fallback" in line for line in lines)
            if route_import and fallback_import:
                pass
            elif route_import:
                for i, line in enumerate(lines):
                    if "from framework.Bot import" in line and "route" in line:
                        lines[i] = line.rstrip(' \n') + ", fallback"
                        break
            elif fallback_import:
                for i, line in enumerate(lines):
                    if "from framework.Bot import" in line and "fallback" in line:
                        lines[i] = "from framework.Bot import route, fallback"
                        break
            else:
                lines.insert(0, import_line)
        _write_lines(routes_file, lines, route_line)
    return str(target_file)
def handle_make_command(args):
    if not args:
        raise ValueError("用法：make:command <命令名>")
    command_name = args[0].strip()
    if not command_name:
        raise ValueError("命令名称不能为空")
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', command_name):
        raise ValueError("命令名必须以字母开头，且仅包含字母、数字、连字符、下划线")
    class_name = ''.join(word.capitalize() for word in re.split(r'[-_]', command_name)) + 'Command'
    target_file = Path("app") / "Bot" / "Commands" / f"{class_name}.py"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    if target_file.exists():
        raise ValueError(f"CLI 命令 '{command_name}' 已存在")
    content = f'''def handle(args):
    return "{command_name} 命令已创建，请编辑此文件添加具体逻辑！"
'''
    target_file.write_text(content, encoding='utf-8')
    return str(target_file)
def handle_cache_clear(args):
    import shutil
    cluster_dir = Path("storage/framework/cluster")
    if cluster_dir.exists():
        shutil.rmtree(cluster_dir)
    cluster_dir.mkdir(parents=True, exist_ok=True)
    session_dir = Path("storage/framework/sessions")
    if session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    return "框架缓存已清理"
# framework/Error/Handler.py
import sys
import asyncio
import traceback
import inspect
from datetime import datetime
from pathlib import Path
import re
class GlobalErrorHandler:
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'underline': '\033[4m'
    }
    def __init__(self):
        self.log_dir = Path("storage/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "error.log"
        self._setup_handlers()
    def _setup_handlers(self):
        sys.excepthook = self._sync_handler
        loop = asyncio._get_running_loop()
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.set_exception_handler(self._async_handler)
    def _write_log(self, context_type: str, error: str, tb_lines: list = None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{context_type}] {error}\n")
            if tb_lines:
                f.writelines(tb_lines)
            f.write('=' * 100 + '\n')
    def _colorize(self, text: str, color: str) -> str:
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    def _analyze_error_context(self, exc_value, exc_traceback):
        error_str = str(exc_value)
        suggestions = []
        if isinstance(exc_value, ModuleNotFoundError):
            module_name = error_str.replace("No module named '", "").rstrip("'")
            if module_name.startswith('app.Bot.Controllers.'):
                controller_name = module_name.split('.')[-1]
                suggestions.append(f"• 检查控制器文件是否存在: app/Bot/Controllers/{controller_name}.py")
                suggestions.append(f"• 确认文件名与类名一致: class {controller_name}(BaseController)")
            elif 'framework' in module_name:
                suggestions.append(f"• 检查框架模块路径是否正确: {module_name}")
            else:
                suggestions.append(f"• 模块 '{module_name}' 未安装或路径错误")
        elif isinstance(exc_value, ValueError):
            if "路由冲突" in error_str:
                match = re.search(r"注册命令 '([^']+)' 但控制器 ([^ ]+) 的 commands 中未包含它", error_str)
                if match:
                    command = match.group(1)
                    controller = match.group(2)
                    suggestions.append(f"• 在 {controller} 中添加: commands = ['{command}']")
                    suggestions.append(f"• 确保 commands 列表包含所有注册的命令")
            elif "缺少 commands 声明" in error_str:
                match = re.search(r"控制器 ([^ ]+) 缺少 commands 声明", error_str)
                if match:
                    controller = match.group(1)
                    suggestions.append(f"• 在 {controller} 中添加 commands 属性")
                    suggestions.append(f"• 示例: commands = ['your_command']")
        elif isinstance(exc_value, AttributeError):
            if "has no attribute 'commands'" in error_str:
                suggestions.append("• 控制器类必须继承 BaseController")
                suggestions.append("• 确保没有重写 __init__ 而忘记调用 super().__init__()")
        elif isinstance(exc_value, ImportError):
            suggestions.append("• 检查导入语句是否正确")
            suggestions.append("• 确认模块路径和文件名拼写")
        return suggestions
    def _get_code_context(self, filename, lineno, context_lines=3):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            start = max(0, lineno - context_lines - 1)
            end = min(len(lines), lineno + context_lines)
            context = []
            for i in range(start, end):
                line_num = i + 1
                line_content = lines[i].rstrip('\n')
                if line_num == lineno:
                    context.append(
                        f"{self._colorize(f'{line_num:4d}', 'bright_red')} > {self._colorize(line_content, 'bright_red')}")
                else:
                    context.append(f"{self._colorize(f'{line_num:4d}', 'bright_white')} | {line_content}")
            return context
        except (FileNotFoundError, OSError):
            return [f"{self._colorize(f'{lineno:4d}', 'bright_white')} | <无法读取文件内容>"]
    def _format_error_output(self, context_type: str, message: str, exc_info=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if context_type == "SYNC":
            type_color = "bright_red"
            border_color = "red"
        else:
            type_color = "bright_magenta"
            border_color = "magenta"
        title_text = f" FRAMEWORK ERROR [{context_type}] "
        border_line = "═" * (len(title_text) + 2)
        output = []
        output.append("")
        output.append(self._colorize(border_line, border_color))
        output.append(self._colorize(title_text, type_color))
        output.append(self._colorize(border_line, border_color))
        output.append(f"{self._colorize('Time:', 'bright_cyan')} {timestamp}")
        output.append(f"{self._colorize('Error:', 'bright_red')} {type(exc_info).__name__}")
        output.append(f"{self._colorize('Message:', 'bright_yellow')} {message}")
        output.append("")
        if exc_info:
            suggestions = self._analyze_error_context(exc_info, exc_info.__traceback__)
            if suggestions:
                output.append(self._colorize("Suggested Solutions:", "bright_green"))
                for suggestion in suggestions:
                    output.append(f"  {suggestion}")
                output.append("")
        if exc_info:
            output.append(self._colorize("Stack Trace:", "bright_white"))
            tb = exc_info.__traceback__
            while tb is not None:
                filename = tb.tb_frame.f_code.co_filename
                lineno = tb.tb_lineno
                func_name = tb.tb_frame.f_code.co_name
                output.append(
                    f"{self._colorize('File', 'bright_blue')} \"{self._colorize(filename, 'cyan')}\", {self._colorize('line', 'bright_blue')} {lineno}, {self._colorize('in', 'bright_blue')} {func_name}")
                code_context = self._get_code_context(filename, lineno)
                output.extend([f"    {line}" for line in code_context])
                output.append("")
                tb = tb.tb_next
        output.append(self._colorize(border_line, border_color))
        output.append("")
        return "\n".join(output)
    def _sync_handler(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error_msg = str(exc_value)
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        formatted_output = self._format_error_output("SYNC", error_msg, exc_value)
        print(formatted_output, file=sys.stderr)
        self._write_log("SYNC", error_msg, tb_lines)
    def _async_handler(self, loop, context):
        exception = context.get('exception')
        message = context.get('message', 'Unhandled async exception')
        if exception:
            error_msg = str(exception)
            tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
            formatted_output = self._format_error_output("ASYNC", message, exception)
            print(formatted_output, file=sys.stderr)
            self._write_log("ASYNC", error_msg, tb_lines)
        else:
            formatted_output = self._format_error_output("ASYNC", message)
            print(formatted_output, file=sys.stderr)
            self._write_log("ASYNC", message)
_global_handler = None
def enable_global_error_handler():
    global _global_handler
    if _global_handler is None:
        _global_handler = GlobalErrorHandler()
    return _global_handler
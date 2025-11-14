from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.shell import BashLexer
from typing import Dict, List, Optional
import shlex
# 定义颜色和样式
style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})
class CommandCompleter(Completer):
    def __init__(self, commands: Dict):
        self.commands = commands  # 命令结构树
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        parts = shlex.split(text)
        current_cmd = self.commands
        last_part = parts[-1] if parts else ''
        # 遍历命令层级结构
        for part in parts[:-1]:
            if part in current_cmd and 'sub' in current_cmd[part]:
                current_cmd = current_cmd[part]['sub']
            else:
                return
        # 生成补全建议
        for cmd in current_cmd:
            if cmd.startswith(last_part):
                display = current_cmd[cmd].get('display', cmd)
                help_text = current_cmd[cmd].get('help', '')
                yield Completion(
                    cmd,
                    start_position=-len(last_part),
                    display=f"{display} \u200b({help_text})",
                    style="fg:ansigreen"
                )
class Shell:
    def __init__(self):
        # 定义命令结构（支持多级命令和帮助信息）
        self.commands = {
            'system': {
                'help': '系统管理',
                'sub': {
                    'start': {
                        'help': '启动服务',
                        'exec': self.system_start,
                        'args': ['service_name']
                    },
                    'stop': {
                        'help': '停止服务',
                        'exec': self.system_stop
                    },
                    'restart': {
                        'help': '重启服务',
                        'exec': self.system_restart
                    }
                }
            },
            'exit': {
                'help': '退出 Shell',
                'exec': self.exit_shell
            }
        }
        self.session = PromptSession(
            lexer=PygmentsLexer(BashLexer),
            completer=CommandCompleter(self.commands),
            style=style
        )
        self.running = True
    def system_start(self, args: List[str]):
        if len(args) < 1:
            print("Error: 需要指定服务名称")
            return
        print(f"[+] 启动服务: {args[0]}")
    def system_stop(self, args: List[str]):
        print("[+] 停止所有服务")

    def system_restart(self, args: List[str]):
        print("[+] 重启所有服务")

    def exit_shell(self, args: List[str]):
        print("退出 Shell...")
        self.running = False
    def parse_command(self, input_text: str):
        parts = shlex.split(input_text)
        if not parts:
            return
        current_cmd = self.commands
        cmd_chain = []
        for part in parts:
            if part in current_cmd:
                cmd_chain.append(part)
                if 'sub' in current_cmd[part]:
                    current_cmd = current_cmd[part]['sub']
                else:
                    break
            else:
                break
        # 查找对应的执行函数
        target = self.commands
        for cmd in cmd_chain:
            target = target[cmd]
            if 'sub' in target:
                target = target['sub']
        if 'exec' in target:
            args = parts[len(cmd_chain):]
            target['exec'](args)
        else:
            print(f"未知命令: {' '.join(cmd_chain)}")
    def run(self):
        print("欢迎使用自定义 Shell（输入 'exit' 退出）")
        while self.running:
            try:
                text = self.session.prompt('>>> ')
                self.parse_command(text)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
if __name__ == "__main__":
    shell = Shell()
    shell.run()
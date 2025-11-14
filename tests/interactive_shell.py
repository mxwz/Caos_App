import cmd
import os
import time

import readline
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

class MyShell(cmd.Cmd):
    intro = f"{Fore.GREEN}欢迎使用MyShell交互式环境。输入help或? 查看命令列表。\n"
    prompt = f"{Fore.CYAN}(myshell) {Style.RESET_ALL}"

    cwd = os.getcwd()  # 设置当前工作目录

    commands = {
        'system': {
            'help': '系统管理',
            'sub': {
                'start': {
                    'help': '启动服务',
                    'exec': 'system_start',
                    'args': ['service_name']
                },
                'stop': {
                    'help': '停止服务',
                    'exec': 'system_stop'
                }
            }
        },
        'exit': {
            'help': '退出 Shell',
            'exec': 'exit_shell'
        },
        'ls': {
            'help': '列出当前目录下的文件',
            'exec': 'ls',
            'args': ['directory']
        }
    }

    def do_ls(self, line):
        """列出当前目录下的文件和目录"""
        args = line.split()
        directory = self.cwd if not args else args[0]

        try:
            entries = os.listdir(directory)
            for entry in entries:
                path = os.path.join(directory, entry)
                if os.path.isdir(path):
                    print(f"{Fore.BLUE}{entry}{Style.RESET_ALL}", end='\t')
                else:
                    print(entry, end='\t')
            print()  # 换行
        except FileNotFoundError:
            print(f"{Fore.RED}目录 '{directory}' 不存在{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}没有权限访问目录 '{directory}'{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")

    def help_ls(self):
        """显示ls命令的帮助信息"""
        print(f"{Fore.GREEN}ls命令用于列出当前目录下的文件和目录。\n"
              f"用法: ls [目录]\n"
              f"示例: ls\n"
              f"       ls /path/to/directory{Style.RESET_ALL}")



    def do_hello(self, line):
        """简单的问候命令"""
        print(f"{Fore.YELLOW}你好！{Style.RESET_ALL}")

    def do_printflow(self, line):
        """流式打印字符串"""
        args = line.split()
        if '-h' in args or '--help' in args:
            self.help_printflow()
            return

        if not args:
            print(f"{Fore.RED}缺少字符串参数{Style.RESET_ALL}")
            return

        for char in ' '.join(args):
            print(char, end='', flush=True)
            time.sleep(0.1)
        print()  # 换行

    def help_printflow(self):
        """显示printflow命令的帮助信息"""
        print(f"{Fore.GREEN}printflow命令用于流式打印字符串。\n"
              f"用法: printflow <字符串>\n"
              f"示例: printflow Hello, World!{Style.RESET_ALL}")

    def system_start(self, service_name):
        """启动服务"""
        print(f"{Fore.GREEN}正在启动服务: {service_name}{Style.RESET_ALL}")

    def system_stop(self):
        """停止服务"""
        print(f"{Fore.RED}正在停止服务{Style.RESET_ALL}")

    def do_system(self, line):
        """系统管理"""
        args = line.split()
        if '-h' in args or '--help' in args:
            self.help_system()
            return

        if not args:
            print(f"{Fore.RED}缺少子命令{Style.RESET_ALL}")
            return

        subcommand = args[0]
        if subcommand in self.commands['system']['sub']:
            subcommand_info = self.commands['system']['sub'][subcommand]
            if subcommand_info['exec'] == 'system_start':
                if len(args) < 2:
                    print(f"{Fore.RED}缺少服务名称{Style.RESET_ALL}")
                    return
                self.system_start(args[1])
            elif subcommand_info['exec'] == 'system_stop':
                self.system_stop()
            else:
                print(f"{Fore.RED}未知子命令: {subcommand}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}未知子命令: {subcommand}{Style.RESET_ALL}")

    def help_system(self):
        """显示system命令的帮助信息"""
        print(f"{Fore.GREEN}system命令用于系统管理。\n"
              f"用法: system <子命令>\n"
              f"子命令:\n"
              f"  start <服务名称> - 启动服务\n"
              f"  stop - 停止服务{Style.RESET_ALL}")

    def do_exit(self, line):
        """退出shell"""
        args = line.split()
        if '-h' in args or '--help' in args:
            self.help_exit()
            return

        print(f"{Fore.RED}再见！{Style.RESET_ALL}")
        return True

    def help_exit(self):
        """显示exit命令的帮助信息"""
        print(f"{Fore.GREEN}exit命令用于退出shell。\n"
              f"用法: exit{Style.RESET_ALL}")

    def do_EOF(self, line):
        """退出shell"""
        return self.do_exit(line)

    def emptyline(self):
        """忽略空行"""
        pass

    def default(self, line):
        print(f"{Fore.RED}未知命令: {line}{Style.RESET_ALL}")

if __name__ == '__main__':
    # 启用自动补全和历史记录
    readline.parse_and_bind("tab: complete")
    readline.read_history_file("myshell_history.txt")
    try:
        MyShell().cmdloop()
    finally:
        readline.write_history_file("myshell_history.txt")
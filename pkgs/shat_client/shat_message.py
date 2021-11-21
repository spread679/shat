from colorama import init, Fore, Back, Style
import datetime


# @description: print a positive result
# @param message: the message to print
def print_positive_message(message):
    return f"{Style.BRIGHT}{Fore.GREEN}[+] {datetime.datetime.now()} - {message}{Style.RESET_ALL}"


# @description: print a negative result
# @param message: the message to print
def print_negative_message(message):
    return f"{Style.BRIGHT}{Fore.RED}[-] {datetime.datetime.now()} - {message}{Style.RESET_ALL}"


# @description: print a negative result
# @param message: the message to print
def print_answer_message(message):
    return f"{Style.BRIGHT}{Fore.YELLOW}[?] {datetime.datetime.now()} - {message}{Style.RESET_ALL}"


# @description: print the current user
# @param username: the username to print
def print_current_user(username):
    return f"{Style.BRIGHT}{Fore.CYAN}{username} >> {Style.RESET_ALL}"


# @description: print the connected user
# @param username: the username to print
# @param message: the message to print
def print_connected_user(username):
    return f"{Style.BRIGHT}{Fore.MAGENTA}[{datetime.datetime.now()}]\n{username} >> {Style.RESET_ALL}"

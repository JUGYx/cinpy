import sys
from rich.console import Console
import sys

console = Console()

def welcome():
    console.print("\n****************************", style="#dd6777")
    console.print("*         Cinemana         *", style="#dd6777")
    console.print("****************************", style="#dd6777")
    console.print("\n[!] This is not an official client.", style="#dd6777")
    console.print("[*] Ctrl-C to quit.\n[*] Requires mpv to work.\n", style="#e6ce9d")

def clear():
    console.clear()

def msg(text,style):
    console.print(f"\n{text}\n", style=style)

def die(c=0,text="Bye..."):
    msg(text,"#dd6777")
    sys.exit(c)



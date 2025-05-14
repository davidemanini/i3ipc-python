#!/usr/bin/python3

import i3ipc
from argparse import ArgumentParser




def switch_to_workspace(connection, e):
#    print(e.ipc_data["current"]["num"])
    connection.command("workspace "+str(e.ipc_data["current"]["num"]))


if __name__ == '__main__':
    ArgumentParser(prog="urgent_desktop.py",
                   description="""
                   Automatically switch to a workspace containing a window
                   that changed its status to urgent.
                   """).parse_args()
    
    i3 = i3ipc.Connection()
    i3.on(i3ipc.Event.WORKSPACE_URGENT, switch_to_workspace)
    i3.main()

#!/usr/bin/python3

import i3ipc
import subprocess
import psutil
from argparse import ArgumentParser, RawDescriptionHelpFormatter


import sys


INFO_TO_BE_COPIED = ["id", "name", "pid"]

def retrive_win_info(win):
    info = {i: win[i] for i in INFO_TO_BE_COPIED}
    info["psname"]=psutil.Process(win["pid"]).name()
    return info

class App:

    def _send_notify(self, win):
        win_info = retrive_win_info(win)
        summary = self.format_summary.format(**win_info)
        body = self.format_body.format(**win_info)
        return subprocess.Popen(self.notify_args + [summary, body])

    def _new_window_event(self):
        if self.wait_window_name:
            def new_window(connection, e):
                win = e.ipc_data["container"]
                if win["shell"] == "xwayland":
                    if win["name"]:
                        self._send_notify(win)
                    else:
                        self.unamed_windows.append(win["id"])
            return new_window
        else:
            def new_window(connection, e):
                win = e.ipc_data["container"]
                if win["shell"] == "xwayland":
                    self._send_notify(win)
            return new_window


    def _title_window_event(self):
        def title_window(connection, e):
            win = e.ipc_data["container"]
            try:
                self.unamed_windows.remove(win["id"])
                self._send_notify(win)
            except ValueError:
                pass
        return title_window


    def __init__(self, format_summary, format_body, wait_window_name=False,
                 expire_time=None,
                 icon=None, app_name=None):
        
        self.format_body = format_body
        self.format_summary = format_summary

        
        self.notify_args = ["notify-send"]
        if app_name:
            self.notify_args += ["-a", app_name]
        if icon:
            self.notify_args += ["-i", icon]
        if expire_time:
            self.notify_args += ["-t", str(expire_time)]

        self.i3 = i3ipc.Connection()

        self.wait_window_name=wait_window_name
        if wait_window_name:
            self.unamed_windows=[]        
            self.i3.on(i3ipc.Event.WINDOW_TITLE, self._title_window_event())

        self.i3.on(i3ipc.Event.WINDOW_NEW, self._new_window_event())

        
    def run(self):
        self.i3.main()


if __name__ == '__main__':
    parser = ArgumentParser(prog="xwayland_notify.py",
                            description="""Sends a notification each time a X11 application starts.""",
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog='''
Formatting strings substitute '{key}' with the correpsonging value.
Supported keys are:

  id: the window id
  name: the window name
  pid: the PID
  psname: the process name                          
''')

    parser.add_argument("-i", "--icon", default=None, type=str,
                        help='Set the icon for the notification')
    parser.add_argument("-t", "--expire-time", default=None, type=int,
                        help='The duration, in milliseconds')
    parser.add_argument("-s", "--summary", default="New X11 application",
                        type=str,
                        help='Format the summary of notification')
    parser.add_argument("-b", "--body", default="process name: {psname}",
                        type=str,
                        help='Format the body of notification')
    parser.add_argument("-n", "--wait-for-name", default=False,
                        action="store_true",
                        help='Wait that a window name become non-null')


    arg = parser.parse_args()
    app =App(icon=arg.icon, format_summary=arg.summary,
             format_body=arg.body, app_name=sys.argv[0],
             expire_time=arg.expire_time,
             wait_window_name=arg.wait_for_name)
    app.run()

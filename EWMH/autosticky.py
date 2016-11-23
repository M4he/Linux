from ewmh import EWMH
import signal
import time
import sys
ewmh = EWMH()

# PYTHON MODULE REQUIREMENTS
#
# - 'ewmh'
# - 'python-xlib' (ewmh dependency)

# PREFACE
#
# I usually use second screens/monitors as a depot for windows that will
# act as some kind of reference point (e.g. docs) or something similar
# during my work. Thus I like those windows being 'sticky' so that they
# are not affected by workspace switching, i.e. the second screen being
# its own separate (sticky) workspace.
#
# This is usually only possible if the WM supports such feature.
# While Mutter (Gnome 3) does, Xfwm (Xfce) for instance does not.
# To help unsupporting but EWMH-compliant WMs, this script keeps track of
# window positions and automatically stickies windows moved to the
# external screen.

# RESTRICTIONS
#
# - only supports one external screen
# - only supports external screen located right of the primary one
# - currently has no exclusion list for windows to prevent specific
#   windows from getting stickied/unstickied

# USAGE
#
# Simply adjust the values below. The STICKY_X_THRESH should be the
# horizontal resolution of your left screen. Any window that has at least
# two thirds of its content beyond this barrier will become sticky if
# the right screen is set to be sticky for instance.
#
# Use LEFT_SCREEN_IS_STICKY to toggle whether the windows of the left
# screen (= True) or those of the right screen (= False) should be
# stickied.
#
# Finally run the script via python:
#   $ python autosticky.py


# config values
REPARENTING_WM = True
LEFT_SCREEN_IS_STICKY = True
STICKY_X_THRESH = 1440
CHECK_INTERVAL_SECONDS = .5

_WINDOW_POSITIONS = {}
_LAST_WINDOWS = {}  # keeps track of recent windows for garbage collection


def get_window_geometry(win):
    if REPARENTING_WM:
        attr = win.query_tree().parent.get_geometry()._data
    else:
        attr = win.get_geometry()._data
    return attr['x'], attr['y'], attr['width'], attr['height']


def get_window_geometry_hash(x, y, w, h):
    return "%s:%s:%s:%s" % (x, y, w, h)


def is_window_to_be_stickied(x, y, w, h):
    if LEFT_SCREEN_IS_STICKY:
        ref_point = (x + round(2*w/3), y + round(2*h/3))
        return ref_point[0] < STICKY_X_THRESH
    else:
        ref_point = (x + round(w/3), y + round(h/3))
        return ref_point[0] > STICKY_X_THRESH


def set_window_sticky(win, sticky=True):
    action = sticky and 1 or 0
    ewmh.setWmState(win, action, '_NET_WM_STATE_STICKY')


def initialize_windows():
    windows = ewmh.getClientList()
    for win in windows:
        win_id = win.__hash__()
        win_pos = get_window_geometry(win)

        if is_window_to_be_stickied(*win_pos):
            set_window_sticky(win)

        _WINDOW_POSITIONS[win_id] = win_pos
        _LAST_WINDOWS[win_id] = True
    ewmh.display.flush()


def reset_window_tracker():
    for win_id in _LAST_WINDOWS:
        _LAST_WINDOWS[win_id] = False


def iterate_windows():
    reset_window_tracker()
    windows = ewmh.getClientList()
    for win in windows:
        win_id = win.__hash__()
        try:
            win_pos = get_window_geometry(win)
        except:
            continue
        _LAST_WINDOWS[win_id] = True
        if win_id in _WINDOW_POSITIONS:
            last_pos = _WINDOW_POSITIONS[win_id]
            if win_pos != last_pos:
                new_state = is_window_to_be_stickied(*win_pos)
                last_state = is_window_to_be_stickied(*last_pos)
                if new_state != last_state:
                    set_window_sticky(win, new_state)
                _WINDOW_POSITIONS[win_id] = win_pos
        else:
            # new window
            if is_window_to_be_stickied(*win_pos):
                set_window_sticky(win, True)
            _WINDOW_POSITIONS[win_id] = win_pos
    ewmh.display.flush()

    # garbage collect any missing windows
    lw_copy = dict(_LAST_WINDOWS)
    for win_id in lw_copy:
        if not lw_copy[win_id]:
            _LAST_WINDOWS.pop(win_id)
            _WINDOW_POSITIONS.pop(win_id)


def unsticky_all_windows():
    windows = ewmh.getClientList()
    for win in windows:
        set_window_sticky(win, sticky=False)
    ewmh.display.flush()


def signal_term_handler(signal, frame):
    unsticky_all_windows()
    sys.exit(0)


def run():
    signal.signal(signal.SIGTERM, signal_term_handler)
    initialize_windows()
    while True:
        iterate_windows()
        time.sleep(CHECK_INTERVAL_SECONDS)

run()

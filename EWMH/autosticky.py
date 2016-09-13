from ewmh import EWMH
import time
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
# - might build up memory, because the window list has currently no
#   garbage collection
# - currently has no exclusion list for windows to prevent specific
#   windows from getting stickied/unstickied

# USAGE
#
# Simply adjust the values below. The STICKY_X_THRESH should be the
# horizontal resolution of your left screen. Any window that has at least
# two thirds of its content beyond this barrier will become sticky.
#
# Finally run the script via python:
#   $ python autosticky.py


# config values
REPARENTING_WM = True
STICKY_X_THRESH = 1440
CHECK_INTERVAL_SECONDS = .5

_WINDOW_POSITIONS = {}


def get_window_geometry(win):
    if REPARENTING_WM:
        attr = win.query_tree().parent.get_geometry()._data
    else:
        attr = win.get_geometry()._data
    return attr['x'], attr['y'], attr['width'], attr['height']


def get_window_geometry_hash(x, y, w, h):
    return "%s:%s:%s:%s" % (x, y, w, h)


def is_window_to_be_stickied(x, y, w, h):
    ref_point = (x + round(w/3), y + round(y/3))
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
    ewmh.display.flush()


def iterate_windows():
    windows = ewmh.getClientList()
    for win in windows:
        win_id = win.__hash__()
        try:
            win_pos = get_window_geometry(win)
        except:
            continue
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
            _WINDOW_POSITIONS[win_id] = win_pos
    ewmh.display.flush()


def run():
    initialize_windows()
    while True:
        iterate_windows()
        time.sleep(CHECK_INTERVAL_SECONDS)

run()

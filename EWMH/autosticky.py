from ewmh import EWMH
import signal
import time
import sys
ewmh = EWMH()

# PYTHON MODULE REQUIREMENTS
#
# - 'python-ewmh'
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

# USAGE
#
# Simply adjust the values below. The POSITION_THRESHOLD should be the
# either the horizontal or vertical resolution of your top/left screen.
# If the bottom/right screen is your external one, set the config variable
# BELOW_THRESHOLD_IS_STICKY to False, otherwise (your top/left screen is
# the external one) set it to True.
# Any window that has at least two thirds of its content beyond this barrier
# towards the external screen will become sticky.
# The VERTICAL_MODE flag specifies whether your screens are aligned
# top/bottom (True) or left/right (False). The POSITION_THRESHOLD will
# represent the X or Y coordinate of your screen edge respectively.
#
# The WIN_CLASS_BLACKLIST array specifies window classes that should be
# excluded from this script's behavior. Since this script tends to remove
# the EWMH sticky flag from windows below the barrier, it may interfere
# with windows that actually need this flag (e.g. panels).
# Use 'xprop' to find the WM_CLASS of those windows and insert its second
# string attribute to the WM_CLASS_BLACKLIST array below.
#
# Finally run the script via python:
#   $ python autosticky.py


# config values
VERTICAL_MODE = True
REPARENTING_WM = True
BELOW_THRESHOLD_IS_STICKY = False
POSITION_THRESHOLD = 1080
CHECK_INTERVAL_SECONDS = .5
WIN_CLASS_BLACKLIST = [
    'Xfce4-panel',
    'Plank'
]

_WINDOW_POSITIONS = {}
_LAST_WINDOWS = {}  # keeps track of recent windows for garbage collection

def is_window_class_blacklisted(win):
    return win.get_wm_class()[1] in WIN_CLASS_BLACKLIST

def get_window_geometry(win):
    if REPARENTING_WM:
        attr = win.query_tree().parent.get_geometry()._data
    else:
        attr = win.get_geometry()._data
    return attr['x'], attr['y'], attr['width'], attr['height']


def get_window_geometry_hash(x, y, w, h):
    return "%s:%s:%s:%s" % (x, y, w, h)


def is_window_to_be_stickied(x, y, w, h):
    if BELOW_THRESHOLD_IS_STICKY:
        ref_point = (x + round(2*w/3), y + round(2*h/3))
        if VERTICAL_MODE:
            return ref_point[1] < POSITION_THRESHOLD
        else:
            return ref_point[0] < POSITION_THRESHOLD
    else:
        ref_point = (x + round(w/3), y + round(h/3))
        if VERTICAL_MODE:
            return ref_point[1] > POSITION_THRESHOLD
        else:
            return ref_point[0] > POSITION_THRESHOLD


def set_window_sticky(win, sticky=True):
    if is_window_class_blacklisted(win):
        return
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
    try:
        initialize_windows()
        while True:
            iterate_windows()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        unsticky_all_windows()

run()

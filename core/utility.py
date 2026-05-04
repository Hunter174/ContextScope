import sys


def set_click_through(window, enabled: bool):
    """
    Enable/disable OS-level click-through for a Qt window.
    """

    if sys.platform == "win32":
        import ctypes

        hwnd = int(window.winId())

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20

        user32 = ctypes.windll.user32

        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        if enabled:
            style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        else:
            style &= ~WS_EX_TRANSPARENT

        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    elif sys.platform == "darwin":
        try:
            import objc
            from Cocoa import NSApp

            ns_window = window.windowHandle().nativeHandle()

            # Fallback approach (more reliable)
            ns_window.setIgnoresMouseEvents_(enabled)

        except Exception:
            pass
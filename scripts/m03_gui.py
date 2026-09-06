#!/usr/bin/env python3
"""X11/XWayland control of the visible M0.3 FS-UAE window only.

Requires python-xlib. Uses physical US key positions (Amiga default).
Examples: m03_gui.py shot evidence.png; m03_gui.py type 'AGTest:AmiGuard'
          m03_gui.py key Return; m03_gui.py chord F12 q
"""
import argparse
import time
from Xlib import X, XK, display, protocol
from Xlib.ext import xtest
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screenshots-dir', type=Path, default=Path('/tmp/amiguard-m03-runtime/screenshots'))
    parser.add_argument('action', choices=['shot', 'type', 'key', 'chord'])
    parser.add_argument('args', nargs='+')
    args = parser.parse_args()
    d = display.Display()
    candidates = []
    def windows(parent):
        for child in parent.query_tree().children:
            yield child
            yield from windows(child)

    for w in windows(d.screen().root):
        if any('fs-uae' in c.lower() for c in (w.get_wm_class() or ())) and w.get_attributes().map_state == X.IsViewable:
            candidates.append(w)
    if len(candidates) != 1:
        raise SystemExit(f'Expected exactly one visible FS-UAE window, got {len(candidates)}')
    w = candidates[0]
    root = d.screen().root
    active = d.intern_atom('_NET_ACTIVE_WINDOW')
    root.send_event(protocol.event.ClientMessage(window=w, client_type=active, data=(32, [2, X.CurrentTime, 0, 0, 0])), event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
    d.sync()
    time.sleep(0.7)
    prop = root.get_full_property(active, X.AnyPropertyType)
    if prop is None or prop.value[0] != w.id:
        raise SystemExit('FS-UAE is not the active desktop window; no input sent')

    def key(code, shift=False):
        if shift:
            xtest.fake_input(d, X.KeyPress, 50)
        xtest.fake_input(d, X.KeyPress, code)
        d.sync()
        time.sleep(0.06)
        xtest.fake_input(d, X.KeyRelease, code)
        if shift:
            xtest.fake_input(d, X.KeyRelease, 50)
        d.sync()
        time.sleep(0.06)

    if args.action == 'shot':
        before = set(args.screenshots_dir.glob('*crop*.png'))
        mod = d.keysym_to_keycode(XK.string_to_keysym('F12'))
        xtest.fake_input(d, X.KeyPress, mod)
        d.sync()
        time.sleep(0.15)
        key(d.keysym_to_keycode(XK.string_to_keysym('s')))
        xtest.fake_input(d, X.KeyRelease, mod)
        d.sync()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            added = set(args.screenshots_dir.glob('*crop*.png')) - before
            if added:
                source = max(added, key=lambda p: p.stat().st_mtime_ns)
                time.sleep(0.3)
                shutil.copyfile(source, args.args[0])
                print(f'Captured FS-UAE frame {source} to {args.args[0]}')
                return
            time.sleep(0.2)
        raise SystemExit('No new emulator screenshot; capture failed')
    elif args.action == 'chord':
        codes = [d.keysym_to_keycode(XK.string_to_keysym(n)) for n in args.args]
        for code in codes:
            xtest.fake_input(d, X.KeyPress, code)
            d.sync()
            time.sleep(0.12)
        for code in reversed(codes):
            xtest.fake_input(d, X.KeyRelease, code)
            d.sync()
            time.sleep(0.12)
    elif args.action == 'key':
        for name in args.args:
            key(d.keysym_to_keycode(XK.string_to_keysym(name)))
    elif args.action == 'type':
        keys = {}
        for chars, codes in [('1234567890', range(10, 20)), ('qwertyuiop', range(24, 34)),
                             ('asdfghjkl', range(38, 47)), ('zxcvbnm', range(52, 59))]:
            keys.update(zip(chars, codes))
        keys.update({' ': 65, ':': 47, ';': 47, '.': 60, '/': 61, '-': 20,
                     '>': 60, '<': 59, '"': 48, '\n': 36})
        for c in args.args[0]:
            if c.lower() not in keys:
                raise SystemExit(f'Unsupported character: {c!r}')
            key(keys[c.lower()], c.isupper() or c in ':><"')
    print(f'{args.action}: {args.args!r}')


if __name__ == '__main__':
    main()

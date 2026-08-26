---
title: "Control a Lid-Closed Laptop with Your Mac Trackpad: A Software KVM Guide"
description: "Use your Mac's trackpad and keyboard to control a closed-lid laptop hooked up to an external monitor. Covers Barrier / Input Leap setup, how software KVM works under the hood, and fixes for permissions, SSL, Gatekeeper, missing DLLs, and hotel Wi-Fi AP isolation."
date: 2026-08-25
slug: "software-kvm"
categories:
    - Tutorial
tags:
    - KVM
    - macOS
    - Windows
    - LAN
toc: true
---

# Control a Lid-Closed Laptop with Your Mac Trackpad: A Software KVM Guide

## 1. The Problem

You have a laptop, an external monitor, and a Mac. The laptop sits closed under your desk, connected only to the monitor, and you want to drive it directly from the Mac's trackpad and keyboard — without plugging in a second mouse and keyboard.

The right solution is a **software virtual KVM (keyboard/mouse sharing)**: the Mac acts as the server (the machine with the physical keyboard and trackpad), and the closed laptop acts as the client. As long as both are on the same LAN, your cursor slides off the Mac's screen edge and "jumps through" to the external display, where trackpad gestures and keystrokes control the laptop seamlessly.

## 2. Choosing an Open-Source Tool

This is a mature problem in the open-source world — no need to build anything yourself.

| Project | What it is | Best for |
| --- | --- | --- |
| [Barrier](https://github.com/debauchee/barrier) / [Input Leap](https://github.com/input-leap/input-leap) | Software KVM (mouse/keyboard sharing) | **Recommended.** Cursor slides between screens with near-zero latency, plus cross-device clipboard |
| [Deskreen](https://github.com/pavlobu/deskreen) | WebRTC screen sharing / reverse control | Using the Mac as a browser-based secondary screen/controller |
| [RustDesk](https://github.com/rustdesk/rustdesk) | Open-source remote desktop | When you also want to see the laptop's screen in a Mac window |

**Go with Barrier or Input Leap.** They're part of the same family (descended from Synergy, maintained for over a decade): fully open source, cross-platform (macOS / Windows / Linux), transmit only keyboard/mouse signals (no display-stream bandwidth), and typically add less than 1–2 ms of LAN latency.

Why not write your own?

- **Low-level complexity**: you'd need to intercept macOS Cocoa/Quartz and multi-touch events, then faithfully replay them through Windows `SendInput` — lots of OS driver and permission handling;
- **The ecosystem is mature**: low-latency TCP/UDP transport, seamless clipboard sync, and a graphical screen-layout editor are all already built;
- **It just works**: install a client on both machines, set the IP and screen name, and you're done in about five minutes.

## 3. How It Works Under the Hood

These tools don't "hack around" the OS — they use official low-level system APIs. It's a standard client-server network model with three layers:

### 3.1 Server side (Mac): global input capture and interception

- Registers a global event hook via `CGEventTapCreate`, listening for events like `kCGEventMouseMoved` and `kCGEventScrollWheel` — this is why **Accessibility permission** is required;
- When the cursor crosses the configured screen edge, it calls `CGAssociateMouseAndMouseCursorPosition(false)` to lock the real cursor position and swallows the input events so macOS doesn't respond;
- `CGWarpMouseCursorPosition` and `CGDisplayHideCursor` handle cursor jumping and hiding.

### 3.2 Network layer: a cross-platform event protocol

Different OSes, different data structures — so a neutral byte-stream protocol is used (e.g. `DMOVP` for relative movement, `DKEYD` for key press, `DCLIP` for clipboard data).

- Long-lived TCP/UDP socket on port **24800**;
- Packets are only tens of bytes of coordinates and key codes, so LAN latency is imperceptible.

### 3.3 Client side (Windows / Linux): virtual input injection

- **Windows**: uses the official Win32 API `SendInput` (older versions used `mouse_event` / `keybd_event`), converting network deltas into `MOUSEINPUT` structs and key codes into `KEYBDINPUT` virtual-key (VK) codes. The kernel treats them like real hardware input;
- **Linux**: `XTestFakeKeyEvent` on X11, or libinput / `/dev/uinput` virtual device nodes on Wayland.

| Layer | Official OS support |
| --- | --- |
| Mac capture | `CGEventTap` (Core Graphics event bus) |
| Mac cursor lock | `CGWarpMouseCursorPosition` & `CGDisplayHideCursor` |
| Windows injection | Win32 `SendInput` (official accessibility/automation channel) |
| Clipboard | macOS `NSPasteboard` ↔ Win32 `OpenClipboard` / `SetClipboardData` |

In short: everything uses the official accessibility and automation channels the OS provides. Once you grant the permissions in System Settings, the program can legitimately and reliably read/write global input events.

## 4. Setup: Mac as Server, Windows Laptop as Client

The rule of thumb: **the server is the machine with the physical keyboard and trackpad**. Since you want the Mac's trackpad to control the other machine, the Mac is the server and the laptop is the client.

### 4.1 Install

- **Mac**: `brew install --cask barrier` is easiest (note: Homebrew's official cask list doesn't include `input-leap` yet). Alternatively, download from [Input Leap Releases](https://github.com/input-leap/input-leap/releases): pick `macOS-Apple_Silicon-*` for M-series, `macOS-x86_64-*` for Intel, or the Universal build if unsure;
- **Windows**: prefer a **Release installer** (e.g. `BarrierSetup-2.4.0-release.exe`) — avoid Debug builds. You can also run `winget install InputLeap.InputLeap`;
- **Prevent sleep when the lid is closed (do this first)**: Windows Control Panel → Power Options → "Choose what closing the lid does", set "When I close the lid" to **Do nothing** while plugged in. Otherwise the laptop sleeps and loses the network when closed.

### 4.2 Configure the Mac (Server)

1. Grant **Accessibility**, **Input Monitoring** (if present), and **Local Network** permissions in System Settings → Privacy & Security;
2. Check `Server (share this computer's mouse and keyboard)`;
3. Click `Configure Server...`: drag a monitor icon from the top-right onto the grid, placing it where the external screen sits relative to the Mac (above or to the right). Double-click the new icon and set its `Screen Name` to exactly what the Windows client displays — **case-sensitive, no extra spaces**;
4. Note the LAN IP shown on the Mac (e.g. `192.168.1.50`);
5. Click `Start`.

### 4.3 Configure the Windows laptop (Client)

1. Check `Client (use another computer's mouse and keyboard)`;
2. **Write down the `Screen Name` shown on the window** (e.g. `DESKTOP-ABC1234`) — you'll enter it on the Mac;
3. Enter the Mac's IP in the `Server IP` field;
4. If auto-discovery doesn't find the server, uncheck `Auto config`;
5. Click `Start`; if an SSL fingerprint prompt appears, click `Accept / Trust`.

### 4.4 Verify and use

- Both ends showing `Running` / `Connected` means pairing succeeded;
- Slide the cursor off the Mac's edge toward the configured screen — it enters the external display;
- Keyboard input, two-finger scrolling, and two-finger right-click all act on the laptop;
- Optional: remap the Mac `Command` key to Windows `Ctrl`, so `Cmd + C / Cmd + V` copy/paste directly;
- Clipboard is shared: copy text on the Mac, slide over, and paste on the laptop.

## 5. Trackpad & Keyboard Support

| Action | Result on the laptop | Support |
| --- | --- | --- |
| Keyboard (letters, numbers, symbols, F-keys, arrows) | Full input | ✅ 100%, no latency |
| One-finger move | Controls laptop cursor | ✅ Perfect |
| One-finger tap / click | Left click | ✅ Perfect |
| Two-finger tap / click | Right-click menu | ✅ Perfect |
| Two-finger scroll (vertical/horizontal) | Smooth scrolling | ✅ Perfect |
| One-finger press & drag | Select text, drag windows/files | ✅ Perfect |
| Three-/four-finger gestures (Mission Control etc.) | Can't trigger Windows task gestures | ❌ Intercepted by macOS first |

For daily work, coding, browsing, and file handling it's fully sufficient — in practice it's like giving the closed laptop a wireless keyboard and trackpad.

## 6. Troubleshooting Log

### 6.1 Mac stuck on "Starting"

Usually stale permissions or an SSL key-generation hang:

1. **Re-grant Accessibility**: System Settings → Privacy & Security → Accessibility, remove InputLeap (minus), re-add it manually (plus), and enable the toggle. Also check Input Monitoring and Local Network;
2. **Disable TLS/SSL to test**: Preferences on both sides, uncheck `Enable TLS/SSL encryption`, then Stop and Start again;
3. **Read the log**: Menu bar → View → Log, looking for `permission denied`, `address already in use`, or `failed to create socket`.

### 6.2 macOS "can't open the app" / terminal launch errors

An `.app` is a directory (App Bundle) — you **can't execute it directly in the terminal** (that gives `permission denied`). Do this instead:

```bash
# Copy out of the mounted volume first (don't run from /Volumes)
cp -R /Volumes/InputLeap/InputLeap.app /Applications/

# Clear Gatekeeper quarantine when "cannot verify the developer" appears
xattr -cr /Applications/InputLeap.app

# Launch normally
open /Applications/InputLeap.app

# Run the inner binary directly if you want terminal logs
/Applications/InputLeap.app/Contents/MacOS/input-leap
```

Alternative for Gatekeeper: System Settings → Privacy & Security → Security section → "Open Anyway".

### 6.3 Windows complains about a missing DLL (e.g. MSVCP140.dll)

You probably installed a **Debug build** (which needs a dev environment) or are missing the Visual C++ runtime. Two fixes:

- Switch to an official **Release installer** (`BarrierSetup-x.x.x-release.exe`), which bundles the dependencies;
- Or install the Microsoft runtime `vc_redist.x64.exe` and reopen the app.

### 6.4 The cursor won't leave the Mac screen

Check in order:

1. **Accessibility permission isn't effective** — if you launched from the terminal binary, the permission may be bound to Terminal/iTerm; enable both (or toggle them off and on);
2. **The two ends never truly connected** — the Windows side should show `Connected`, and the Mac log should show `client "xxx" has connected`; a persistent `connecting to server...` means a network problem;
3. **Screen Name mismatch** — the names must match character for character;
4. **Edge locks / hotkeys** — check for an active Scroll Lock (it freezes screen switching) and whether Preferences enable `Switch on double tap` or `Dead corners`; sometimes you need to push the cursor to the edge firmly or quickly.

### 6.5 Both machines can browse the internet but can't connect: hotel Wi-Fi AP isolation

Typical symptom: both devices are on the same hotel network, but IPs are in different subnets (e.g. `192.168.200.x` vs `192.168.203.x`) and pings time out. Hotels and public Wi-Fi often enable **AP/client isolation** or use very large subnets (e.g. `/21`, `/22`) that block peer-to-peer traffic between clients.

Workarounds:

1. **Phone hotspot (easiest)**: connect both machines to the same phone hotspot. Input Leap only sends keyboard/mouse signals — a few KB per second, negligible data use. Re-check the Mac's IP (usually `172.20.10.x` or `192.168.43.x`) and enter it on Windows;
2. **Mac Internet Sharing**: System Settings → General → Sharing → Internet Sharing; share the hotel Wi-Fi connection over Wi-Fi and have the Windows laptop join the Mac's hotspot;
3. **Direct Ethernet cable (lowest latency)**: connect both machines with one cable; link-local IPs (`169.254.x.x`) are assigned automatically, or set static IPs manually (e.g. Mac `10.0.0.1`, laptop `10.0.0.2`). Keyboard/mouse traffic goes over the cable while both keep using hotel Wi-Fi for the internet.

Other notes:

- Make sure both devices join the **same SSID**, not one 2.4 GHz and one 5 GHz or guest network;
- Disable VPNs / proxies / VM virtual adapters, or the IP shown in the app may be a virtual adapter address;
- On the Mac, run `ipconfig getifaddr en0` to find the real Wi-Fi IP;
- Check that Windows Firewall allows **port 24800** (temporarily disabling Defender Firewall is a quick test).

## 7. Summary

- To drive a closed-lid laptop from your Mac's trackpad, **Barrier / Input Leap** is the go-to software KVM: Mac as server, laptop as client, same LAN, cursor sharing plus clipboard sync;
- Under the hood it's all official system APIs (`CGEventTap` / `SendInput`) — legitimate and stable once you grant the required permissions;
- Three things make or break the setup: **reachable IPs, an exact Screen Name match, and complete permissions on both ends**;
- Most "can't connect / cursor won't cross / stuck starting" issues trace back to permissions, SSL, Debug builds, or network isolation;
- On hotel or public Wi-Fi with AP isolation, a phone hotspot or a direct Ethernet cable is the fastest fix.

#!/usr/bin/env python3
"""Generates every PNG diagram in ../diagrams for the physical-design notes."""
import os
from collections import deque
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "diagrams")
os.makedirs(OUT, exist_ok=True)
C = dict(ink="#1f2937", mute="#6b7280", blue="#dbeafe", green="#dcfce7", amber="#fef3c7",
         rose="#ffe4e6", violet="#ede9fe", slate="#e5e7eb", teal="#ccfbf1",
         b="#3b82f6", g="#16a34a", r="#dc2626", o="#ea580c", p="#7c3aed", y="#ca8a04")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})


def fig(w, h):
    f, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(0, w * 10); ax.set_ylim(0, h * 10); ax.axis("off")
    return f, ax


def save(f, name):
    f.savefig(os.path.join(OUT, name), bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(f)


def box(ax, x, y, w, h, t, fc=C["blue"], fs=10, bold=False, r=0.6, ec=None, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec or C["ink"], lw=1.2))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs,
            weight="bold" if bold else "normal", color=tc or C["ink"])


def arrow(ax, x1, y1, x2, y2, t=None, color=None, fs=9, style="-|>", ls="-", rad=0.0, toff=(0, 1.3)):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=13,
                                 color=color or C["ink"], lw=1.3, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))
    if t:
        ax.text((x1 + x2) / 2 + toff[0], (y1 + y2) / 2 + toff[1], t, ha="center", va="center",
                fontsize=fs, color=C["mute"], bbox=dict(fc="white", ec="none", pad=0.4))


def title(ax, t, sub=None):
    X = ax.get_xlim()[1]; Y = ax.get_ylim()[1]
    ax.text(X / 2, Y - 2, t, ha="center", va="top", fontsize=14, weight="bold", color=C["ink"])
    if sub:
        ax.text(X / 2, Y - 6, sub, ha="center", va="top", fontsize=10, color=C["mute"])


def wave(ax, x0, y0, period, n, h=4, scale=1.0, color=C["ink"], high_first=True, lw=1.5):
    xs, ys = [x0], [y0]
    t = x0
    for _ in range(n):
        half = period * scale / 2
        xs += [t, t, t + half, t + half]
        ys += [y0, y0 + h, y0 + h, y0]
        t += period * scale
    xs.append(t); ys.append(y0)
    ax.plot(xs, ys, color=color, lw=lw)


# ------------------------------------------------------------------ 01 flow
def d_flow():
    f, ax = fig(14, 7.4)
    title(ax, "Physical design flow: from netlist to a chip you can manufacture", "the 10 steps used throughout this course")
    steps = [("1", "Floorplan", "die & core size,\npre-placed cells,\ndecaps, power, pins", C["green"]),
             ("2", "Netlist\nbinding", "gates -> real\ncell shapes\n(library)", C["blue"]),
             ("3", "Placement", "put cells on\nthe floorplan", C["blue"]),
             ("4", "Optimise\nplacement", "estimate wires,\nadd repeaters\n(buffers)", C["blue"]),
             ("5", "Timing\n(ideal clock)", "setup check,\nslew check", C["amber"]),
             ("6", "Clock tree\nsynthesis", "clock reaches\nevery flop at\nsame time", C["violet"]),
             ("7", "Clock net\nshielding", "protect clock\nfrom crosstalk", C["violet"]),
             ("8", "Timing\n(real clock)", "setup + hold\nwith real\nclock delays", C["amber"]),
             ("9", "Routing\n+ DRC", "real wires,\nobey design\nrules", C["rose"]),
             ("10", "Extraction\n+ final STA", "real R & C\n(SPEF) ->\nsign-off timing", C["rose"])]
    for i, (n, t, d, c) in enumerate(steps):
        row, col = divmod(i, 5)
        x = 3 + col * 27.5; y = 38 - row * 30
        box(ax, x, y, 23, 22, "", fc=c)
        ax.add_patch(Circle((x + 3.2, y + 18.8), 2.4, fc=C["ink"]))
        ax.text(x + 3.2, y + 18.8, n, ha="center", va="center", color="white", fontsize=9, weight="bold")
        ax.text(x + 13, y + 16, t, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(x + 11.5, y + 6, d, ha="center", va="center", fontsize=8.6)
        if col < 4:
            arrow(ax, x + 23, y + 11, x + 27.5, y + 11)
    arrow(ax, 3 + 4 * 27.5 + 11.5, 38, 3 + 11.5, 30, color=C["mute"], ls="--")
    ax.text(70, 3, "Input: synthesised netlist (gates + connections)      Output: GDS layout sent to the factory",
            ha="center", fontsize=9.5, color=C["mute"])
    save(f, "pd01_flow.png")


# ------------------------------------------------------------------ 02 UF / AR
def d_uf_ar():
    f, ax = fig(14, 7)
    title(ax, "Core, die, utilisation factor and aspect ratio", "each logic cell is treated as a 1 x 1 unit box (wires ignored for now);  grey = die, white = core")
    u = 6.5
    def chip(x, cw, ch, lab):
        y = 46 - ch * u
        ax.add_patch(Rectangle((x - 2.5, y - 2.5), cw * u + 5, ch * u + 5, fc=C["slate"], ec=C["ink"], lw=1.2))
        ax.add_patch(Rectangle((x, y), cw * u, ch * u, fc="white", ec=C["ink"], lw=1.4))
        for k, name in enumerate(["FF", "FF", "AND", "OR"]):
            cx, cy = k % 2, k // 2
            if cw >= 4 and ch == 1:
                cx, cy = k, 0
            ax.add_patch(Rectangle((x + cx * u, y + (ch - 1 - cy) * u), u, u, fc=C["blue"], ec=C["b"]))
            ax.text(x + cx * u + u / 2, y + (ch - 1 - cy) * u + u / 2, name, ha="center", va="center", fontsize=9)
        ax.text(x + cw * u / 2, 26, lab, ha="center", va="top", fontsize=9.5)
    chip(10, 2, 2, "core 2 x 2 units\nUF = 4/4 = 1 (100%)\nAR = 2/2 = 1 (square)")
    chip(50, 4, 1, "core 4 wide x 1 high\nUF = 4/4 = 1\nAR = 1/4 = 0.25 (rectangle)")
    chip(100, 4, 2, "core 4 wide x 2 high\nUF = 4/8 = 0.5 (50%)\nAR = 2/4 = 0.5")
    ax.text(70, 8, "Utilisation factor = area used by the netlist / total core area     Aspect ratio = core height / core width",
            ha="center", fontsize=10, weight="bold")
    ax.text(70, 3.5, "Real designs aim for UF about 0.5-0.6: the free space is needed for buffers, wires and later changes.",
            ha="center", fontsize=9.5, color=C["mute"])
    save(f, "pd02_uf_ar.png")


# ------------------------------------------------------------------ 03 pre-placed cells
def d_preplaced():
    f, ax = fig(13, 6.6)
    title(ax, "Pre-placed cells: big blocks are placed FIRST, by the designer", "their position is fixed; the tool fills in everything else later")
    for k, (x, lab) in enumerate([(6, "Step 1: empty core"), (48, "Step 2: place IP blocks (fixed)"), (90, "Step 3: tool places the rest")]):
        ax.add_patch(Rectangle((x, 12), 34, 34, fc="white", ec=C["ink"], lw=1.4))
        ax.text(x + 17, 7, lab, ha="center", fontsize=9.5)
        if k >= 1:
            box(ax, x + 3, 30, 12, 12, "Memory", fc=C["violet"], fs=8.5, r=0.3)
            box(ax, x + 19, 30, 12, 12, "MUX /\nclock gating", fc=C["violet"], fs=8, r=0.3)
            box(ax, x + 3, 16, 12, 10, "Comparator", fc=C["violet"], fs=8, r=0.3)
        if k == 2:
            import random
            random.seed(3)
            for _ in range(28):
                cx = x + 17 + random.random() * 15; cy = 15 + random.random() * 12
                ax.add_patch(Rectangle((cx, cy), 1.6, 1.6, fc=C["blue"], ec=C["b"], lw=0.5))
    arrow(ax, 40, 29, 48, 29); arrow(ax, 82, 29, 90, 29)
    save(f, "pd03_preplaced.png")


# ------------------------------------------------------------------ 04 decap
def d_decap():
    f, ax = fig(13, 6.8)
    title(ax, "Decoupling capacitor: a small 'water tank' next to each block", "the long supply wire has resistance + inductance, so the block sees a dropped voltage when it switches")
    box(ax, 4, 30, 14, 12, "Power\nsupply\n1 V", fc=C["amber"], fs=9)
    ax.plot([18, 46], [36, 36], color=C["ink"], lw=2)
    for i in range(3):
        ax.plot([22 + i * 7, 24 + i * 7, 26 + i * 7, 28 + i * 7], [36, 38, 34, 36], color=C["r"], lw=1.6)
    ax.text(32, 40, "R + L of the long wire", ha="center", fontsize=8.5, color=C["r"])
    box(ax, 46, 28, 18, 16, "Block\n(pre-placed)", fc=C["violet"], fs=9)
    ax.text(55, 23, "sees only ~0.7 V\nwhen many gates switch", ha="center", va="top", fontsize=8.5, color=C["r"])
    # with decap
    box(ax, 72, 30, 14, 12, "Power\nsupply\n1 V", fc=C["amber"], fs=9)
    ax.plot([86, 118], [36, 36], color=C["ink"], lw=2)
    box(ax, 118, 28, 18, 16, "Block", fc=C["violet"], fs=9)
    ax.plot([108, 108], [36, 31], color=C["ink"], lw=1.6)
    ax.plot([104, 112], [31, 31], color=C["g"], lw=3); ax.plot([104, 112], [29, 29], color=C["g"], lw=3)
    ax.plot([108, 108], [29, 25], color=C["ink"], lw=1.6); ax.plot([105, 111], [25, 25], color=C["ink"], lw=1.6)
    ax.text(100, 18, "decap charges up when idle,\nthen gives current locally\nwhen the block switches", ha="center", va="top", fontsize=8.5, color=C["g"])
    ax.text(127, 23, "stays close to 1 V", ha="center", va="top", fontsize=8.5, color=C["g"])
    ax.text(34, 50, "WITHOUT decap", ha="center", weight="bold", color=C["r"])
    ax.text(104, 50, "WITH decap next to the block", ha="center", weight="bold", color=C["g"])
    ax.set_xlim(0, 140)
    save(f, "pd04_decap.png")


# ------------------------------------------------------------------ 05 power grid
def d_power():
    f, ax = fig(13, 6.8)
    title(ax, "Power planning: one supply point vs a power mesh", "many cells switching together cause ground bounce (0 rises) and voltage droop (1 falls)")
    # single point
    ax.add_patch(Rectangle((6, 10), 46, 40, fc="white", ec=C["ink"], lw=1.3))
    ax.add_patch(Rectangle((6, 48), 5, 2, fc=C["r"])); ax.text(8.5, 52, "VDD", ha="center", fontsize=8.5, color=C["r"])
    ax.add_patch(Rectangle((47, 10), 5, 2, fc=C["b"])); ax.text(49.5, 7, "VSS", ha="center", fontsize=8.5, color=C["b"])
    for i in range(8):
        ax.add_patch(Rectangle((14 + i * 4, 28), 3, 3, fc=C["amber"], ec=C["y"]))
    ax.text(29, 24, "16-bit bus switching 1 -> 0 at once:\nall charge rushes to ONE ground pin\n-> ground bounce", ha="center", va="top", fontsize=8.5)
    ax.text(29, 54, "Single VDD / VSS point", ha="center", weight="bold", color=C["r"])
    # mesh
    x0 = 76
    ax.add_patch(Rectangle((x0, 10), 46, 40, fc="white", ec=C["ink"], lw=1.3))
    for i in range(6):
        ax.plot([x0 + 4 + i * 8, x0 + 4 + i * 8], [10, 50], color=C["r"], lw=2 if i % 2 == 0 else 0.01)
        ax.plot([x0 + 8 + i * 8, x0 + 8 + i * 8], [10, 50], color=C["b"], lw=2 if i % 2 == 0 else 0.01)
    for j in range(5):
        ax.plot([x0, x0 + 46], [14 + j * 8, 14 + j * 8], color=C["r"] if j % 2 == 0 else C["b"], lw=2)
    ax.text(x0 + 23, 54, "Power mesh (grid)", ha="center", weight="bold", color=C["g"])
    ax.text(x0 + 23, 6, "red = VDD, blue = VSS: every cell has a supply and a ground nearby", ha="center", fontsize=8.5)
    ax.set_xlim(0, 130)
    save(f, "pd05_power_mesh.png")


# ------------------------------------------------------------------ 06 pins + blockage
def d_pins():
    f, ax = fig(12, 7.2)
    title(ax, "Pin placement and logical cell placement blockage")
    ax.add_patch(Rectangle((10, 8), 76, 54, fc=C["slate"], ec=C["ink"], lw=1.3))
    ax.add_patch(Rectangle((18, 16), 60, 38, fc="white", ec=C["ink"], lw=1.3))
    ax.add_patch(Rectangle((10, 8), 76, 8, fc="none", hatch="///", ec=C["r"], lw=0))
    ax.add_patch(Rectangle((10, 54), 76, 8, fc="none", hatch="///", ec=C["r"], lw=0))
    ax.add_patch(Rectangle((10, 16), 8, 38, fc="none", hatch="///", ec=C["r"], lw=0))
    ax.add_patch(Rectangle((78, 16), 8, 38, fc="none", hatch="///", ec=C["r"], lw=0))
    pins_l = [("Din1", 46), ("Din2", 38), ("Din3", 30)]
    for n, y in pins_l:
        ax.add_patch(Rectangle((10, y - 1), 2.5, 2, fc=C["b"])); ax.text(9, y, n, ha="right", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((10, 20), 4, 4, fc=C["p"])); ax.text(9, 22, "CLK", ha="right", va="center", fontsize=8.5, weight="bold", color=C["p"])
    for n, y in [("Dout1", 46), ("Dout2", 38), ("Dout3", 30)]:
        ax.add_patch(Rectangle((83.5, y - 1), 2.5, 2, fc=C["o"])); ax.text(87, y, n, va="center", fontsize=8.5)
    box(ax, 22, 40, 10, 8, "FF1", fc=C["blue"], fs=8.5, r=0.2)
    box(ax, 64, 40, 10, 8, "FF2", fc=C["blue"], fs=8.5, r=0.2)
    ax.plot([12.5, 22], [46, 46], color=C["b"], lw=1); ax.plot([74, 83.5], [46, 46], color=C["o"], lw=1)
    ax.text(96, 52, "Input pins on the side\nwhere their cells are", fontsize=9)
    ax.text(96, 38, "Clock pin is BIGGER:\nit drives many flip-flops,\nso it needs low resistance", fontsize=9, color=C["p"])
    ax.text(96, 20, "Hatched ring = placement\nblockage: no logic cells\nmay be placed between\nthe pins and the core", fontsize=9, color=C["r"])
    ax.set_xlim(0, 125)
    save(f, "pd06_pins_blockage.png")


# ------------------------------------------------------------------ 07 netlist binding
def d_binding():
    f, ax = fig(13.5, 6.6)
    title(ax, "Netlist binding: every gate becomes a real box from the library", "the library has each cell in different sizes; bigger = stronger and faster, but more area")
    box(ax, 4, 14, 36, 34, "", fc="white")
    ax.text(22, 44.5, "Netlist (logic view)", ha="center", weight="bold", fontsize=10)
    ax.text(22, 28, "Din1 -> FF1 -> AND -> OR -> FF2 -> Dout1\nDin2 -> FF1 -> NOT -> FF2 -> Dout2\nclk -> all flip-flops", ha="center", va="center", fontsize=8.6, family="DejaVu Sans Mono")
    arrow(ax, 40, 31, 50, 31)
    box(ax, 50, 14, 36, 34, "", fc="white")
    ax.text(68, 44.5, "Library (physical view)", ha="center", weight="bold", fontsize=10)
    items = [("FF", 3.5, 3.5), ("FF x2", 5, 3.5), ("AND", 2.5, 2.5), ("AND x4", 4, 2.5), ("OR", 2.5, 2.5), ("NOT", 1.6, 2.5)]
    for i, (n, w, h) in enumerate(items):
        r, c = divmod(i, 2)
        x = 55 + c * 15; y = 34 - r * 8
        ax.add_patch(Rectangle((x, y), w * 2, h * 2, fc=C["blue"], ec=C["b"]))
        ax.text(x + w + 0.2, y - 1.3, n, ha="center", fontsize=8)
    arrow(ax, 86, 31, 96, 31)
    box(ax, 96, 14, 40, 34, "", fc="white")
    ax.text(116, 44.5, "Netlist as boxes", ha="center", weight="bold", fontsize=10)
    for i, (n, w) in enumerate([("FF1", 7), ("AND", 5), ("OR", 5), ("NOT", 3.2), ("FF2", 7)]):
        ax.add_patch(Rectangle((99 + i * 7.3, 26), w * 0.9, 7, fc=C["blue"], ec=C["b"]))
        ax.text(99 + i * 7.3 + w * 0.45, 24, n, ha="center", fontsize=7.5, va="top")
    ax.set_xlim(0, 140)
    save(f, "pd07_netlist_binding.png")


# ------------------------------------------------------------------ 08 placement + repeaters
def d_repeaters():
    f, ax = fig(13, 6.4)
    title(ax, "Optimised placement: long wires get repeaters (buffers)", "the tool estimates wire length and capacitance; if the signal would become too slow, it inserts buffers")
    ax.add_patch(Rectangle((4, 8), 122, 46, fc="white", ec=C["ink"], lw=1.2))
    box(ax, 8, 38, 10, 8, "FF1", fc=C["blue"], fs=9, r=0.2)
    box(ax, 22, 38, 7, 8, "1", fc=C["amber"], fs=9, r=0.2)
    box(ax, 33, 38, 7, 8, "2", fc=C["amber"], fs=9, r=0.2)
    box(ax, 44, 38, 10, 8, "FF2", fc=C["blue"], fs=9, r=0.2)
    for a, b in [(18, 22), (29, 33), (40, 44)]:
        ax.plot([a, b], [42, 42], color=C["ink"])
    ax.text(31, 33, "cells close together:\nshort wires, no buffer needed", ha="center", va="top", fontsize=8.8, color=C["g"])
    box(ax, 8, 14, 10, 8, "FF1'", fc=C["blue"], fs=9, r=0.2)
    box(ax, 112, 14, 10, 8, "FF2'", fc=C["blue"], fs=9, r=0.2)
    ax.plot([18, 112], [18, 18], color=C["ink"])
    for x in (44, 78):
        ax.add_patch(plt.Polygon([[x, 15], [x, 21], [x + 5, 18]], fc=C["g"], ec=C["ink"]))
    ax.text(65, 25, "long wire: its capacitance makes the edge slow -> insert repeaters (green triangles)", ha="center", fontsize=8.8, color=C["r"])
    # waveforms
    ax.plot([62, 66, 70, 74], [44, 44, 50, 50], color=C["g"], lw=1.6); ax.text(68, 52, "good edge", ha="center", fontsize=8, color=C["g"])
    ax.plot([84, 88, 100, 104], [44, 44, 50, 50], color=C["r"], lw=1.6); ax.text(94, 52, "slow edge (bad slew)", ha="center", fontsize=8, color=C["r"])
    ax.set_xlim(0, 130)
    save(f, "pd08_repeaters.png")


# ------------------------------------------------------------------ 09 setup timing
def d_setup():
    f, ax = fig(13.5, 7.4)
    title(ax, "Setup timing check with an ideal clock:   theta < T - S - SU", "data launched at time 0 must arrive at the capture flop before the next edge minus setup and uncertainty")
    box(ax, 6, 46, 14, 12, "Launch\nflop", fc=C["blue"], fs=9)
    ax.add_patch(matplotlib.patches.Ellipse((48, 52), 34, 12, fc=C["amber"], ec=C["ink"]))
    ax.text(48, 52, "combinational logic\ntheta = logic delay + wire delay", ha="center", va="center", fontsize=8.6)
    box(ax, 76, 46, 14, 12, "Capture\nflop", fc=C["blue"], fs=9)
    arrow(ax, 20, 52, 31, 52); arrow(ax, 65, 52, 76, 52)
    ax.text(100, 54, "Example: f = 1 GHz -> T = 1 ns\nS = 0.1 ns, SU = 0.05 ns\n-> theta must be < 0.85 ns", fontsize=9.3)
    # timeline
    y = 22
    ax.plot([10, 122], [y, y], color=C["ink"], lw=1)
    for x, l in [(14, "0"), (114, "T")]:
        ax.plot([x, x], [y - 1.5, y + 14], color=C["ink"], lw=1.6)
        ax.text(x, y - 3.5, l, ha="center", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((14, y + 2), 80, 3, fc=C["amber"], ec=C["y"]))
    ax.text(54, y + 3.5, "theta (data travel time)", ha="center", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((104, y + 2), 10, 3, fc=C["rose"], ec=C["r"]))
    ax.text(109, y + 7, "S", ha="center", fontsize=9, color=C["r"], weight="bold")
    ax.add_patch(Rectangle((99, y + 2), 5, 3, fc=C["violet"], ec=C["p"]))
    ax.text(101.5, y + 7, "SU", ha="center", fontsize=8.5, color=C["p"], weight="bold")
    ax.text(14, y + 16, "launch edge", ha="center", fontsize=8.5, color=C["mute"])
    ax.text(114, y + 16, "capture edge", ha="center", fontsize=8.5, color=C["mute"])
    ax.text(66, 8, "S = setup time: the flop's internal MUXes need time before the edge.  SU = setup uncertainty (jitter).",
            ha="center", fontsize=9, color=C["mute"])
    ax.set_xlim(0, 135)
    save(f, "pd09_setup.png")


# ------------------------------------------------------------------ 10 jitter
def d_jitter():
    f, ax = fig(13, 5.8)
    title(ax, "Clock jitter: the edge does not arrive at exactly the same time every cycle", "the clock source is not perfect, so each edge can move a little; we reserve 'uncertainty' (SU) for it")
    wave(ax, 8, 26, 30, 3, h=12, color=C["ink"])
    for k in range(1, 4):
        x = 8 + k * 30
        ax.add_patch(Rectangle((x - 2.5, 24), 5, 16, fc=C["rose"], ec="none", alpha=0.7))
        ax.plot([x - 2, x - 2], [26, 38], color=C["r"], lw=0.8, ls="--")
        ax.plot([x + 2, x + 2], [26, 38], color=C["r"], lw=0.8, ls="--")
    ax.text(68, 18, "red band = window in which the edge may occur (jitter)", ha="center", fontsize=9.5, color=C["r"])
    ax.text(68, 9, "Ideal clock: period T exactly.   Real clock: T +/- a little.   Setup check becomes  theta < T - S - SU",
            ha="center", fontsize=9.5)
    ax.set_xlim(0, 136)
    save(f, "pd10_jitter.png")


# ------------------------------------------------------------------ 11 multiple clocks
def d_multiclk():
    f, ax = fig(14, 7)
    title(ax, "Setup check with two clocks: find the SHORTEST launch-to-capture window", "CLK1 (launch) T = 1 ns,  CLK2 (capture) T = 1.5 ns  ->  expand both until a common rising edge at 3 ns")
    sc = 36  # units per ns
    x0 = 14
    ax.text(10, 43, "CLK1\n(launch)", ha="right", va="center", fontsize=9)
    ax.text(10, 26, "CLK2\n(capture)", ha="right", va="center", fontsize=9)
    wave(ax, x0, 39, 1.0, 3, h=8, scale=sc, color=C["b"])
    wave(ax, x0, 22, 1.5, 2, h=8, scale=sc, color=C["g"])
    for t in [0, 1, 2, 3]:
        ax.text(x0 + t * sc, 50, f"{t} ns", ha="center", fontsize=8.5, color=C["b"])
    for t in [0, 1.5, 3]:
        ax.text(x0 + t * sc, 18.5, f"{t} ns", ha="center", fontsize=8.5, color=C["g"])
    ax.plot([x0 + 3 * sc] * 2, [16, 50], color=C["mute"], ls=":", lw=1)
    ax.add_patch(FancyArrowPatch((x0 + 1 * sc, 36), (x0 + 1.5 * sc, 33), arrowstyle="-|>", mutation_scale=14, color=C["r"], lw=2))
    ax.text(x0 + 1.25 * sc, 31, "0.5 ns", ha="center", fontsize=9.5, color=C["r"], weight="bold")
    ax.add_patch(FancyArrowPatch((x0, 36), (x0 + 1.5 * sc, 34.5), arrowstyle="-|>", mutation_scale=12, color=C["mute"], lw=1, ls="--"))
    ax.text(x0 + 0.4 * sc, 33.2, "1.5 ns", fontsize=8.5, color=C["mute"])
    ax.add_patch(FancyArrowPatch((x0 + 2 * sc, 36), (x0 + 3 * sc, 33), arrowstyle="-|>", mutation_scale=12, color=C["mute"], lw=1, ls="--"))
    ax.text(x0 + 2.5 * sc, 31, "1 ns", ha="center", fontsize=8.5, color=C["mute"])
    ax.text(70, 8, "Launch at 1 ns, capture at 1.5 ns -> shortest window SW = 0.5 ns.     Setup check:  theta < SW - S - ISU",
            ha="center", fontsize=10, weight="bold")
    ax.text(70, 3, "ISU = inter-clock uncertainty (the two clocks can jitter against each other)", ha="center", fontsize=9, color=C["mute"])
    save(f, "pd11_multiple_clocks.png")


# ------------------------------------------------------------------ 12 slew
def d_slew():
    f, ax = fig(13.5, 6.8)
    title(ax, "Data slew (transition time): how fast a signal changes from 0 to 1", "every cell is characterised only for a range of slews, e.g. 20 ps <= slew <= 40 ps")
    for x0, w, lab, col in [(8, 6, "fast edge (OK)", C["g"]), (34, 14, "too slow (violation)", C["r"])]:
        ax.plot([x0, x0 + 4, x0 + 4 + w, x0 + 12 + w], [24, 24, 44, 44], color=col, lw=2)
        ax.plot([x0 + 4 + 0.1 * w, x0 + 4 + 0.1 * w], [20, 46], color=C["mute"], lw=0.6, ls=":")
        ax.plot([x0 + 4 + 0.9 * w, x0 + 4 + 0.9 * w], [20, 46], color=C["mute"], lw=0.6, ls=":")
        ax.text(x0 + 4 + w / 2, 15, lab, ha="center", fontsize=9, color=col)
    ax.text(31, 50, "slew = time from 10% to 90% of the swing", ha="center", fontsize=9)
    # inverter
    X = 92
    ax.plot([X, X], [52, 46], color=C["ink"]); ax.text(X, 53.5, "VDD", ha="center", fontsize=8.5)
    box(ax, X - 6, 38, 12, 8, "PMOS", fc=C["rose"], fs=8.5, r=0.2)
    ax.plot([X, X], [38, 34], color=C["ink"])
    box(ax, X - 6, 26, 12, 8, "NMOS", fc=C["blue"], fs=8.5, r=0.2)
    ax.plot([X, X], [26, 22], color=C["ink"]); ax.text(X, 19.5, "GND", ha="center", fontsize=8.5)
    ax.plot([X, X + 12], [36, 36], color=C["ink"]); ax.text(X + 13, 36, "out", va="center", fontsize=8.5)
    ax.plot([X - 6, X - 14, X - 14, X - 6], [42, 42, 30, 30], color=C["ink"]); ax.text(X - 15, 36, "in", ha="right", va="center", fontsize=8.5)
    ax.annotate("", xy=(X + 3, 23), xytext=(X + 3, 49), arrowprops=dict(arrowstyle="-|>", color=C["r"], lw=2))
    ax.text(X + 20, 30, "slow input:\nBOTH transistors\nare ON for longer\n-> short-circuit\ncurrent (wasted\npower, extra delay)", fontsize=8.6, color=C["r"])
    ax.text(68, 5, "If a slew is outside the allowed range, the tool adds or resizes buffers to make the edge sharp again.",
            ha="center", fontsize=9.5, color=C["mute"])
    ax.set_xlim(0, 136)
    save(f, "pd12_slew.png")


# ------------------------------------------------------------------ 13 skew + H-tree
def d_htree():
    f, ax = fig(14, 7.4)
    title(ax, "Clock skew and the H-tree", "skew = difference in clock arrival time between flops; we want it close to 0")
    # bad tree
    box(ax, 4, 18, 8, 6, "clk", fc=C["violet"], fs=9, r=0.2)
    box(ax, 22, 44, 8, 6, "FF1", fc=C["blue"], fs=9, r=0.2)
    box(ax, 56, 44, 8, 6, "FF2", fc=C["blue"], fs=9, r=0.2)
    ax.plot([12, 26, 26], [21, 21, 44], color=C["g"], lw=2)
    ax.plot([26, 60, 60], [21, 21, 44], color=C["r"], lw=2)
    ax.text(29, 32, "T1\n(short)", fontsize=8.5, color=C["g"])
    ax.text(62, 32, "T2\n(long)", fontsize=8.5, color=C["r"])
    ax.text(36, 10, "Skew = T2 - T1  (large: bad)", ha="center", fontsize=10, color=C["r"], weight="bold")
    # H tree
    cx, cy = 106, 30
    pts = [(cx - 16, cy + 12), (cx + 16, cy + 12), (cx - 16, cy - 12), (cx + 16, cy - 12)]
    ax.plot([cx - 16, cx + 16], [cy, cy], color=C["g"], lw=2)
    for sx in (-16, 16):
        ax.plot([cx + sx, cx + sx], [cy - 12, cy + 12], color=C["g"], lw=2)
    ax.plot([cx, cx], [cy, 8], color=C["g"], lw=2)
    box(ax, cx - 4, 2, 8, 6, "clk", fc=C["violet"], fs=9, r=0.2)
    for i, (x, y) in enumerate(pts):
        box(ax, x - 4, y - 3 + (3 if y > cy else -3), 8, 6, f"FF{i+1}", fc=C["blue"], fs=9, r=0.2)
    for x, y in [(cx, cy), (cx - 16, cy), (cx + 16, cy)]:
        ax.add_patch(plt.Polygon([[x - 1.6, y - 1.6], [x - 1.6, y + 1.6], [x + 1.8, y]], fc=C["amber"], ec=C["ink"], zorder=5))
    ax.text(cx, 56, "H-tree: always connect at the MID-POINT\nso every path to a flop has the same length", ha="center", fontsize=9.3, color=C["g"])
    ax.text(cx + 30, 18, "yellow = clock buffers\n(equal rise and fall time)\nkeep the edge sharp on\nlong, high-capacitance wires", fontsize=8.6)
    save(f, "pd13_skew_htree.png")


# ------------------------------------------------------------------ 14 crosstalk + shielding
def d_crosstalk():
    f, ax = fig(14, 7)
    title(ax, "Crosstalk and clock net shielding", "two wires next to each other form a small capacitor: a switching 'aggressor' disturbs a 'victim'")
    ax.plot([6, 60], [44, 44], color=C["r"], lw=3); ax.text(4, 44, "aggressor", ha="right", va="center", fontsize=8.5, color=C["r"])
    ax.plot([6, 60], [34, 34], color=C["b"], lw=3); ax.text(4, 34, "victim", ha="right", va="center", fontsize=8.5, color=C["b"])
    for x in (18, 33, 48):
        ax.plot([x - 2, x + 2], [40, 40], color=C["ink"], lw=1.5); ax.plot([x - 2, x + 2], [38, 38], color=C["ink"], lw=1.5)
        ax.plot([x, x], [44, 40], color=C["ink"], lw=0.8); ax.plot([x, x], [38, 34], color=C["ink"], lw=0.8)
    ax.text(33, 49, "coupling capacitance", ha="center", fontsize=8.5)
    ax.plot([8, 18, 19, 30, 31, 50], [18, 18, 26, 26, 26, 26], color=C["r"], lw=1.5)
    ax.plot([8, 18, 19.5, 22, 50], [14, 14, 18, 14, 14], color=C["b"], lw=1.5)
    ax.text(30, 8, "GLITCH: victim should stay 0 but\ngets a bump (can flip a flop)", ha="center", fontsize=8.6, color=C["b"])
    ax.text(30, 30, "", fontsize=1)
    # shielding
    ax.plot([80, 134], [48, 48], color=C["mute"], lw=3); ax.text(136, 48, "VDD shield", va="center", fontsize=8.5)
    ax.plot([80, 134], [40, 40], color=C["p"], lw=3); ax.text(136, 40, "CLOCK net", va="center", fontsize=8.5, color=C["p"], weight="bold")
    ax.plot([80, 134], [32, 32], color=C["mute"], lw=3); ax.text(136, 32, "GND shield", va="center", fontsize=8.5)
    ax.plot([80, 134], [22, 22], color=C["r"], lw=3); ax.text(136, 22, "other signal", va="center", fontsize=8.5, color=C["r"])
    ax.text(107, 12, "Shield wires are tied to VDD / GND, so they never switch.\nThey break the coupling between the clock and its neighbours.", ha="center", fontsize=8.8, color=C["g"])
    ax.text(107, 55, "Shield the critical nets (clock)", ha="center", weight="bold", color=C["g"])
    ax.set_xlim(-12, 152)
    save(f, "pd14_crosstalk_shielding.png")


# ------------------------------------------------------------------ 15 real clock STA
def d_realclk():
    f, ax = fig(14, 7.4)
    title(ax, "Setup check with a REAL clock (after CTS)", "the clock now travels through buffers 1-2 to the launch flop and 1-3-4 to the capture flop")
    box(ax, 30, 40, 12, 10, "Launch\nFF", fc=C["blue"], fs=9)
    ax.add_patch(matplotlib.patches.Ellipse((64, 45), 24, 9, fc=C["amber"], ec=C["ink"]))
    ax.text(64, 45, "theta", ha="center", va="center", fontsize=10)
    box(ax, 88, 40, 12, 10, "Capture\nFF", fc=C["blue"], fs=9)
    arrow(ax, 42, 45, 52, 45); arrow(ax, 76, 45, 88, 45)
    def buf(x, y, n):
        ax.add_patch(plt.Polygon([[x, y - 2], [x, y + 2], [x + 4, y]], fc=C["violet"], ec=C["ink"], zorder=4))
        ax.text(x + 1.5, y + 3.5, n, ha="center", fontsize=9, weight="bold", color=C["p"])
    ax.plot([6, 98], [22, 22], color=C["p"], lw=1.4)
    ax.text(5, 22, "clk", ha="right", va="center", fontsize=9)
    buf(14, 22, "1")
    ax.plot([24, 24, 36, 36], [22, 30, 30, 40], color=C["p"], lw=1.4); buf(24, 30, "2")
    buf(48, 22, "3"); buf(74, 22, "4")
    ax.plot([98, 98, 94, 94], [22, 30, 30, 40], color=C["p"], lw=1.4)
    ax.text(70, 12, "Delta1 = delay of buffers 1 + 2 (+ wires)      Delta2 = delay of buffers 1 + 3 + 4 (+ wires)", ha="center", fontsize=9.5)
    ax.text(70, 5, "(theta + Delta1)  <  (T + Delta2) - S - SU        data arrival time  <  data required time        skew = Delta1 - Delta2",
            ha="center", fontsize=9.8, weight="bold")
    ax.set_xlim(0, 140)
    save(f, "pd15_real_clock_setup.png")


# ------------------------------------------------------------------ 16 hold
def d_hold():
    f, ax = fig(13.5, 6.6)
    title(ax, "Setup vs hold: two different questions about the same path")
    box(ax, 4, 30, 60, 22, "", fc=C["amber"])
    ax.text(34, 48, "SETUP (max delay) check", ha="center", weight="bold")
    ax.text(34, 38, "Is the data FAST enough to reach the capture\nflop before the NEXT clock edge?\n(theta + D1) < (T + D2) - S - SU", ha="center", va="center", fontsize=9.2)
    box(ax, 72, 30, 60, 22, "", fc=C["green"])
    ax.text(102, 48, "HOLD (min delay) check", ha="center", weight="bold")
    ax.text(102, 38, "Is the data SLOW enough not to disturb what the\ncapture flop is holding at the SAME edge?\n(theta + D1) > (H + D2) + HU", ha="center", va="center", fontsize=9.2)
    ax.text(68, 20, "Setup slack = data required time - data arrival time        Hold slack = data arrival time - data required time",
            ha="center", fontsize=9.6)
    ax.text(68, 13, "Both slacks must be zero or positive. Negative slack = violation.", ha="center", fontsize=9.6, color=C["r"], weight="bold")
    ax.text(68, 6, "H = hold time of the capture flop (it must keep sending out its current data a little after the edge).  HU = hold uncertainty.",
            ha="center", fontsize=9, color=C["mute"])
    ax.set_xlim(0, 136)
    save(f, "pd16_setup_vs_hold.png")


# ------------------------------------------------------------------ 17 Lee's algorithm
def lee_grid():
    W, H = 10, 8
    block = {(x, y) for x in range(3, 6) for y in range(2, 6)} | {(7, 5), (7, 6), (8, 5)}
    S, T = (1, 3), (8, 2)
    dist = {S: 0}
    q = deque([S])
    while q:
        c = q.popleft()
        if c == T:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in block and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    # backtrace preferring to keep direction (fewer bends)
    path = [T]; cur = T; d_prev = None
    while cur != S:
        cands = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cur[0] + dx, cur[1] + dy)
            if dist.get(n, 1e9) == dist[cur] - 1:
                cands.append(((dx, dy) != d_prev, (dx, dy), n))
        cands.sort()
        _, d_prev, cur = cands[0]
        path.append(cur)
    return W, H, block, S, T, dist, path


def d_lee():
    W, H, block, S, T, dist, path = lee_grid()
    f, ax = fig(13.5, 7.4)
    title(ax, "Maze routing with Lee's algorithm", "1) label cells outward from S (1, 2, 3 ...) like a wave   2) when T is reached, trace back through decreasing numbers")
    for k, (x0, show_path) in enumerate([(6, False), (74, True)]):
        u = 6
        for x in range(W):
            for y in range(H):
                X, Y = x0 + x * u, 8 + y * u
                fc = "white"
                if (x, y) in block: fc = "#9ca3af"
                if show_path and (x, y) in path: fc = C["green"]
                if (x, y) == S: fc = C["b"]
                if (x, y) == T: fc = C["r"]
                ax.add_patch(Rectangle((X, Y), u, u, fc=fc, ec=C["mute"], lw=0.6))
                lab = ""
                if (x, y) == S: lab = "S"
                elif (x, y) == T: lab = "T"
                elif (x, y) in dist and dist[(x, y)] <= dist[T]: lab = str(dist[(x, y)])
                if lab:
                    ax.text(X + u / 2, Y + u / 2, lab, ha="center", va="center", fontsize=8.5,
                            color="white" if lab in ("S", "T") else C["ink"], weight="bold" if lab in ("S", "T") else "normal")
        ax.text(x0 + W * u / 2, 4, "after the wave reaches T (distance %d)" % dist[T] if not show_path else
                "back-trace: choose the route with the fewest bends (L-shapes)", ha="center", fontsize=9)
    ax.text(68, 61, "grey = blocked (pre-placed macro) - the router cannot pass through it", ha="center", fontsize=9, color=C["mute"])
    ax.set_xlim(0, 140)
    save(f, "pd17_lee_algorithm.png")


# ------------------------------------------------------------------ 18 DRC
def d_drc():
    f, ax = fig(14, 6.6)
    title(ax, "Design rules (DRC): the factory's rules for drawing wires", "breaking a rule means the wire may not be manufactured correctly")
    # width
    ax.add_patch(Rectangle((6, 30), 24, 4, fc=C["b"]))
    ax.annotate("", xy=(33, 30), xytext=(33, 34), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(18, 22, "1. Minimum wire WIDTH\n(too thin -> may break)", ha="center", fontsize=8.8)
    # spacing
    ax.add_patch(Rectangle((42, 36), 24, 4, fc=C["b"])); ax.add_patch(Rectangle((42, 28), 24, 4, fc=C["b"]))
    ax.annotate("", xy=(69, 32), xytext=(69, 36), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(54, 22, "2. Minimum wire SPACING\n(too close -> may short)", ha="center", fontsize=8.8)
    # pitch
    ax.add_patch(Rectangle((78, 36), 4, 16, fc=C["b"])); ax.add_patch(Rectangle((88, 36), 4, 16, fc=C["b"]))
    ax.annotate("", xy=(80, 33), xytext=(90, 33), arrowprops=dict(arrowstyle="<->", lw=1))
    ax.text(85, 22, "3. Wire PITCH\n= centre to centre", ha="center", fontsize=8.8)
    # via
    ax.add_patch(Rectangle((102, 30), 30, 5, fc=C["b"], alpha=0.8))
    ax.add_patch(Rectangle((114, 22), 5, 22, fc=C["o"], alpha=0.8))
    ax.add_patch(Rectangle((114.5, 30.5), 4, 4, fc=C["ink"]))
    ax.text(117, 14, "4. Signal short -> move one wire to\nanother metal layer and join with a VIA\n(via width and via spacing rules too)", ha="center", fontsize=8.8)
    ax.text(70, 5, "After routing, the design must be 'DRC clean'. Then the real wires' R and C are extracted for final timing.",
            ha="center", fontsize=9.3, color=C["mute"])
    ax.set_xlim(0, 140)
    save(f, "pd18_drc_rules.png")


# ------------------------------------------------------------------ 19 SPEF net
def d_spef():
    f, ax = fig(14, 7.2)
    title(ax, "Parasitic extraction: a real wire becomes a chain of resistors and capacitors", "this R-C network is written in a SPEF file (IEEE 1481-1999) for the timing tool")
    box(ax, 4, 34, 12, 10, "driver\n(U1:Z)", fc=C["blue"], fs=8.5)
    box(ax, 120, 34, 14, 10, "load\n(U2:A)", fc=C["blue"], fs=8.5)
    xs = [16, 44, 72, 100, 120]
    for i in range(4):
        a, b = xs[i], xs[i + 1]
        m = (a + b) / 2
        ax.plot([a, m - 6], [39, 39], color=C["ink"])
        ax.plot([m + 6, b], [39, 39], color=C["ink"])
        zz_x = [m - 6, m - 4, m - 2, m, m + 2, m + 4, m + 6]
        ax.plot(zz_x, [39, 41, 37, 41, 37, 41, 39], color=C["r"], lw=1.5)
        ax.text(m, 43, f"R{i+1}", ha="center", fontsize=8.5, color=C["r"])
    for i, x in enumerate(xs[1:4]):
        ax.plot([x, x], [39, 33], color=C["ink"])
        ax.plot([x - 3, x + 3], [33, 33], color=C["b"], lw=2.5); ax.plot([x - 3, x + 3], [31, 31], color=C["b"], lw=2.5)
        ax.plot([x, x], [31, 27], color=C["ink"]); ax.plot([x - 2.5, x + 2.5], [27, 27], color=C["ink"])
        ax.text(x + 4, 32, f"C{i+1}", fontsize=8.5, color=C["b"])
        ax.add_patch(Circle((x, 39), 0.9, fc=C["ink"]))
        ax.text(x, 46.5, f"node {i+1}", ha="center", fontsize=8, color=C["mute"])
    spef = ("*D_NET net1 0.35      <- net name, total capacitance\n"
            "*CONN\n*I U1:Z O            <- driver pin (output)\n*I U2:A I            <- load pin (input)\n"
            "*CAP\n1 net1:1 0.10\n2 net1:2 0.12\n3 net1:3 0.13\n"
            "*RES\n1 U1:Z net1:1 2.0\n2 net1:1 net1:2 3.0\n3 net1:2 net1:3 3.0\n4 net1:3 U2:A 2.0\n*END")
    ax.text(30, 22, spef, va="top", fontsize=8.2, family="DejaVu Sans Mono")
    ax.text(110, 18, "One *D_NET section per net.\n*CONN = pins on the net,\n*CAP = capacitors to ground,\n*RES = resistors between nodes.\nUnits come from the header\n(*C_UNIT, *R_UNIT).", fontsize=8.8, va="top")
    ax.set_xlim(0, 140)
    save(f, "pd19_spef_net.png")


if __name__ == "__main__":
    for fn in [d_flow, d_uf_ar, d_preplaced, d_decap, d_power, d_pins, d_binding, d_repeaters, d_setup,
               d_jitter, d_multiclk, d_slew, d_htree, d_crosstalk, d_realclk, d_hold, d_lee, d_drc, d_spef]:
        fn()
    print("written to", os.path.abspath(OUT))

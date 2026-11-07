# Day 05 — Route, DRC Clean, Parasitics Extraction, Final STA

> **Course:** Section 1: Physical Design Flow Overview &nbsp;|&nbsp; **Lecture 5** &nbsp;|&nbsp; [VLSI Academy — Physical Design Flow (Udemy)](https://www.udemy.com/course/vlsi-academy-physical-design-flow/)  
> **Notes source:** your handwritten notes + the lecture topic

## Step 9a: Routing — real wires

Until now, wires were only **estimated**. **Routing** draws the **real metal wires** that connect every pin to every other pin, using several metal layers stacked on top of each other.

## Step 9b: DRC clean

The factory has **design rules** — minimum wire width, minimum spacing between wires, how vias (connections between layers) must look. **DRC (Design Rule Check)** checks that the layout follows all of them. The layout must be **DRC clean** (zero violations) before it can be made.

## Step 10a: Parasitic extraction

Real wires have **resistance (R)** and **capacitance (C)** — called **parasitics** because they are unwanted side effects. Extraction calculates the R and C of every wire and writes them to a file (**SPEF**).

## Step 10b: Final STA

**Static Timing Analysis** is run one last time, now **with the real wires' R and C** (your notes: *timing analysis — as now we have real wires*). If all timing checks pass (positive slack), the design is ready for **sign-off** and the layout is sent to the factory.

## The whole flow, as written in your notes

(Your notes number the steps slightly differently from the diagram — the order is the same.)

```
Step 1  bind the netlist with physical cells
Step 2  placement
Step 3  optimised placement (estimate wire length & capacitance, insert repeaters)
Step 4  timing analysis with ideal clock (trace data path, check slew)
Step 5  clock tree analysis (is the clock reaching the required flip-flops?)
Step 6  clock net shielding (protect the clock from crosstalk)
Step 7  timing analysis with real clock
Step 8  routing -> real wires
Step 9  DRC -> clean (design rule check)
Step 10 parasitic extraction -> timing analysis (now with real wires)
```

## Key points

- Routing creates the real wires; DRC makes sure the factory can build them.
- Extraction gives the real R and C of each wire (SPEF file).
- Final STA with real parasitics decides if the chip meets its speed.

## Practice Questions

1. What is the difference between estimated wires and routed wires?
2. What does "DRC clean" mean?
3. What are parasitics?
4. Why is timing checked again after extraction?

**Answers**

1. Estimated wires are guesses used during placement; routed wires are the real metal shapes.
2. The layout has zero design-rule violations.
3. The unwanted resistance and capacitance of real wires.
4. Real wires' R and C change the delays; only now is the timing accurate.

---
[⬅ Day 04](../Day-04-Clock-Net-Shielding/README.md) | [Index](../README.md) | [Day 06 ➡](../Day-06-Utilization-Factor-and-Aspect-Ratio/README.md)

# Day 06 — Utilization Factor and Aspect Ratio

> **Course:** Section 2: Floorplanning &nbsp;|&nbsp; **Lecture 6** &nbsp;|&nbsp; [VLSI Academy — Physical Design Flow (Udemy)](https://www.udemy.com/course/vlsi-academy-physical-design-flow/)  
> **Notes source:** your handwritten notes + the lecture topic

## Defining the width and height of the core and die

The very first floorplanning decision: **how big is the chip?** For this step we are interested only in the **size of the cells**; we **ignore the wires** at first (your notes).

### Start from the cells

From your notes: say we have **4 components**, each a square of **1 unit × 1 unit = 1 square unit**. All 4 together need **at least 4 square units**.

### What is a die?

On a **silicon wafer** (a big round disc) many chips are made at once. A **die** is one small piece of semiconductor cut from the wafer, **on which the circuit is fabricated**. The **core** is the inner part of the die where the logic sits.

## Utilisation factor (UF)

```
                        area occupied by the netlist
Utilisation factor  =  ------------------------------
                           total area of the core
```

- If the 4 sq. units of cells sit in a **4 sq. unit core**, UF = 4/4 = **1 → 100% utilisation**. The core is completely full.
- **Ideally**, utilisation is **50–60% (UF = 0.5–0.6)** (your notes).

**Why not 100%?** The free space is needed later for **buffers/repeaters**, **wires**, **clock-tree buffers** and small fixes. A 100% full core has no room for any of these. It's like packing a suitcase completely full — you can't add anything later.

## Aspect ratio (AR)

```
                   height of the core
Aspect ratio  =  ----------------------
                    width of the core
```

- **AR = 1** → the core is a **square**.
- AR ≠ 1 → a **rectangle**.

![Utilisation factor and aspect ratio](../diagrams/pd02_uf_ar.png)

### Worked example (from your notes)

The 4 cells (FF, FF, AND, OR) placed in a core **4 units wide × 2 units high**:

- Core area = 4 × 2 = 8 sq. units
- UF = 4 / 8 = **0.5**
- AR = 2 / 4 = **0.5**

### More examples

| Core (W × H) | Core area | UF | AR | Shape |
|---|---|---|---|---|
| 2 × 2 | 4 | 4/4 = 1.0 | 1.0 | square, completely full |
| 4 × 1 | 4 | 1.0 | 0.25 | thin rectangle, full |
| 4 × 2 | 8 | 0.5 | 0.5 | rectangle, half full |
| 3 × 3 | 9 | 0.44 | 1.0 | square, room to spare |

## Key points

- UF = cell area / core area; aim for about **0.5–0.6**.
- AR = height / width; **1 = square**.
- Size the core from the cell area plus free space for buffers and wires.

## Practice Questions

1. 6 cells of 1 sq. unit each are placed in a 4 × 3 core. Find UF and AR.
2. Why is 100% utilisation not used in real designs?
3. A core is 10 µm wide with AR = 0.5. How high is it?

**Answers**

1. UF = 6/12 = 0.5; AR = 3/4 = 0.75.
2. There would be no room left for buffers, repeaters, clock-tree cells and routing.
3. Height = 0.5 × 10 = 5 µm.

---
[⬅ Day 05](../Day-05-Route-DRC-Clean-Parasitics-Extraction-Final-STA/README.md) | [Index](../README.md) | [Day 07 ➡](../Day-07-Concept-of-Pre-Placed-Cells/README.md)

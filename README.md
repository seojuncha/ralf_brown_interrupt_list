# Ralf Brown's Interrupt List — Table Edition (PDF)

A structured, table-formatted PDF reference compiled from **Ralf Brown's Interrupt List (RBIL)**, the most comprehensive documentation of IBM PC interrupt calls ever assembled.

## Contents

The PDF covers the following sections:

| Section | Description |
|---------|-------------|
| 1. Master Interrupt Vector Table | INT 00h–77h — BIOS, IRQ, DOS, EMS, DPMI vectors |
| 2. INT 10h — Video Services | BIOS video sub-functions (AH=00h–4Fh, incl. VESA VBE) |
| 3. INT 13h — Disk Services | CHS and Extended LBA disk sub-functions |
| 4. INT 21h — DOS Function Dispatcher | 50+ DOS API sub-functions (AH=00h–68h) |
| 5. DOS Extended Error Codes | INT 21h AH=59h return values |

## Usage

This document is intended as a **quick-reference cheat sheet** for developers, hobbyists, and students working with DOS, BIOS, or low-level x86 programming.

- Download `ralf_brown_interrupt_list.pdf` from this repository.
- No installation required — open with any PDF viewer.

## Regenerating the PDF

The PDF is generated from a Python script using [ReportLab](https://www.reportlab.com/).

**Requirements**

```
pip install reportlab
```

**Run**

```
python make_interrupt_pdf.py
```

## Original Source

The data in this document is derived from **Ralf Brown's Interrupt List**, version 61 (2000).

- Homepage: http://www.cs.cmu.edu/~ralf/files.html
- Mirror: http://www.ctyme.com/rbrown.htm

All credit for the original research and documentation goes to **Ralf Brown**.

## License

See [NOTICE](./NOTICE.txt) for copyright and redistribution terms.

The Python source code in this repository is released under the **MIT License**.  
The compiled PDF and its contents are derived from RBIL and are subject to Ralf Brown's original copyright — see NOTICE for details.

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Try to register a CJK-capable font if available
try:
    pdfmetrics.registerFont(TTFont('NotoSans', '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'))
    MAIN_FONT = 'NotoSans'
except:
    MAIN_FONT = 'Helvetica'

OUTPUT_PATH = "/mnt/user-data/outputs/ralf_brown_interrupt_list.pdf"

# ── Data ──────────────────────────────────────────────────────────────────────
# Each entry: (INT hex, Function, Description)
interrupt_data = [
    # INT 00h - 1Fh  (BIOS / CPU)
    ("00h", "CPU Divide Error", "Division by zero or quotient overflow."),
    ("01h", "CPU Single Step", "Debug single-step trap (TF flag set)."),
    ("02h", "NMI", "Non-Maskable Interrupt (hardware error / parity)."),
    ("03h", "CPU Breakpoint", "INT 3 one-byte breakpoint instruction."),
    ("04h", "CPU Overflow", "INTO instruction when OF flag is set."),
    ("05h", "BIOS Print Screen", "Print screen / bound range exceeded (80286+)."),
    ("06h", "CPU Invalid Opcode", "Undefined opcode exception (80286+)."),
    ("07h", "CPU No Math Coprocessor", "No FPU / device-not-available exception."),
    ("08h", "IRQ0 – System Timer", "Hardware timer tick (18.2 Hz). Calls INT 1Ch."),
    ("09h", "IRQ1 – Keyboard", "Key pressed/released; BIOS puts scancode in buffer."),
    ("0Ah", "IRQ2 – Cascade / EGA", "Cascaded IRQ line or EGA vertical retrace."),
    ("0Bh", "IRQ3 – COM2 / COM4", "Serial port 2 / 4 interrupt."),
    ("0Ch", "IRQ4 – COM1 / COM3", "Serial port 1 / 3 interrupt."),
    ("0Dh", "IRQ5 – LPT2 / XT Hard Disk", "Parallel port 2 or XT hard-disk controller."),
    ("0Eh", "IRQ6 – Floppy Disk", "Floppy disk controller operation complete."),
    ("0Fh", "IRQ7 – LPT1 / Spurious", "Parallel port 1 / spurious 8259 interrupt."),
    ("10h", "BIOS Video Services", "Comprehensive video I/O (set mode, cursor, scroll, write char, palette…)."),
    ("11h", "BIOS Equipment List", "Returns AX = installed-equipment bit flags."),
    ("12h", "BIOS Memory Size", "Returns AX = conventional memory in KB (max 640)."),
    ("13h", "BIOS Disk Services", "Low-level disk read/write/verify/format (floppy & hard disk)."),
    ("14h", "BIOS Serial Port Services", "Init, transmit, receive, get status for COM1–COM4."),
    ("15h", "BIOS System Services", "Cassette (XT), A20, extended memory (AH=87h/88h), APM, PnP, CD-ROM…"),
    ("16h", "BIOS Keyboard Services", "Read key, check keystroke, get shift status, set typematic rate."),
    ("17h", "BIOS Printer Services", "Print character, init printer, get printer status."),
    ("18h", "BIOS ROM BASIC Entry", "Jump to ROM BASIC (or 'No ROM BASIC' message on clones)."),
    ("19h", "BIOS Bootstrap Loader", "Reboot (warm): reload boot sector from disk."),
    ("1Ah", "BIOS Time-of-Day", "Get/set clock ticks, get/set RTC date & time, alarm, PCI BIOS."),
    ("1Bh", "BIOS Ctrl-Break Handler", "Called by INT 09h when Ctrl-Break is detected."),
    ("1Ch", "BIOS Timer Tick User Hook", "Called 18.2 times/sec by INT 08h; user-installable hook."),
    ("1Dh", "Video Parameter Table Ptr", "Pointer to video init parameter table (not callable)."),
    ("1Eh", "Floppy Parameter Table Ptr", "Pointer to floppy disk base parameter table (not callable)."),
    ("1Fh", "Video Graphics Chars Ptr", "Pointer to 8x8 graphics character table (chars 80h–FFh)."),

    # INT 20h–2Fh  (DOS)
    ("20h", "DOS Program Terminate", "Terminate current process (COM programs; returns to parent)."),
    ("21h", "DOS Function Dispatcher", "Primary DOS API: AH = function number. File I/O, memory, process, time, etc."),
    ("22h", "DOS Terminate Address", "Segment:Offset of code to receive control on program exit."),
    ("23h", "DOS Ctrl-C Handler", "Called when Ctrl-C / Ctrl-Break detected during DOS call."),
    ("24h", "DOS Critical Error Handler", "Called on hardware errors (disk not ready, write protect, etc.)."),
    ("25h", "DOS Absolute Disk Read", "Read sectors directly from a logical drive."),
    ("26h", "DOS Absolute Disk Write", "Write sectors directly to a logical drive."),
    ("27h", "DOS TSR (Keep Process)", "Terminate and Stay Resident (old method; use INT 21h/31h)."),
    ("28h", "DOS Idle Hook", "Called repeatedly by DOS when idle (during INT 21h input wait)."),
    ("29h", "DOS Fast Console Output", "Fast character output used by COMMAND.COM (AL = char)."),
    ("2Ah", "DOS Network / Critical Section", "Microsoft Network (INT 2Ah) and critical-section hooks."),
    ("2Fh", "DOS Multiplex Interrupt", "Inter-process communication: PRINT, APPEND, DOSKEY, MSCDEX, DPMI…"),

    # INT 31h  (DPMI)
    ("31h", "DPMI Services", "DOS Protected-Mode Interface: alloc/free selectors & memory, real-mode calls, exceptions."),

    # INT 33h  (Mouse)
    ("33h", "Mouse Driver Services", "Mouse reset, show/hide cursor, get position & buttons, set callbacks."),

    # INT 40h–4Fh
    ("40h", "BIOS Floppy Redirect (XT HD)", "On XT systems with hard disk, original INT 13h floppy handler moved here."),
    ("41h", "Hard Disk 0 Parameter Table", "Pointer to Fixed Disk Parameter Table for drive 0."),
    ("46h", "Hard Disk 1 Parameter Table", "Pointer to Fixed Disk Parameter Table for drive 1."),
    ("4Ah", "RTC Alarm / User Alarm", "Called by BIOS when real-time clock alarm fires (also INT 1Ah/AH=06h)."),
    ("4Bh", "Virtual DMA Services (VDS)", "DMA buffer locking/unlocking for bus-master devices under protected mode."),

    # INT 60h–67h  (User/Network/EMS)
    ("60h–66h", "User / Application Vectors", "Reserved for application or hardware use; commonly used by TSRs."),
    ("67h", "LIM EMS 4.0 Services", "Expanded Memory Specification: alloc/free pages, map windows, move/exchange regions."),

    # INT 70h–77h  (IRQ8–IRQ15, AT)
    ("70h", "IRQ8 – RTC", "Real-time clock periodic interrupt / alarm (AT and above)."),
    ("71h", "IRQ9 – Redirect to IRQ2", "Redirected to INT 0Ah for backward compatibility."),
    ("72h", "IRQ10 – Reserved", "Available hardware IRQ (NIC, SCSI, sound card…)."),
    ("73h", "IRQ11 – Reserved", "Available hardware IRQ."),
    ("74h", "IRQ12 – PS/2 Mouse", "PS/2 auxiliary port (mouse) interrupt."),
    ("75h", "IRQ13 – Math Coprocessor", "FPU error interrupt; redirects to INT 02h."),
    ("76h", "IRQ14 – Primary IDE", "Primary IDE / hard disk controller interrupt."),
    ("77h", "IRQ15 – Secondary IDE", "Secondary IDE controller interrupt."),
]

# ── Selected INT 21h sub-function highlights ─────────────────────────────────
dos21_data = [
    ("00h", "Terminate Program", "Terminate (COM); superseded by AH=4Ch."),
    ("01h", "Character Input with Echo", "Read char from stdin with echo; handles Ctrl-C."),
    ("02h", "Character Output", "Write char in DL to stdout."),
    ("05h", "Printer Output", "Send char to LPT1."),
    ("06h", "Direct Console I/O", "Direct console input/output, no Ctrl-C check."),
    ("08h", "Console Input without Echo", "Read char, no echo."),
    ("09h", "Display String", "Print '$'-terminated string at DS:DX."),
    ("0Ah", "Buffered Keyboard Input", "Read line into buffer; DS:DX -> buffer descriptor."),
    ("0Bh", "Check Standard Input Status", "AL=FFh if char waiting, else AL=00h."),
    ("0Ch", "Flush Buffer / Read Keyboard", "Flush input buffer then call AH sub-function."),
    ("0Dh", "Disk Reset", "Flush all dirty disk buffers."),
    ("0Eh", "Select Default Drive", "Set default drive (DL=0=A, 1=B, …); returns drive count."),
    ("19h", "Get Current Default Drive", "Returns AL = current drive number."),
    ("1Ah", "Set Disk Transfer Area (DTA)", "DS:DX = new DTA address."),
    ("25h", "Set Interrupt Vector", "AL=int#, DS:DX=handler; installs interrupt vector."),
    ("2Ah", "Get System Date", "CX=year, DH=month, DL=day, AL=day-of-week."),
    ("2Bh", "Set System Date", "CX=year, DH=month, DL=day."),
    ("2Ch", "Get System Time", "CH=hr, CL=min, DH=sec, DL=1/100 sec."),
    ("2Dh", "Set System Time", "CH=hr, CL=min, DH=sec, DL=1/100 sec."),
    ("2Fh", "Get DTA Address", "ES:BX = current DTA address."),
    ("30h", "Get DOS Version", "AL=major, AH=minor version; BH=OEM ID."),
    ("31h", "Terminate and Stay Resident", "AL=return code, DX=paragraphs to keep."),
    ("35h", "Get Interrupt Vector", "AL=int#; returns ES:BX = current handler."),
    ("36h", "Get Free Disk Space", "DL=drive; AX=sects/cluster, BX=free clusters, CX=bytes/sect, DX=total clusters."),
    ("38h", "Get/Set Country Info", "Country code, currency, date/time format, etc."),
    ("39h", "Create Directory (mkdir)", "DS:DX = ASCIZ path."),
    ("3Ah", "Remove Directory (rmdir)", "DS:DX = ASCIZ path."),
    ("3Bh", "Change Current Directory (cd)", "DS:DX = ASCIZ path."),
    ("3Ch", "Create/Truncate File", "DS:DX = name, CX = attr; AX = file handle."),
    ("3Dh", "Open File", "DS:DX = name, AL = access mode; AX = handle."),
    ("3Eh", "Close File Handle", "BX = handle."),
    ("3Fh", "Read from File/Device", "BX=handle, CX=bytes, DS:DX=buffer; AX=bytes read."),
    ("40h", "Write to File/Device", "BX=handle, CX=bytes, DS:DX=buffer; AX=bytes written."),
    ("41h", "Delete File (unlink)", "DS:DX = ASCIZ filename."),
    ("42h", "Move File Pointer (lseek)", "BX=handle, AL=origin, CX:DX=offset; DX:AX=new pos."),
    ("43h", "Get/Set File Attributes", "AL=0 get / AL=1 set; DS:DX=name, CX=attributes."),
    ("44h", "I/O Control (IOCTL)", "Sub-functions for device info, raw I/O, drive info, etc."),
    ("45h", "Duplicate File Handle (dup)", "BX=handle; AX=new handle sharing same file pos."),
    ("46h", "Force Duplicate Handle (dup2)", "BX=old, CX=new; redirects CX to same file as BX."),
    ("47h", "Get Current Directory", "DL=drive, DS:SI=64-byte buffer; returns path."),
    ("48h", "Allocate Memory", "BX=paragraphs; AX=segment of allocated block."),
    ("49h", "Free Memory Block", "ES=segment to free."),
    ("4Ah", "Resize Memory Block", "ES=segment, BX=new size in paragraphs."),
    ("4Bh", "Execute Program (EXEC)", "DS:DX=name, ES:BX=param block; loads & optionally runs."),
    ("4Ch", "Terminate with Return Code", "AL = exit code. Most common way to exit."),
    ("4Dh", "Get Return Code of Child", "AH=termination type, AL=child exit code."),
    ("4Eh", "Find First Matching File", "DS:DX=filespec, CX=attr; fills DTA with first match."),
    ("4Fh", "Find Next Matching File", "Continue search started by AH=4Eh."),
    ("56h", "Rename/Move File", "DS:DX=old name, ES:DI=new name."),
    ("57h", "Get/Set File Date & Time", "BX=handle, AL=0 get / AL=1 set; CX=time, DX=date."),
    ("5Ah", "Create Temporary File", "DS:DX=path; creates unique file, returns handle."),
    ("5Bh", "Create New File", "DS:DX=name; fails if file already exists."),
    ("5Ch", "Lock/Unlock File Region", "AL=0 lock / AL=1 unlock; network file sharing."),
    ("5Eh", "Network / Printer Functions", "Machine name, printer setup string, etc."),
    ("62h", "Get PSP Address", "BX = segment of current Program Segment Prefix."),
    ("65h", "Get Extended Country Info", "International info: collate table, DBCS lead-byte table."),
    ("67h", "Set Handle Count", "BX = max open handles for this process."),
    ("68h", "Flush/Commit File", "BX = handle; forces write-through to disk."),
]

# ── PDF Build ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=15*mm, bottomMargin=15*mm,
    title="Ralf Brown's Interrupt List",
    author="Compiled Reference",
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'Title2', parent=styles['Title'],
    fontName=MAIN_FONT, fontSize=20, spaceAfter=6,
    textColor=colors.HexColor('#1a237e'),
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName=MAIN_FONT, fontSize=13, spaceBefore=10, spaceAfter=4,
    textColor=colors.HexColor('#283593'),
    borderPad=2,
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName=MAIN_FONT, fontSize=11, spaceBefore=8, spaceAfter=3,
    textColor=colors.HexColor('#1565c0'),
)
body_style = ParagraphStyle(
    'Body2', parent=styles['Normal'],
    fontName=MAIN_FONT, fontSize=8.5, leading=12,
)
caption_style = ParagraphStyle(
    'Caption', parent=styles['Normal'],
    fontName=MAIN_FONT, fontSize=7.5, leading=10,
    textColor=colors.HexColor('#555555'),
)

def make_table(data_rows, col_widths, header):
    """Build a styled Table from header + rows."""
    all_rows = [header] + data_rows
    tbl = Table(all_rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header
        ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), MAIN_FONT),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('ALIGN',       (0,0), (-1,0), 'CENTER'),
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING',(0,0),(-1,0), 5),
        ('TOPPADDING',  (0,0),(-1,0), 5),
        # Data rows
        ('FONTNAME',    (0,1), (-1,-1), MAIN_FONT),
        ('FONTSIZE',    (0,1), (-1,-1), 8),
        ('LEADING',     (0,1), (-1,-1), 11),
        ('TOPPADDING',  (0,1), (-1,-1), 3),
        ('BOTTOMPADDING',(0,1),(-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING',(0,0), (-1,-1), 5),
        # Alternating rows
        *[('BACKGROUND', (0,i), (-1,i), colors.HexColor('#e8eaf6'))
          for i in range(2, len(all_rows), 2)],
        # Grid
        ('GRID',        (0,0), (-1,-1), 0.4, colors.HexColor('#9fa8da')),
        ('LINEBELOW',   (0,0), (-1,0), 1.2, colors.HexColor('#283593')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#e8eaf6')]),
    ]))
    return tbl

story = []

# ── Title Page ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 20*mm))
story.append(Paragraph("Ralf Brown's Interrupt List", title_style))
story.append(Paragraph("PC Interrupt Quick Reference — Table Edition", h2_style))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "Ralf Brown's Interrupt List (RBIL) is the most comprehensive reference for IBM PC "
    "interrupt calls, covering BIOS, DOS, hardware IRQs, and third-party extensions. "
    "This document presents a structured tabular summary of the most commonly used "
    "interrupt vectors and their sub-functions.",
    body_style
))
story.append(Spacer(1, 6*mm))

# ── Section 1: Master Interrupt Vector Table ──────────────────────────────────
story.append(Paragraph("1. Master Interrupt Vector Table", h1_style))
story.append(Paragraph(
    "The table below lists the primary interrupt vectors (INT 00h–77h) "
    "recognised by standard PC BIOS/DOS environments.",
    body_style
))
story.append(Spacer(1, 3*mm))

W = A4[0] - 30*mm   # usable width
col_w = [18*mm, 52*mm, W - 18*mm - 52*mm]
header_row = [
    Paragraph("<b>INT #</b>", caption_style),
    Paragraph("<b>Function / Name</b>", caption_style),
    Paragraph("<b>Description</b>", caption_style),
]
data_rows = [
    [Paragraph(r[0], caption_style),
     Paragraph(r[1], caption_style),
     Paragraph(r[2], caption_style)]
    for r in interrupt_data
]
story.append(make_table(data_rows, col_w, header_row))

# ── Section 2: INT 10h Video Sub-functions ────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("2. INT 10h — BIOS Video Services (AH sub-functions)", h1_style))
story.append(Paragraph(
    "INT 10h is the BIOS video interrupt. The sub-function is selected by AH. "
    "Extended functions (AH=10h–13h) support EGA/VGA palette, display combinations, and string output.",
    body_style
))
story.append(Spacer(1, 3*mm))

video_data = [
    ("00h", "Set Video Mode", "AL = mode (00h=40x25 text, 03h=80x25 color text, 13h=320x200x256…)"),
    ("01h", "Set Cursor Shape", "CH=start scan line, CL=end scan line."),
    ("02h", "Set Cursor Position", "BH=page, DH=row, DL=column."),
    ("03h", "Get Cursor Position & Shape", "BH=page; returns DH=row, DL=col, CH/CL=shape."),
    ("04h", "Read Light Pen Position", "Returns light pen data (obsolete)."),
    ("05h", "Select Active Display Page", "AL = page number (0–7 for text)."),
    ("06h", "Scroll Window Up", "AL=lines (0=clear), BH=attr, CH/CL=upper-left, DH/DL=lower-right."),
    ("07h", "Scroll Window Down", "Same parameters as AH=06h but scrolls opposite direction."),
    ("08h", "Read Char & Attr at Cursor", "BH=page; returns AH=attr, AL=char."),
    ("09h", "Write Char & Attr at Cursor", "BH=page, BL=attr, AL=char, CX=count."),
    ("0Ah", "Write Char Only at Cursor", "BH=page, AL=char, CX=count (keeps existing attribute)."),
    ("0Bh", "Set Color Palette / Background", "BH=0: set background; BH=1: select CGA palette."),
    ("0Ch", "Write Graphics Pixel", "BH=page, AL=color, CX=column, DX=row."),
    ("0Dh", "Read Graphics Pixel", "BH=page, CX=column, DX=row; AL=color."),
    ("0Eh", "Teletype Output (TTY)", "AL=char, BH=page, BL=fg color (graphics mode); advances cursor."),
    ("0Fh", "Get Current Video Mode", "AH=columns, AL=mode, BH=active page."),
    ("10h", "Set/Get Palette Registers (EGA+)", "Sub-AH: set individual, all, overscan, blink/intensity toggle."),
    ("11h", "Character Generator (EGA+)", "Load user font, set block specifier, select font."),
    ("12h", "Alternate Select (EGA+)", "BL=10h: get EGA config; BL=20h: select alternate print screen."),
    ("13h", "Write String", "AL=mode, BH=page, BL=attr, CX=len, DH/DL=row/col, ES:BP=string."),
    ("1Ah", "Display Combination Code (VGA)", "AL=00h get / AL=01h set display combination."),
    ("1Bh", "Functionality/State Info (VGA)", "ES:DI = 64-byte buffer for state table."),
    ("1Ch", "Save/Restore Video State (VGA)", "CX=flags, AL=00h size / 01h save / 02h restore."),
    ("4Fh", "VESA BIOS Extensions (VBE)", "AL: 00h info, 01h mode info, 02h set mode, 03h get mode, 05h window, 07h display start…"),
]

col_v = [16*mm, 52*mm, W - 16*mm - 52*mm]
header_v = [
    Paragraph("<b>AH</b>", caption_style),
    Paragraph("<b>Function</b>", caption_style),
    Paragraph("<b>Parameters / Notes</b>", caption_style),
]
rows_v = [[Paragraph(r[0], caption_style), Paragraph(r[1], caption_style), Paragraph(r[2], caption_style)] for r in video_data]
story.append(make_table(rows_v, col_v, header_v))

# ── Section 3: INT 13h Disk Services ─────────────────────────────────────────
story.append(Spacer(1, 6*mm))
story.append(Paragraph("3. INT 13h — BIOS Disk Services (AH sub-functions)", h1_style))
story.append(Paragraph(
    "INT 13h provides low-level floppy and hard disk I/O. "
    "Extended INT 13h (AH=41h–48h) adds LBA addressing for large drives (> 8 GB).",
    body_style
))
story.append(Spacer(1, 3*mm))

disk_data = [
    ("00h", "Reset Disk System", "DL=drive; resets controller (DL>=80h for hard disk)."),
    ("01h", "Get Drive Status", "DL=drive; AH=status of last operation."),
    ("02h", "Read Sectors", "AH=02h, AL=sects, CH=cyl, CL=sect, DH=head, DL=drive, ES:BX=buf."),
    ("03h", "Write Sectors", "Same registers as Read. DL>=80h for hard disk."),
    ("04h", "Verify Sectors", "Verify (no data transfer); same registers."),
    ("05h", "Format Track", "DH=head, CH=cyl, DL=drive, ES:BX=address field buffer."),
    ("08h", "Get Drive Parameters", "DL=drive; CH=max cyl, CL=max sect, DH=max head, DL=# drives."),
    ("09h", "Init Fixed Disk Parameters", "DL=drive; uses Fixed Disk Parameter Table."),
    ("0Ch", "Seek to Cylinder", "CH=cyl, DH=head, DL=drive."),
    ("0Dh", "Reset Fixed Disk Controller", "DL>=80h."),
    ("10h", "Test Drive Ready", "DL=drive; CF=0 if ready."),
    ("11h", "Recalibrate Drive", "DL=drive."),
    ("15h", "Get Drive Type", "DL=drive; AH: 0=none,1=floppy no chg detect,2=floppy+detect,3=hard."),
    ("16h", "Detect Disk Change (Floppy)", "DL=drive; AH=06h if disk changed."),
    ("17h", "Set Disk Type for Format", "DL=drive, AL=type (floppy)."),
    ("18h", "Set Media Type for Format", "CH=cyl, CL=sects, DL=drive; ES:DI->11-byte param table."),
    ("41h", "Check EDD Extensions Present", "BX=55AAh, DL=drive; CF=0 if supported, BX=AA55h."),
    ("42h", "Extended Read Sectors (LBA)", "DL=drive, DS:SI -> 16-byte Disk Address Packet."),
    ("43h", "Extended Write Sectors (LBA)", "DL=drive, DS:SI -> DAP."),
    ("44h", "Extended Verify Sectors (LBA)", "DL=drive, DS:SI -> DAP."),
    ("45h", "Lock/Unlock Drive", "DL=drive, AL=0 lock / 1 unlock / 2 get status."),
    ("46h", "Eject Removable Media", "DL=drive."),
    ("47h", "Extended Seek (LBA)", "DL=drive, DS:SI -> DAP."),
    ("48h", "Get Extended Drive Parameters", "DL=drive, DS:SI -> 26-byte result buffer."),
]

col_d = [16*mm, 52*mm, W - 16*mm - 52*mm]
header_d = [
    Paragraph("<b>AH</b>", caption_style),
    Paragraph("<b>Function</b>", caption_style),
    Paragraph("<b>Parameters / Notes</b>", caption_style),
]
rows_d = [[Paragraph(r[0], caption_style), Paragraph(r[1], caption_style), Paragraph(r[2], caption_style)] for r in disk_data]
story.append(make_table(rows_d, col_d, header_d))

# ── Section 4: INT 21h DOS Function Dispatcher ────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("4. INT 21h — DOS Function Dispatcher (AH sub-functions)", h1_style))
story.append(Paragraph(
    "INT 21h is the primary DOS API. On entry, AH selects the function. "
    "On exit, CF=1 with AX=error code indicates failure. "
    "Over 100 sub-functions are defined across DOS versions 1.x–7.x.",
    body_style
))
story.append(Spacer(1, 3*mm))

col_21 = [16*mm, 55*mm, W - 16*mm - 55*mm]
header_21 = [
    Paragraph("<b>AH</b>", caption_style),
    Paragraph("<b>Function</b>", caption_style),
    Paragraph("<b>Parameters / Notes</b>", caption_style),
]
rows_21 = [[Paragraph(r[0], caption_style), Paragraph(r[1], caption_style), Paragraph(r[2], caption_style)] for r in dos21_data]
story.append(make_table(rows_21, col_21, header_21))

# ── Section 5: Status / Error Codes ───────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph("5. DOS Extended Error Codes (INT 21h AH=59h)", h1_style))
story.append(Paragraph(
    "When INT 21h returns CF=1, call AH=59h (BX=0) to get extended error information: "
    "AX=error code, BH=error class, BL=suggested action, CH=locus.",
    body_style
))
story.append(Spacer(1, 3*mm))

error_data = [
    ("01h", "Invalid function number"),
    ("02h", "File not found"),
    ("03h", "Path not found"),
    ("04h", "Too many open files"),
    ("05h", "Access denied"),
    ("06h", "Invalid handle"),
    ("07h", "Memory control blocks destroyed"),
    ("08h", "Insufficient memory"),
    ("09h", "Invalid memory block address"),
    ("0Ah", "Invalid environment"),
    ("0Bh", "Invalid format"),
    ("0Ch", "Invalid access code"),
    ("0Dh", "Invalid data"),
    ("0Fh", "Invalid drive specification"),
    ("10h", "Attempt to remove current directory"),
    ("11h", "Not same device"),
    ("12h", "No more files"),
    ("13h", "Disk write protected"),
    ("14h", "Unknown unit"),
    ("15h", "Drive not ready"),
    ("16h", "Unknown command"),
    ("17h", "CRC error"),
    ("18h", "Bad request structure length"),
    ("19h", "Seek error"),
    ("1Ah", "Unknown media type"),
    ("1Bh", "Sector not found"),
    ("1Ch", "Printer out of paper"),
    ("1Dh", "Write fault"),
    ("1Eh", "Read fault"),
    ("1Fh", "General failure"),
    ("20h", "Sharing violation"),
    ("21h", "Lock violation"),
    ("22h", "Invalid disk change"),
    ("23h", "FCB unavailable"),
    ("24h", "Sharing buffer overflow"),
    ("25h", "Code page mismatch"),
    ("26h", "Cannot complete file operation"),
    ("27h", "Insufficient disk space"),
    ("50h", "File already exists"),
    ("52h", "Cannot make directory"),
    ("53h", "Fail on INT 24h"),
    ("57h", "Invalid parameter"),
    ("58h", "Network write fault"),
    ("59h", "Function not supported on network"),
    ("5Ah", "Required system component not installed"),
]

mid = len(error_data) // 2
left_col  = error_data[:mid]
right_col = error_data[mid:]
# pad if odd
if len(right_col) < len(left_col):
    right_col.append(("", ""))

err_rows = []
for l, r in zip(left_col, right_col):
    err_rows.append([
        Paragraph(l[0], caption_style), Paragraph(l[1], caption_style),
        Paragraph(r[0], caption_style), Paragraph(r[1], caption_style),
    ])

half = (W - 6*mm) / 2
col_e = [14*mm, half - 14*mm, 14*mm, half - 14*mm]
header_e = [
    Paragraph("<b>Code</b>", caption_style), Paragraph("<b>Description</b>", caption_style),
    Paragraph("<b>Code</b>", caption_style), Paragraph("<b>Description</b>", caption_style),
]
story.append(make_table(err_rows, col_e, header_e))

# ── Footer note ───────────────────────────────────────────────────────────────
story.append(Spacer(1, 8*mm))
story.append(Paragraph(
    "Source: Ralf Brown's Interrupt List (RBIL), version 61 (2000). "
    "Full list available at http://www.cs.cmu.edu/~ralf/files.html  |  "
    "This document is a curated summary — not a complete reproduction.",
    caption_style
))

doc.build(story)
print(f"PDF created: {OUTPUT_PATH}")

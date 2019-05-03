import os
import sys
import struct
import mmap

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log

FORMAT_32 = 1
FORMAT_64 = 2

ENDIAN_LITTLE = 1
ENDIAN_BIG    = 2

PT_INTERP = 3

def format_str(format):
    if format == FORMAT_32:
        return "32bit(1)"
    if format == FORMAT_64:
        return "64bit(2)"
    return "?({})".format(format)
def endian_str(endian):
    if endian == ENDIAN_LITTLE:
        return "little-endian(1)"
    if endian == ENDIAN_BIG:
        return "big-endian(2)"
    return "?({})".format(endian)
def osabi_str(osabi, ver):
    def format(default_str, ver):
        if ver == 0:
            return default_str
        return "{}_v{}".format(default_str, ver)
    if osabi == 0:
        return format("SystemV(0)", ver)
    if osabi == 1:
        return format("HP-UX(1)", ver)
    if osabi == 2:
        return format("NetBSD(2)", ver)
    if osabi == 3:
        return format("Linux(3)", ver)
    if osabi == 4:
        return format("GNU-Hurd(4)", ver)
    if osabi == 6:
        return format("Solaris(6)", ver)
    if osabi == 7:
        return format("AIX(7)", ver)
    if osabi == 8:
        return format("IRIX(8)", ver)
    if osabi == 9:
        return format("FreeBSD(9)", ver)
    if osabi == 10:
        return format("Tru64(10)", ver)
    if osabi == 11:
        return format("NovellModesto(11)", ver)
    if osabi == 12:
        return format("OpenBSD(12)", ver)
    if osabi == 13:
        return format("OpenVMS(13)", ver)
    if osabi == 14:
        return format("NonStopKernel(14)", ver)
    if osabi == 15:
        return format("AROS(15)", ver)
    if osabi == 16:
        return format("FenixOS(16)", ver)
    if osabi == 17:
        return format("CloudABI(17)", ver)
    return format("?({})".format(osabi))

class ElfHeader:
    def parse_from_file(file):
        file.seek(0)
        header = file.read(64)
        return ElfHeader.parse_from_bytes(header)
    def parse_from_bytes(bytes):
        if len(bytes) < 64:
            return "file too small"
        magic = bytes[:4].decode("ascii")
        if not magic == '\x7fELF':
            return "bad magic '{}'".format(magic)
        format = bytes[4]
        if format != FORMAT_32 and format != FORMAT_64:
            return "unknown format {} (1=32bit, 2=64bit)".format(format)

        endian = bytes[5]
        if endian != ENDIAN_LITTLE and endian != ENDIAN_BIG:
            return "unknown endian {} (1=little, 2=big)".format(endian)

        global_ver = bytes[6]
        if global_ver != 1:
            return "unknown version {}, expected 1".format(global_ver)

        osabi = bytes[7]
        osabi_ver = bytes[8]

        return ElfHeader(format, endian, osabi, osabi_ver, bytes)
    def __init__(self, format, endian, osabi, osabi_ver, bytes):
        self.format = format
        self.endian = endian
        self.osabi = osabi
        self.osabi_ver = osabi_ver

        if format == FORMAT_32:
            unpack_fmt = "HHILLLIHHHHHH"
        else:
            unpack_fmt = "HHIQQQIHHHHHH"
        if endian == ENDIAN_LITTLE:
            unpack_fmt = "<" + unpack_fmt

        (self.type, self.machine, self.other_ver, self.entry, self.phoff,
         self.shoff, self.flags, self.ehsize, self.phentsize, self.phnum,
         self.shentsize, self.shnum, self.shstrndx) = struct.unpack_from(
             unpack_fmt, bytes, 16)
    def __str__(self):
        return "{} {} {}".format(format_str(self.format), endian_str(self.endian),
                                 osabi_str(self.osabi, self.osabi_ver))
    def fix_pack_fmt_endian(self, fmt):
        if self.endian == ENDIAN_LITTLE:
            return "<" + fmt
        return fmt

def change_interpreter(filename, new_interp):
    log.log("[DEBUG] changing interpreter for: {}".format(filename))
    with open(filename, 'r+b') as file:
        hdr = ElfHeader.parse_from_file(file)
        if isinstance(hdr, str):
            sys.exit("'{}' doesn't appear to be an ELF file: {}".format(filename, hdr))

        with mmap.mmap(file.fileno(), 0) as mem:
            result,new_interp_off = set_interpreter(filename, hdr, mem, new_interp)
            if result == 0:
                sys.exit("ELF file '{}' doesn't have a PT_INTERP program header".format(filename))
            if result == 1:
                return

        log.log("[DEBUG] adding interpreter to end of file at offset {}".format(new_interp_off))
        file.seek(new_interp_off)
        file.write(new_interp + b'\0')

# Returns:
#   0 if there is not interp section
#   1 if it successfully replaced the interpreter
#   2 if you need to add the interpreter to the end of the file
def set_interpreter(filename, hdr, mem, new_interp):
    word_fmt = hdr.fix_pack_fmt_endian("I")

    log.log("[DEBUG] changinge interpreter with {} program headers...".format(hdr.phnum))
    # look for PT_INTERP section
    for phindex in range(0, hdr.phnum):
        phoff = hdr.phoff + (phindex * hdr.phentsize)
        (type,) = struct.unpack_from(word_fmt, mem, phoff)
        log.log("[DEBUG] type {}".format(type))
        if type == PT_INTERP:
            log.log("[DEBUG] found PT_INTERP section!")
            phoff += 4
            if hdr.format == FORMAT_32:
                ph_fmt = hdr.fix_pack_fmt_endian("IIII")
                (interp_off, vaddr, paddr, filesz) = struct.unpack_from(ph_fmt, mem, phoff)
            else:
                ph_fmt = hdr.fix_pack_fmt_endian("IQQQQ")
                (flags, interp_off, vaddr, paddr, filesz) = struct.unpack_from(ph_fmt, mem, phoff)
            current_interp = mem[interp_off:interp_off+filesz]
            #log.log("[DEBUG] current_interp is '{}'".format(current_interp))
            if len(new_interp) + 1 <= filesz:
                padding = filesz - len(new_interp)
                log.log("[DEBUG] padding = '{}'".format(padding))
                new_field = new_interp + (b'\0' * (filesz - len(new_interp)))
                #log.log("[DEBUG] new_field '{}'".format(new_field))
                mem[interp_off:interp_off+len(new_field)] = new_field
                log.log("[DEBUG] set new interp to {} @ offset {}".format(mem[interp_off:interp_off+len(new_field)], interp_off))
                return 1,None # successfully replaced interp

            # append the new interperter to the end of the file
            new_interp_off = len(mem)
            new_filesz = len(new_interp) + 1
            if hdr.format == FORMAT_32:
                struct.pack_into(ph_fmt, mem, phoff, new_interp_off,
                                 vaddr, paddr, new_filesz)
            else:
                struct.pack_into(ph_fmt, mem, phoff, flags, new_interp_off,
                                 vaddr, paddr, new_filesz)
                (flags, interp_off, vaddr, paddr, filesz) = struct.unpack_from(ph_fmt, mem, phoff)
                assert interp_off == new_interp_off
                assert filesz == new_filesz

            return 2,new_interp_off # add interpreter to the end of the file
    return 0,None # no interp section

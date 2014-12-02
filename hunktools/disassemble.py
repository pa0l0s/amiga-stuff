import struct


ADDR_MODES = {
    '000': 'Dn', '001': 'An', '010': '(An)', '011': '(An)+', '100': '-(An)',
    '101': '(d16,An)', '110': '(d8,An,Xn)', '111': 'EXT'  # -> ADDR_MODES_EXT
}

ADDR_MODES_EXT = {
    '000': '(xxx).W', '001': '(xxx).L', '100': '#<data>',
    '010': '(d16,PC)', '011': '(d8,PC,Xn)'
}

OPCODE_CATEGORIES = {
    '0000': 'bitops_movep_imm', '0001': 'move.b', '0010': 'move.l', '0011': 'move.w',
    '0100': 'misc', '0101': 'addq_subq', '1001': 'sub_subx',
    '0110': 'bcc_bsr_bra', '0111': 'moveq',
    '1101': 'add_addx'
}

ADD_SUB_OPMODES = {
    '000': ('b', 'ea,dn->dn'), '001': ('w', 'ea,dn->dn'),'010': ('l', 'ea,dn->dn'),
    '100': ('b', 'dn,ea->ea'), '101': ('w', 'dn,ea->ea'),'110': ('l', 'dn,ea->ea')
}

SIZES = ['b', 'w', 'l']

CONDITION_CODES = [
    't', 'f', 'hi', 'ls',
    'cc', 'cs', 'ne', 'eq',
    'vc', 'vs', 'pl', 'mi',
    'ge', 'lt', 'gt', 'le'
]

class Opcode(object):
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def is_branch(self):
        return False

    def __repr__(self):
        return "%s" % self.name

class Operation2(Opcode):
    def __init__(self, name, size, src, dest):
        Opcode.__init__(self, name, size)
        self.src = src
        self.dest = dest

    def __repr__(self):
        return "%s\t%s,%s" % (self.name, self.src, self.dest)


class Operation1(Opcode):
    """A single operand operation"""

    def __init__(self, name, size, dest):
        Opcode.__init__(self, name, size)
        self.dest = dest

    def __repr__(self):
        return "%s\t%s" % (self.name, self.dest)


class Jump(Opcode):
    def __init__(self, name, size, displacement):
        Opcode.__init__(self, name, size)
        self.displacement = displacement

    def is_branch(self):
        return True

    def __repr__(self):
        return "%s\t%s" % (self.name, self.displacement)


def is_move(category):
    return category in {'move.b', 'move.w', 'move.l'}


def next_word(size, data, data_offset):
    if size == 'L':
        value = struct.unpack('>i', data[data_offset:data_offset+4])[0]
        added = 4
    elif size == 'W':
        data[data_offset:data_offset+2]
        value = struct.unpack('>h', data[data_offset:data_offset+2])[0]
        added = 2
    else:
        raise Exception('unsupported size: ', size)
    return (value, added)


def operand(size, mode_bits, reg_bits, data, offset):
    result = ""
    added = 0
    mode = ADDR_MODES[mode_bits]
    size = size.upper()

    if mode == 'EXT':
        mode = ADDR_MODES_EXT[reg_bits]
        regnum = int(reg_bits, 2)
        if mode == '#<data>':
            imm_value, added = next_word(size, data, offset + 2)
            result = "#%d" % imm_value
        elif mode in {'(xxx).L', '(xxx).W'}:  # absolute
            addr, added = next_word(mode[-1], data, offset + 2)
            result = "%d.%s" % (addr, mode[-1])
        elif mode == '(d16,PC)':
            disp16, added = next_word('W', data, offset + 2)
            result = "%d(PC)" % disp16
        else:
            raise Exception("unsupported ext mode: '%s'" % mode)
    elif mode == '(d16,An)':
        regnum = int(reg_bits, 2)
        disp16, added = next_word('W', data, offset + 2)
        result = "%d(A%d)" % (disp16, regnum)
    else:
        regnum = int(reg_bits, 2)
        result = mode.replace('n', str(regnum))
    return result, added
    

def disassemble_move(bits, data, offset):
    category = OPCODE_CATEGORIES[bits[0:4]]
    total_added = 2
    # dst: reg|mode
    dst_op, added = operand(category[-1], bits[7:10], bits[4:7], data, offset)
    total_added += added

    # src: mode|reg
    src_op,added = operand(category[-1], bits[10:13], bits[13:16], data, offset)
    total_added += added
    return Operation2(category, total_added, src_op, dst_op)


def disassemble_add_sub(name, bits, data, offset):
    total_added = 2
    reg = "D%d" % int(bits[4:7], 2)
    size, operation = ADD_SUB_OPMODES[bits[7:10]]
    ea, added = operand(size, bits[10:13], bits[13:16], data, offset)
    total_added += added

    if operation == 'ea,dn->dn':
        src = ea
        dst = reg
    elif operation == 'dn,ea->ea':
        src = reg
        dst = ea
    else:
        raise Exception('Unknown operation for %s' % name)

    return Operation2('%s.%s' % (name, size), total_added, src, dst)


def disassemble_misc(bits, data, offset):
    #print("misc bits: " + bits)
    if bits == '0100111001110101':  # rts
        return Opcode('rts', 2)
    elif bits == '0100101011111100': # illegal
        return Opcode('illegal', 2)
    elif bits[7:10] == '111':  # lea
        regnum = int(bits[4:7], 2)
        ea, added = operand('l', bits[10:13], bits[13:16], data, offset)
        return Operation2('lea', added + 2, ea, 'A%d' % regnum)
    elif bits.startswith('0100111010'):  # jsr
        ea, added = operand('l', bits[10:13], bits[13:16], data, offset)
        return Jump('jsr', added + 2, ea)
    elif bits.startswith('0100111011'):  # jmp
        ea, added = operand('l', bits[10:13], bits[13:16], data, offset)
        return Jump('jmp', added + 2, ea)
    elif bits.startswith('01001010'):  # tst.x
        size = SIZES[int(bits[8:10], 2)]
        ea, added = operand('l', bits[10:13], bits[13:16], data, offset)
        return Operation1('tst.%s' % size, added + 2, ea)
    else:
        print("unrecognized misc: %s" % bits)
        raise Exception('TODO Misc')


def signed8(value):
    return -(256 - value) if value > 127 else value


def branch_displacement(bits, data, offset):
    """disp, added = read displacement"""
    disp = signed8(int(bits[8:16], 2))
    if disp == 0:  # 16 bit displacement
        return next_word('W', data, offset + 2)
    elif disp == -1:  # 32 bit displacement
        return next_word('L', data, offset + 2)
    else:
        return disp, 0


def _disassemble(data, offset):
    bits = "{0:016b}".format(struct.unpack(">H", data[offset:offset+2])[0])
    # first step categorize by looking at bits 15-12
    opcode = bits[0:4]
    category = OPCODE_CATEGORIES[opcode]

    if is_move(category):
        instr = disassemble_move(bits, data, offset)
    elif category in {'add_addx', 'sub_subx'}:
        if bits[7] == 1 and bits[10:12] == '11':  # extended
            raise Exception('addx/subx not supported yet')
        else:
            instr = disassemble_add_sub(category[0:3], bits, data, offset)
    elif category == 'misc':
        instr = disassemble_misc(bits, data, offset)
    elif category == 'moveq':
        regnum = int(bits[4:7], 2)
        value = signed8(int(bits[8:16], 2))
        instr = Operation2('moveq', 2, "#%d" % value, 'D%d' % regnum)
    elif category == 'bcc_bsr_bra':
        if bits[0:8] == '01100000':  # bra
            disp, added = branch_displacement(bits, data, offset)
            instr = Jump('bra', added + 2, disp)
        elif bits[0:8] == '01100001':  # bsr
            disp, added = branch_displacement(bits, data, offset)
            instr = Jump('bsr', added + 2, disp)
        else:
            cond = CONDITION_CODES[int(bits[4:8], 2)]
            disp, added = branch_displacement(bits, data, offset)
            instr = Jump('b%s' % cond, added + 2, disp)
    elif category == 'addq_subq':
        if bits[7] == '0':  # addq
            ea, added = operand('l', bits[10:13], bits[13:16], data, offset)
            value = int(bits[4:7], 2)
            instr = Operation2('addq', added + 2, '#%d' % value, ea)
        else:
            raise Exception('TODO addq_subq etc')
    else:
        print("\nUnknown instruction\nCategory: ", category, " Bits: ", bits)
        raise Exception('TODO')
    return instr


def print_instruction(address, op):
    print("$%08x:\t%s" % (address, op))
    """
    if len(op) == 3:
        opcode, src, dst = op
        print("$%08x:\t%8s %s,%s" % (address, opcode, src, dst))
    elif len(op) == 2:
        opcode, ea = op
        print("$%08x:\t%8s %s" % (address, opcode, ea))
    elif len(op) == 1:
        print("$%08x:\t%8s" % (address, op[0]))
    else:
        raise Exception("can't print instruction with %d components" % len(op))
    """

def disassemble(code):
    """Disassembling a chunk of code works on this assumptions:

    1. the first address in the block contains a valid instruction from here
      a. branches: add the displacement target to the list of continue points
      b. if the instruction is an absolute jump/branch, we can't safely
         assume the code after the instruction is valid -> continue at branch
         target
      c. conditional branch -> add the address after the instruction as a valid
         ass valid decoding location
      d. rts: we can't assume the code after this instruction is valid
    """
    offset = 0
    while offset < len(code):
        instr = _disassemble(code, offset)
        print_instruction(offset, instr)
        offset += instr.size
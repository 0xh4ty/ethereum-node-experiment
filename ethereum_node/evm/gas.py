#!/usr/bin/env python3
# evm/gas.py

# --- Fixed cost operation sets ---
GZERO = 0               # Cost for operations in Wzero
GBASE = 2               # Cost for operations in Wbase
GVERYLOW = 3            # Cost for operations in Wverylow
GLOW = 5                # Cost for operations in Wlow
GMID = 8                # Cost for operations in Wmid
GHIGH = 10              # Cost for operations in Whigh
GEXTCODE = 700          # For EXTCODESIZE, EXTCODECOPY
GJUMPDEST = 1           # Cost for JUMPDEST

# --- Memory expansion ---
GMEMORY = 3             # Per word memory expansion cost

# --- SHA3 ---
GSHA3 = 30              # Fixed cost for SHA3
GSHA3WORD = 6           # Per word of input

# --- Log operations ---
GLOG = 375              # Base cost for LOG0
GLOGDATA = 8            # Per byte of data
GLOGTOPIC = 375         # Per topic

# --- Call-related ---
GCALL = 700             # Base cost for CALL
GCALLVALUE = 9000       # Additional cost when value is transferred
GCALLSTIPEND = 2300     # Stipend subtracted from GCALLVALUE
GNEWACCOUNT = 25000     # Cost when CALL or SELFDESTRUCT creates new account

# --- Self-destruct ---
GSELFDESTRUCT = 5000    # Base cost
RSELFDESTRUCT = 24000   # Refund if storage is cleared

# --- Storage operations ---
GSLOAD = 100            # Cost for SLOAD
GCOLDSLOAD = 2100       # Cold SLOAD
GSSET = 20000           # SSTORE: zero → non-zero
GSRESET = 5000          # SSTORE: non-zero → zero or same
RSCLEAR = 4800          # Refund for clearing slot

# --- Access list costs ---
GWARMACCESS = 100
GACCESSLIST_ADDRESS = 2400
GACCESSLIST_STORAGE = 1900
GCOLDACCOUNTACCESS = 2600

# --- CREATE / CODE DEPOSIT ---
GCREATE = 32000
GCREATE2 = 32000
GCODEDEPOSIT = 200      # Per byte

# --- EXP ---
GEXP = 10               # Base cost
GEXPBYTE = 50           # Per byte in exponent

# --- COPY operations ---
GCOPY = 3               # Per word for CODECOPY, RETURNDATACOPY, CALLDATACOPY

# --- BLOCKHASH ---
GBLOCKHASH = 20

# --- Transaction costs ---
GTXCREATE = 32000
GTXDATAZERO = 4
GTXDATANONZERO = 16
GTRANSACTION = 21000

# --- Utility ---
def memory_expansion_cost(num_words: int) -> int:
    return num_words * GMEMORY

# --- Opcode gas costs (by opcode number) ---
GAS_COSTS = {
    0x00: GZERO,         # STOP
    0x01: GVERYLOW,      # ADD
    0x02: GMID,          # MUL
    0x03: GVERYLOW,      # SUB
    0x04: GMID,          # DIV
    0x05: GMID,          # SDIV
    0x06: GMID,          # MOD
    0x20: GSHA3,         # SHA3
    0x50: GBASE,         # POP
    0x51: GVERYLOW,      # MLOAD
    0x52: GVERYLOW,      # MSTORE
    0x53: GVERYLOW,      # MSTORE8
    0x54: GSLOAD,        # SLOAD
    0x55: GSSET,         # SSTORE (assume worst-case for now)
    0x56: GBASE,         # JUMP
    0x57: GBASE,         # JUMPI
    0x5b: GJUMPDEST,     # JUMPDEST
    0xa0: GLOG,          # LOG0
    0xa1: GLOG,          # LOG1
    0xa2: GLOG,          # LOG2
    0xa3: GLOG,          # LOG3
    0xa4: GLOG,          # LOG4
    0xf0: GCREATE,       # CREATE
    0xf1: GCALL,         # CALL
    0xf2: GCALL,         # CALLCODE
    0xf3: GZERO,         # RETURN
    0xf4: GCALL,         # DELEGATECALL
    0xf5: GCREATE2,      # CREATE2
    0xfa: GCALL,         # STATICCALL
    0xfd: GBASE,         # REVERT
    0xff: GSELFDESTRUCT, # SELFDESTRUCT
}

# Fill in PUSH1 - PUSH32 (0x60 - 0x7f)
for i in range(0x60, 0x80):
    GAS_COSTS[i] = GVERYLOW

# Fill in DUP1 - DUP16 (0x80 - 0x8f)
for i in range(0x80, 0x90):
    GAS_COSTS[i] = GVERYLOW

# Fill in SWAP1 - SWAP16 (0x90 - 0x9f)
for i in range(0x90, 0xa0):
    GAS_COSTS[i] = GVERYLOW

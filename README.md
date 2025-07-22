# Ethereum Node Experiment (Devnet)

A Python-based Ethereum execution client for devnet experimentation. Implements core Yellow Paper logic with full EVM, constant-difficulty PoW, JSON-RPC, and LAN sync.

## Architecture

```text
                  ┌─────────────────────┐
                  │     JSON-RPC API    │ ◄───── web3.py, CLI, etc.
                  │   (FastAPI server)  │
                  └────────┬────────────┘
                           │
                    ┌──────▼───────┐
                    │  Node Main   │ ◄─── main.py entry point
                    └──────┬───────┘
                           │
        ┌──────────────────┼───────────────────┐
        │                  │                   │
┌───────▼───────┐   ┌──────▼──────┐     ┌──────▼──────┐
│ Transaction   │   │ Block       │     │ State       │
│ Pool (txpool) │   │ Builder     │     │ Manager     │
└──────┬────────┘   │ & Validator │     │ (Trie, A/C) │
       │            └─────┬───────┘     └──────┬──────┘
       │                  │                   │
       ▼                  ▼                   ▼
 ┌────────────┐     ┌────────────┐      ┌─────────────┐
 │ EVM (vm.py)│◄────┤ Consensus  │◄────►│   Storage    │
 │  Opcodes   │     │ Engine     │      │ (LevelDB)    │
 └────────────┘     │ (PoW loop) │      └─────────────┘
                    └────────────┘

                    ▲
                    │
              ┌─────┴─────┐
              │  P2P Sync │ ◄────── Connects to peers, exchanges blocks/txs
              │  Network  │
              └───────────┘
```

## Usage

```bash
python -m ethereum_node.main --help
```

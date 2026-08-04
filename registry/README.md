# Registry

Rust crate. Encrypted personal storage with two independent modules.

This is the reason for the pivot. The failure being designed against: the laptop dies, the SSD corrupts, and I lose passwords, notes, and accumulated context. The registry exists to make that impossible.

## Modules

### Keys

Encrypted password and secret storage. 2FA-gated writes, TOTP seeds, credential management.

### Logbook

Encrypted journal. Daily entries, searchable, append-mostly. Unlocking the logbook does NOT unlock the keys store.

## Design (ADR-020)

Two independent unlock states, off one master password:

```
master password ──KDF──▸ master key
                            ├──▸ logbook key   (unlocks journal entries)
                            └──▸ keys key      (unlocks passwords/2FA)
```

## Status

Not yet started. See `local/rust-toys/05-vault-and-crypto.md` for the spec and `local/rust-toys/LEARNING.md` for the Rust curriculum.

## Dependencies (planned)

```toml
[dependencies]
argon2 = "0.5"                           # KDF
chacha20poly1305 = "0.10"                # AEAD
zeroize = { version = "1", features = ["derive"] }  # zero memory on drop
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

Crypto primitives come from audited crates. Everything around them (key hierarchy, file format, unlock flow, relock policy) is hand-built. See ADR-024.

## Structure (planned)

```
registry/
├── src/
│   ├── lib.rs            # public API
│   ├── crypto.rs         # KDF, AEAD, key hierarchy
│   ├── keys/
│   │   ├── mod.rs        # keys store API
│   │   └── model.rs      # Secret, Credential structs
│   ├── logbook/
│   │   ├── mod.rs        # logbook API
│   │   └── model.rs      # JournalEntry structs
│   ├── store.rs          # encrypted storage read/write
│   └── error.rs          # RegistryError enum
├── tests/
│   └── integration.rs
└── Cargo.toml
```

## Integration

Standalone for now. When Tauri arrives, this becomes a dependency of `src-tauri/Cargo.toml` and gets exposed via Tauri commands. The React frontend calls `invoke("unlock_logbook", { password })` through Tauri IPC.

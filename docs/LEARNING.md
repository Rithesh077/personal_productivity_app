# Learning log

The migration is a vehicle for learning Rust as much as it is a rewrite. This file tracks what I am learning, in what order, and whether it has actually stuck.

Toy specifications live in `local/rust-toys/`.

Started 26 Jul 2026.

## How I work

Recorded here so that no agent reading the repository gets this backwards.

I write the code, test it, and refactor it, and then I ask for an assessment. Not the other way round, unless I say otherwise.

Do not hand me a solution when I am stuck. I will ask. Silence means I am still working on it.

My background is C. I have written more C than anything else and it remains my favourite language, so manual memory management is not new to me. Explanations should route through C rather than through Python or Java: ownership is a considerably easier sell to someone who has already been tracking lifetimes by hand.

## C to Rust

The differences likely to catch me out.

| C habit | Rust equivalent | The catch |
|---|---|---|
| `malloc` / `free` | Ownership and `Drop` | Freeing is automatic and happens exactly once, checked at compile time. You never call it |
| Passing a pointer | `&T` / `&mut T` | Many shared references or one exclusive reference, never both at once |
| `char *` | `String` vs `&str` | An owned heap buffer versus a borrowed view into someone else's. `String` is the one you would have had to free |
| Struct assignment copies | Move semantics | Assigning a non-`Copy` value invalidates the original. The largest single surprise coming from C |
| `void *` with a tagged union | `enum` carrying data | Variants hold payloads, and `match` is exhaustive, so the compiler catches the case I forgot |
| `return -1` and `errno` | `Result<T, E>` and `?` | Errors appear in the signature. Ignoring one is a compiler warning rather than a silent bug months later |
| `static` globals | `Arc<Mutex<T>>` | Shared mutable state has to prove it is thread-safe. `Send` and `Sync` are checked, not assumed |
| Manual reference counting | `Rc` / `Arc` | Not to be reached for until plain ownership has genuinely failed. See toy 3 |
| Pointer-based trees and lists | Arena plus index IDs | The ordinary C tree with parent pointers does not port. Toy 3 is entirely about this |

The last row is the one that will hurt. In C, a tree with parent pointers is unremarkable. In Rust it fights back at every step. Toy 3 exists so that I meet that early, on my own data model, rather than three weeks into the migration.

## Curriculum

Eight toys, each producing something the real app keeps. Full specifications in `local/rust-toys/`.

| # | Toy | Concepts | Becomes |
|---|---|---|---|
| 1 | Task list CLI, std only | Ownership, borrowing, structs, enums, `Vec`, `Option`, `match` | `core::model` |
| 2 | Persistence and errors | Traits, `Result`, `?`, custom errors, serde, file I/O | `core::store` |
| 3 | Hierarchy and cascade | The borrow checker, properly | `core::planner` |
| 4 | Concurrency and locking | `Arc`, `Mutex`, `Send`/`Sync`, async | Storage locking |
| 5 | Vault and crypto | Bytes, `Drop`, zeroing, KDF, AEAD | `core::vault` |
| 6 | TUI | Event loops, render state | The interim app |
| 7 | Tauri bridge and React | Commands, `State`, IPC | The shell |
| 8 | Sync spike | Networking, conflict resolution | Sync, possibly |

Toys 3 and 5 are the ones that matter. Toy 3 is where Rust stops being C with better syntax. Toy 5 is where the actual reason for the pivot gets built. If only two get done properly, those are the two.

## Concept tracker

To be marked honestly. Having used something is not the same as understanding it. The bar for a tick is being able to explain why it works, out loud, without looking it up.

Legend: unmarked is untouched, `~` is used but not understood, `x` is can explain it cold.

### Fundamentals
- [ ] Ownership and moves
- [ ] Borrowing, `&` versus `&mut`
- [ ] One mutable reference or many immutable ones
- [ ] `String` versus `&str`, `Vec<T>` versus `&[T]`
- [ ] `Copy` versus `Clone`, and noticing when I clone purely to silence the compiler
- [ ] Structs, `impl`, methods versus associated functions
- [ ] Enums carrying data, exhaustive `match`
- [ ] `Option<T>`, and not missing null

### Intermediate
- [ ] Traits, trait bounds, `impl Trait`
- [ ] `Result`, `?`, custom error enums, `From`
- [ ] Lifetimes: reading them first, writing them later
- [ ] Iterators and closures
- [ ] `HashMap` and the entry API
- [ ] Modules, crates, workspaces
- [ ] Generics

### Hard parts
- [ ] `Box`, `Rc`, `RefCell`, and when each is actually correct
- [ ] Interior mutability and why it exists
- [ ] Why parent pointers hurt, and the arena pattern
- [ ] `Arc<Mutex<T>>`, `Send` and `Sync`
- [ ] Async, futures, and the runtime
- [ ] Deadlocking by holding a lock across an await
- [ ] `unsafe`, and what it does not switch off

### Applied
- [ ] Serde derive and hand-written implementations
- [ ] SQLite from Rust
- [ ] Byte handling: `[u8; 32]`, slices, endianness, file formats
- [ ] Crypto hygiene: KDF parameters, nonces, zeroing, constant-time comparison
- [ ] Tauri commands and `State`
- [ ] Cross-compilation and mobile targets

## Reference

The Rust Book, chapters 4 (ownership), 6 (enums and matching), 8 (collections), 9 (errors), 10 (generics, traits, lifetimes), 13 (iterators and closures), 15 (smart pointers), 16 (concurrency). Numbering past chapter 16 shifts between editions, so go by name.

Rust by Example for when the Book is too wordy and I only want the shape of the syntax. Rustlings for the fundamentals block above. The Tauri v2 guide, but not until toy 7 starts.

`cargo clippy` is effectively a free code review, and most of what it reports is teaching me idiom rather than catching bugs.

## Log

One entry per session, kept short. The useful column is what confused me; that is the part worth having later.

```
### date, toy N
Built:
Fought with:
Clicked:
Still unclear:
Clones added purely to satisfy the compiler:
```

No entries yet. The first lands with toy 1.

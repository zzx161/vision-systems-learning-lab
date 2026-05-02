# Labs

This directory contains the hands-on part of the study system.

## Structure

- `Makefile`
  Build all lab programs.
- `src/`
  C++ sources for the first-phase labs.
- `bin/`
  Generated executables after build.
- `lab_*.md`
  Lab guides, commands, and what to observe.

## Build

From this directory:

```bash
make
```

Build outputs:

- `bin/lesson_01_threads`
- `bin/lesson_02_memory`
- `bin/lesson_03_cache`
- `bin/lesson_04_runtime_shapes`
- `bin/lesson_06_tail_latency`

## Notes

- The labs are designed to work with only `g++`, `top`, and `vmstat`.
- If `pidstat`, `strace`, or `perf` are installed later, the guides already include optional exercises for them.

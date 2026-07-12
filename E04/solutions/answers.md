# Lab 04 Solutions: Multitasking & IPC

> **Note on the question sheet.** No blank, professor-issued question PDF for this
> exercise was found in the original course materials — only `E04-v1.pdf`, which is
> the author's own annotated walkthrough (prompts and answers written together,
> several blank filler pages). It is still the closest thing to an official question
> sheet for Lab 04 that exists in the source folder, and it walks through the same
> files as `materials/` (`code1.c` … `code5.c`, `Ex9.sh`, `Ex10.sh`, `scheduler.sh`),
> so it is used here as `solutions/questions.pdf`. This answer sheet is organized
> around that same sequence, one section per program/script, in the order they
> appear in the PDF.

## 1. `code1.c` — two threads, one unprotected counter

**Run and observe.** Compile and run (`materials/Resources/code1.c` via the
`makefile`). The output shows lines like `A1`, `B1`, `A2`, `B2`, ... but the numbers
are **not** cleanly ordered: they can repeat, skip, or interleave unpredictably
between the two threads.

**What is happening?** `code1.c` starts two threads, pins thread A to core 0 and
thread B to core 1 with `pthread_setaffinity_np`, and both threads increment and
print the same global `int counter` in a loop with no synchronization. Because the
two threads run truly in parallel on different cores and share the same memory
address for `counter`, their read-increment-print sequences interleave at the
hardware level. This is a **race condition**: the final/interleaved values depend on
scheduling, not on program logic.

**`pthread_create()` — what it does.** Creates and starts a new thread. Signature:
`int pthread_create(pthread_t *thread, const pthread_attr_t *attr, void *(*start_routine)(void*), void *arg)`.
- `pthread_t *thread` — output parameter, receives the new thread's ID.
- `attr` — thread attributes (`NULL` uses the default attributes).
- `start_routine` — function pointer the new thread starts executing.
- `arg` — the single argument passed to `start_routine` (here, the string `"A"` or `"B"`).

## 2. `code2.c` — adding a mutex around the increment

**Run and observe.** The A/B interleaving is still visible in the output (both
threads still print concurrently), and each printed number is unique and strictly
increasing overall (no duplicate or repeated values) — but the highest number
reached varies noticeably between runs, e.g. ending around `B500` in one run and
around `B999` in another (verified by running the compiled binary three times: runs
ended at `B593`, `B999`, and `B500`).

**What is different?** A `pthread_mutex_t lock` is declared, initialized with
`pthread_mutex_init`, and the increment + print of `counter` is wrapped in
`pthread_mutex_lock(&lock)` / `pthread_mutex_unlock(&lock)`. Only one thread can hold
the lock at a time, so increments can no longer be lost — no two threads ever
increment `counter` at the same instant, and no printed value repeats.

**Why does the final count still vary between runs?** `counter = 0;` at the top of
`print_number` is **not** inside the lock. Each thread resets the *shared* `counter`
to `0` once, right when it starts — whenever that happens to be relative to the
other thread. If thread B's unprotected reset happens after thread A has already
counted partway up, A's progress is wiped out and both threads continue
incrementing the same counter from `0` again; if the two resets happen close to
each other at the start, the two threads simply share one counter for the whole
run and jointly count all the way up toward `1000` (500 increments each). This is
still a race condition — just on the *reset*, not on the increment — and it is why
the mutex removes duplicate/lost values but does not make the final result
deterministic.

**What is a mutex?** A mutual-exclusion lock: a synchronization primitive that only
one thread can hold ("lock") at a time. Any other thread calling
`pthread_mutex_lock()` blocks until the holder calls `pthread_mutex_unlock()`. It
guarantees exclusive access to whatever shared data the critical section protects.

## 3. `code3.c` — locking for the whole loop

**Run and observe.** The output now shows thread A counting cleanly from 1 to 1000,
finishing completely, and only then does thread B count from 1 to 1000 (or vice
versa) — the two sequences no longer interleave at all.

**What is happening?** In `code3.c` the mutex is acquired once, *before* the loop
(`pthread_mutex_lock(&lock)` then reset `counter = 0`), held for all 1000
iterations, and released only after the loop ends. So whichever thread acquires the
lock first runs its entire loop uninterrupted; the second thread blocks on
`pthread_mutex_lock()` until the first thread's whole loop — and unlock — completes.

**Why does each thread count to 1000, and why does it happen twice?** The loop bound
in `code3.c` is `1000` (unlike `code1.c`/`code2.c`, which use `500`), and `counter` is
reset to `0` inside the locked section by *each* thread. Because the threads run the
full locked loop one after another rather than concurrently, there is no overlap: you
see one complete, independent 1→1000 count from thread A, then one complete,
independent 1→1000 count from thread B.

## 4. `code4.c` — the mutex that never unlocks

**What is happening?** Each loop iteration calls `pthread_mutex_lock(&lock)`,
increments and prints `counter`, but the loop body never calls
`pthread_mutex_unlock(&lock)`. Verified by running the compiled binary with
line-buffered output (`stdbuf -oL ./code4`, since with normal buffering the
program never exits to flush its output): the program prints exactly one line,
`A1`, and then hangs until killed. Whichever thread wins the race to run first
(here, thread A) locks the mutex, prints its first value, then on the *second*
loop iteration calls `pthread_mutex_lock(&lock)` again while still holding the
same lock from iteration one — a self-deadlock, since a default (non-recursive)
`pthread_mutex_t` blocks a thread that tries to lock a mutex it already holds.
The other thread (B) never even gets to print once, because it blocks on its
very first `pthread_mutex_lock(&lock)` call waiting for a lock that will now
never be released.

**Why?** The programmer forgot the matching `pthread_mutex_unlock(&lock)` call. Once
a mutex is locked and never unlocked, every subsequent call to
`pthread_mutex_lock()` (from either thread, on the next iteration or from the other
thread) blocks indefinitely — a deadlock. This demonstrates that a mutex only works
correctly if lock and unlock are paired for every acquisition.

## 5. `code5.c` — CPU affinity and an intentional infinite loop

**Setup.** `apt update && apt install -y htop` installs a live process/CPU monitor.
`code5.c` pins **both** threads to CPU core 0 (a single shared `cpu_set_t` is used for
both `pthread_setaffinity_np` calls, instead of one cpuset per core as in the earlier
files), and `print_number` is replaced with `for(ever);` — an intentional, empty
infinite loop (`#define ever ;;`), so the program never terminates.

**What do you observe in `htop`?** Both threads show up pinned to, and consuming, CPU
core 0 (up to 100% of that core), while core 1 stays mostly idle. Because two
busy-looping threads now compete for the same core instead of using one core each,
there is more context switching between them and effectively lower throughput per
thread than when they had a core each.

**How do you find and stop it?** `ps aux | grep code5` lists the process (the process
ID is in the second column); `kill -9 <processID>` force-kills it, since the infinite
loop has no way to exit on its own.

## 6. `scheduler.sh` — a simple cooperative task scheduler

**Task.** Create the script (`touch scheduler.sh`, `chmod +x scheduler.sh`, edit with
`nano`/`vim`/`gedit`) implementing three "periodic" tasks driven from a single loop
that sleeps 100 ms per iteration:
- `task_100ms` runs every iteration (every ~100 ms).
- `task_1s` runs every 10 iterations of `task_100ms` (every ~1 s), tracked with
  `counter_100ms`.
- `task_5s` runs every 5 firings of `task_1s` (every ~5 s), tracked with
  `counter_1s`.

**What is happening?** This script simulates a cooperative, single-threaded
scheduler using only shell counters and `sleep 0.1` — there is no real-time
guarantee (each iteration's actual period is `0.1s` plus whatever the three task
functions themselves take to run), but it approximates independent periodic tasks
without needing threads, processes, or the OS scheduler directly. It is the
shell-level analogue of the timer-driven multitasking discussed for `code1.c`–`code5.c`.

## 7. `Ex9.sh` / `Ex10.sh` and `list_containers.py` — Docker as an IPC example

**`Ex9.sh`.** Creates a Docker network (`exercise_net`) and starts ten containers
(`bash_container_1` … `bash_container_10`) attached to it, each running
`sh -c "while true; do sleep 3600; done"` so they stay alive for inspection.

**`Ex10.sh`.** Reverses `Ex9.sh`: finds all containers with the
`bash_container_` prefix, stops any that are running, force-removes all of them,
and then removes the `exercise_net` network — a clean teardown of everything
`Ex9.sh` created.

**`list_containers.py`.** Instead of using the `docker` CLI or the Python Docker
SDK, this script talks to the Docker Engine API directly over its **Unix domain
socket** (`/var/run/docker.sock`) using `requests_unixsocket`, requesting
`GET /containers/json?all=0` (running containers only). This is the IPC angle of
the lab: the Docker CLI and the Docker daemon are separate processes that
communicate over a local socket, and this script shows that any process with
permission to open that socket can talk to the daemon the same way the official
CLI does — a concrete example of socket-based IPC between unrelated processes on
the same host.

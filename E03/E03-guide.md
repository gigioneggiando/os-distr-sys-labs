# Lab 03 Guide: Operating Systems & File Systems

A walkthrough with hints and explanations for exercises 01–06.

## General Tips Across All Exercises

| Task | Command |
|---|---|
| Build an image | `docker build -t <TAG> -f <DOCKERFILE-NAME> .` |
| List running containers | `docker ps` |
| Follow logs live | `docker logs -f <name>` |
| Check host CPU count | `nproc` |
| Check a container's exit code | `docker run <image>; echo $?` |
| Log into MySQL | `sudo mysql` (or `mysql -u <user> -p`) |

**Golden rule for `COPY` errors:** the path in `COPY <source> <dest>` is relative to the **build context** — the folder you pass to `docker build` (usually `.`), not to wherever the Dockerfile physically sits.

**Golden rule for organizing exercises:** one folder per exercise, each with its own `Dockerfile` and script, to avoid Docker picking up the wrong file.

**Golden rule for resource experiments:** change one variable at a time (CPU *or* memory, not both) so you can clearly attribute any change in behavior to the setting you changed.

---

## Exercise 01: Fibonacci

**Goal:** Write a script that calculates Fib35 and prints how long it took.

### Key concepts
- A **naive recursive** Fibonacci implementation is deliberately inefficient (exponential time complexity) — that's what makes it a useful CPU-bound benchmark for later exercises.
- `time.time()` before and after the call gives elapsed wall-clock time.

### The script (`fib.py`)

```python
import time


def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    start_time = time.time()
    result = fib(35)
    end_time = time.time()

    elapsed = end_time - start_time
    print(f"{elapsed}")
```

### Run

```bash
python3 fib.py
```

### Tuning the number
- Under ~1 second → increase to `fib(37)` or `fib(38)`.
- Over ~10–15 seconds → decrease to `fib(32)` or `fib(33)`.
- A good target is **2–8 seconds**, so CPU throttling is clearly visible in Exercise 02.

---

## Exercise 02: CPU Usage

**Goal:** Run `fib.py` inside a container and observe how `--cpus` affects execution time.

### Key concepts
- `--cpus=<VALUE>` limits how much CPU time a container may consume, e.g. `--cpus="2.5"` allocates two and a half CPUs' worth of time.
- A single-threaded script can only ever use **one core's worth** of computation — giving it more available cores does not speed it up.

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY fib.py .

CMD ["python3", "fib.py"]
```

### Build

```bash
docker build -t fib-test .
```

### Run with different CPU limits

```bash
docker run --rm --cpus="0.25" fib-test
docker run --rm --cpus="0.5"  fib-test
docker run --rm --cpus="1.0"  fib-test
docker run --rm --cpus="2.0"  fib-test
docker run --rm fib-test          # no limit, for comparison
```

### Expected behavior
- `--cpus="0.25"` should run roughly **4x slower** than `--cpus="1.0"`.
- Going from `--cpus="1.0"` to `--cpus="2.0"` (or unlimited) should make **little to no difference**, since `fib.py` never uses more than one core.

### Discussion point
More CPUs ≠ faster, unless the workload is actually parallelized across multiple threads or processes.

---

## Exercise 03: Memory Usage

**Goal:** Run a memory-heavy script inside a container and observe how `-m` and `--memory-swap` affect it.

### Key concepts
- `-m=<VALUE>` limits how much RAM a container can use, e.g. `-m="2.5g"`.
- `--memory-swap=<VALUE>` sets the **total** of memory + swap available, and must be used together with `-m`. For example, `-m="512m" --memory-swap="1g"` means 512 MB RAM + 512 MB swap.
- If a container exceeds its memory limit with no swap available, it gets killed by the OOM (out-of-memory) killer — exit code `137`.

### The script (`memory.py`)

```python
import time


def use_space(loops):
    for i in range(0, loops):
        arr = bytearray(512000000)


start_time = int(round(time.time() * 1000))
use_space(2)
end_time = int(round(time.time() * 1000))
print('time: ' + str(end_time - start_time))
```

This allocates a ~512 MB `bytearray` twice, so it needs roughly **1 GB** total to run comfortably.

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY memory.py .

CMD ["python3", "memory.py"]
```

### Build

```bash
docker build -t memory-test .
```

### Run with different memory limits

```bash
docker run --rm -m="2g" memory-test                              # plenty of headroom
docker run --rm -m="1g" memory-test                               # right at the edge
docker run --rm -m="512m" --memory-swap="1g" memory-test          # too little RAM, swap available
docker run --rm -m="512m" --memory-swap="512m" memory-test        # too little RAM, no swap
```

### Expected behavior
- Enough memory → finishes quickly.
- Too little memory, swap available → much slower (disk swap is far slower than RAM), but completes.
- Too little memory, no swap → container is OOM-killed (exit code `137`).

### Discussion point
Constraining memory below what a program needs doesn't just slow it down proportionally — it can kill the process outright, or force a much slower disk-based fallback if swap is allowed.

---

## Exercise 04: Disk Read Performance

**Goal:** Benchmark sequential and random read performance using `fio`.

### Key concepts
- `fio` runs jobs defined in `.fio` job files and reports throughput (`bw`), IOPS, and latency.
- `direct=1` bypasses the OS page cache, measuring true disk performance instead of cached reads.
- Read speed is calculated as:
$$\text{speed (MiB/s)} = \text{IOPS} \times \text{block size}$$

### Required changes (apply to both job files)

```
runtime = 120
direct = 1
```

### Install fio

```bash
sudo apt-get update && sudo apt-get install -y fio
```

### Run the jobs

```bash
fio fio-rand-read.fio
fio fio-seq-read.fio
```

### Reading the output

Find the `iops` line in each report:
```
iops : min=..., max=..., avg=X, stdev=..., samples=...
```

| Job | Block size | Avg IOPS |
|---|---|---|
| fio-rand-read | 4K | *(fill in)* |
| fio-seq-read | 256K | *(fill in)* |

### Calculate speed

```
speed (rand) = IOPS_rand × 4K
speed (seq)  = IOPS_seq  × 256K
```

### Discussion point
Sequential reads with large blocks typically achieve much higher throughput than small random reads, since contiguous access minimizes repositioning overhead on the storage device.

---

## Exercise 05: Disk Write Performance

**Goal:** Benchmark sequential and random write performance using `fio`.

### Key concepts
Same setup as Exercise 04, but writing instead of reading — real data will be written to your storage device.

### Required changes (apply to both job files)

```
bs = 4K
numjobs = 4   # in fio-rand-write.fio
numjobs = 1   # in fio-seq-write.fio
runtime = 120
direct = 1
```

### Run the jobs

```bash
fio fio-rand-write.fio
fio fio-seq-write.fio
```

### Reading the output

| Job | Block size | numjobs | Avg IOPS |
|---|---|---|---|
| fio-rand-write | 4K | 4 | *(fill in)* |
| fio-seq-write | 4K | 1 | *(fill in)* |

With `numjobs=4`, use the **aggregate** IOPS from the "Run status group" summary at the bottom of the report, not any single job's individual line.

### Calculate speed

```
speed (rand) = IOPS_rand × 4K
speed (seq)  = IOPS_seq  × 4K
```

---

## Exercise 06: Implement File System [Optional]

**Goal:** Implement a FUSE filesystem backed by MySQL, so files and their contents live as rows in a database table.

### Key concepts
- `getattr()` and `readdir()` run when `ls -l` is executed.
  - `readdir()` returns the list of filenames in the directory.
  - `getattr()` returns metadata (mode, size) about a specific file.
- `read()` runs when a file's content is read (e.g. via `cat`), using the provided `encoded()` helper to convert content to UTF-8 bytes.
- Missing files should raise `FuseOSError(ENOENT)`.

### Step 1 — Install MySQL

```bash
sudo apt-get update
sudo apt-get install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Step 2 — Create the database, table, and a dedicated app user

```sql
CREATE DATABASE IF NOT EXISTS fusedb;
USE fusedb;

CREATE TABLE IF NOT EXISTS Files (
    fileid INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filesize INT NOT NULL,
    filecontent TEXT
);

INSERT INTO Files (filename, filesize, filecontent) VALUES
    ('hello.txt', 7, 'Hello!'),
    ('world.txt', 7, 'World!');

CREATE USER IF NOT EXISTS 'fuseuser'@'%' IDENTIFIED BY 'fusepass';
GRANT ALL PRIVILEGES ON fusedb.* TO 'fuseuser'@'%';
FLUSH PRIVILEGES;
```

Apply directly from the shell:
```bash
sudo mysql < setup.sql
```

Note: `filesize` should match the byte length of the *encoded* content (the `encoded()` helper appends `\n`), so `'Hello!'` (6 chars) becomes 7 bytes once encoded.

Using a dedicated `fuseuser` account (rather than `root`) avoids the default MySQL-on-Ubuntu behavior where `root@localhost` uses socket-based authentication and rejects password-based connections from client libraries.

### Step 3 — Install Python dependencies

Since Ubuntu's system Python is externally managed, install packages inside a virtual environment:

```bash
sudo apt-get install -y python3-full python3-venv fuse libfuse2
python3 -m venv venv
source venv/bin/activate
pip install fusepy mysql-connector-python
```

**Known issue: `OSError: Unable to find libfuse`.** The `fusepy` library only
speaks the FUSE **2** ABI, loaded from `libfuse.so.2`. Recent OS releases
(Debian 13 "trixie", and the generic `python:3.12` Docker tag, which now
resolves to trixie) ship FUSE **3** only and no longer package `libfuse2` at
all — installing plain `fuse` is not enough, and on trixie `apt-get install
libfuse2` has no candidate. If you hit this error, you have two options:
- Explicitly install `libfuse2` (works on Ubuntu and on Debian 12 "bookworm";
  confirmed working in this exact exercise), **or**
- Use a Debian 12 ("bookworm")-based image if you're in Docker (see the hint
  below) — the plain `python:3.12` tag currently resolves to Debian 13,
  which cannot install `libfuse2` at all.

### Step 4 — Allow non-root mount access

FUSE's `allow_other` mount option requires an explicit opt-in on Ubuntu:

```bash
sudo sed -i 's/#user_allow_other/user_allow_other/' /etc/fuse.conf
```

### Step 5 — Fill in the TODOs in `main.py`

- **`getattr()`**: query `Files` for a row matching the filename; raise `ENOENT` if not found, otherwise return `S_IFREG` mode and the stored `filesize`.
- **`read()`**: query `filecontent` for the filename; raise `ENOENT` if not found, otherwise return `encoded(content)[offset:offset+size]`.
- **`readdir()`**: query all `filename` values from the table and append them to `['.', '..']`.
- **`__main__`**: establish the MySQL connection with `mysql.connector.connect(...)` before mounting the filesystem, so all `Operations` methods can use it.

### Step 6 — Run it

```bash
mkdir -p /tmp/fusemount
python3 main.py /tmp/fusemount --host localhost --user fuseuser --password fusepass --database fusedb
```

### Step 7 — Test it

From another terminal:
```bash
ls -l /tmp/fusemount
cat /tmp/fusemount/hello.txt
```

### Expected behavior
- `ls -l` lists every filename stored in the `Files` table with correct sizes.
- `cat` prints the corresponding `filecontent` for each file.

### Hint: Running inside Docker
FUSE needs elevated privileges to mount inside a container. Pin the base
image to `python:3.12-bookworm` rather than the plain `python:3.12` tag —
the latter now resolves to Debian 13 "trixie", which cannot install
`libfuse2` (see the known issue above) and will fail with `OSError: Unable
to find libfuse`:
```bash
docker run --privileged --rm -it -v $(pwd):/app -w /app python:3.12-bookworm bash
apt-get update && apt-get install -y fuse libfuse2
```
Verified working end to end with this setup: `ls -l /tmp/fusemount` lists
`hello.txt` and `world.txt` with the correct sizes, and `cat` on each file
prints `Hello!` / `World!` as expected. The MySQL server can run as a
separate container on the same Docker network — pass its container name as
`--host` in Step 6 (e.g. `--host mysql` if that's the service name in your
`docker-compose.yml`).

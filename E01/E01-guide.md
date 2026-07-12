# Lab 01 Guide: Docker

A walkthrough with hints and explanations for exercises 02–06.

---

## General Tips Across All Exercises

**Build command anatomy:**
```bash
docker image build -t <TAG> -f <DOCKERFILE-NAME> <BUILD-CONTEXT-PATH>
```
- `-t` → name your image (always do this, easier than remembering IDs).
- `-f` → only needed if your file isn't literally named `Dockerfile`.
- `<BUILD-CONTEXT-PATH>` (often `.`) → the folder Docker treats as the root for any `COPY`/`ADD` paths.

**Golden rule for `COPY` errors:** the path in `COPY <source> <dest>` is always relative to the **build context**, not to wherever the Dockerfile happens to sit. When in doubt, `cd` into the folder you're building from and check `ls` there first.

**Golden rule for organizing multiple exercises:** one folder per exercise, each with its own `Dockerfile`. This avoids Docker accidentally picking up the wrong one.

---

## Exercise 02: Hello, World!

**Goal:** Run your first container using a pre-built image from Docker Hub.

### Concept
- `docker container run <IMAGE>` looks for the image locally first, then pulls it from Docker Hub if not found.
- `hello-world` is a minimal test image used to confirm Docker is installed and working.

### Steps

```bash
docker container run hello-world
```

or the shorter equivalent:

```bash
docker run hello-world
```

### What happens
1. Docker client talks to the Docker daemon.
2. Daemon pulls `hello-world` from Docker Hub (if not cached locally).
3. Daemon creates a container from the image and runs it.
4. Output streams back to your terminal.

### Troubleshooting
- **Permission denied** → prefix with `sudo`.
- **Docker daemon not running** → `sudo systemctl start docker`.

---

## Exercise 03: Home-cooked Hello, World!

**Goal:** Write your own Dockerfile and build your own image instead of using one from Docker Hub.

### Key concepts
- A **Dockerfile** is a plain text file (named exactly `Dockerfile`, no extension) with build instructions.
- Instructions are `UPPERCASE`, arguments are lowercase: `INSTRUCTION argument`.
- `#` = comment line.
- **Image** = a template/class. **Container** = a running instance/object.
- `FROM` sets the base image.
- `RUN` executes a command **at build time** (e.g., installing packages, creating files).
- `CMD` sets the command that runs **when the container starts** — this defines the container's lifetime. When it finishes, the container stops.

### The Dockerfile

```dockerfile
FROM ubuntu

RUN echo "Hello, World! 42." > helloWorld

CMD ["cat", "helloWorld"]
```

### Build

```bash
docker image build -t hello-tag .
```

- `-t hello-tag` gives the image a memorable name (tag) instead of a random ID.
- `.` tells Docker to use the current directory as the **build context** (where it looks for the Dockerfile and any files to copy).

### Run

```bash
docker run hello-tag
```

**Expected output:**
```
Hello, World! 42.
```

### Hint: Custom Dockerfile name
If your file isn't named `Dockerfile`, use `-f`:
```bash
docker image build -f my-custom-name -t hello-tag .
```

---

## Exercise 04: Building Dockerfiles

**Goal:** Learn the `COPY` instruction and interactive containers.

### Key concepts
- `COPY <host-path> <container-path>` copies files/folders from your machine into the image at build time.
- `-it` flag = interactive terminal. Combined with `bash` as the run argument, it drops you into a live shell inside the container.
- Without `-it`, you can't type inside the container.

### The Dockerfile (as given)

```dockerfile
FROM ubuntu

COPY L1E4/ /home/

CMD bash
```

> **Important:** The `COPY` source path is *relative to the build context* (the `.` you pass to `docker build`), **not** relative to where the Dockerfile physically sits, unless you build from inside that same folder.

### Two valid folder layouts

**Option A — Dockerfile outside the folder:**
```
project/
├── Dockerfile
└── L1E4/
    └── print.py
```
```dockerfile
COPY L1E4/ /home/
```
Build from `project/`:
```bash
docker image build -t exercise4 .
```

**Option B — Dockerfile inside the folder (common gotcha):**
```
L1E4/
├── Dockerfile
└── print.py
```
Now the context IS `L1E4/`, so copying `L1E4/` again would be wrong. Instead:
```dockerfile
COPY print.py /home/print.py
```
Build from inside `L1E4/`:
```bash
cd L1E4
docker image build -t exercise4 .
```

### Task 1–3: Build, run interactively, install Python manually

```bash
docker image build -t exercise4 .
docker run -it exercise4
```
Inside the container:
```bash
apt update
apt install -y python3
python3 /home/print.py
```
Expected: `200`

Exit with `exit`.

### Task 4: Automate it — install Python and run script on container start

```dockerfile
FROM ubuntu

RUN apt update && apt install -y python3

COPY print.py /home/print.py

CMD ["python3", "/home/print.py"]
```

Rebuild and run (no `-it` needed since nothing is interactive anymore):
```bash
docker image build -t exercise4-auto .
docker run exercise4-auto
```
Expected: `200`

### Common pitfalls
- **"No such file or directory"** → the file wasn't copied to where you think. Debug with:
  ```bash
  find / -name "print.py" 2>/dev/null
  ls -la /home/
  ```
- **Wrong Dockerfile picked up** → Docker always builds `./Dockerfile` by default. If you have multiple exercises in one folder, either:
  - Put each exercise in its **own folder**, or
  - Rename files (`Dockerfile.ex3`, `Dockerfile.ex4`) and always specify `-f`:
    ```bash
    docker image build -f Dockerfile.ex4 -t exercise4 .
    ```
- **Permission denied installing packages** → inside a container you're usually `root` already, so `apt install` should work without `sudo`. If you get a lock-file error, that's usually about running `apt` on the **host** (your actual Ubuntu machine) instead of inside the container — check your shell prompt to confirm where you are.

---

## Exercise 05: Expose Container Contents

**Goal:** Serve a PHP website from a container and access it via your browser using port mapping.

### Key concepts
- `-p <HOST-PORT>:<CONTAINER-PORT>` maps a port on your machine to a port inside the container.
- Apache serves HTTP traffic on port **80** by default — that's the `<CONTAINER-PORT>` you expose.
- `EXPOSE 80` in a Dockerfile is documentation of intent; the actual mapping still needs `-p` at runtime.

### Typical Dockerfile

```dockerfile
FROM php:7.2-apache

COPY index.php /var/www/html/

EXPOSE 80
```

> Adjust the `COPY` line based on where your `.php` files actually live relative to the build context — don't move files just to match a generic example. If your file is `index.php` sitting next to the Dockerfile, copy it directly:
> ```dockerfile
> COPY index.php /var/www/html/
> ```
> If you have a whole folder of PHP files, copy the folder:
> ```dockerfile
> COPY src/ /var/www/html/
> ```
> Or copy everything in the current build context:
> ```dockerfile
> COPY . /var/www/html/
> ```

### Build

```bash
docker image build -t exercise5 .
```

### Run with port mapping

```bash
docker run -p 8080:80 exercise5
```

Now visit:
```
http://localhost:8080
```

### Expected terminal output (Apache logs)

```
AH00558: apache2: Could not reliably determine the server's fully qualified domain name...
[mpm_prefork:notice] AH00163: Apache/x.x.x (Debian) PHP/x.x.x configured -- resuming normal operations
[core:notice] Command line: 'apache2 -D FOREGROUND'
172.17.0.1 - - [date] "GET / HTTP/1.1" 200 ...
```

The `AH00558` warning is harmless — it's just Apache complaining it doesn't know its own hostname.

### Stopping the container
```bash
Ctrl + C
```

---

## Exercise 06: Make Your Script

**Goal:** Write a custom Python script, copy it into a container, install Python, and run the script as the container's main process.

### Key concepts
- `CMD` with a **finite** process (a script that runs and exits) means the container stops once that process ends. This is different from something like Apache, which runs forever until stopped manually.
- The `-u` flag on `python3` disables output buffering, so `print()` statements show up immediately instead of being held back until the script finishes.

### The Python script

```python
import time

print("Starting counter...")

for i in range(1, 6):
    print(f"Count: {i}")
    time.sleep(1)

print("Script finished!")
```

Save as `counter.py`.

### The Dockerfile

```dockerfile
FROM ubuntu

RUN apt update && apt install -y python3

COPY counter.py /home/counter.py

CMD ["python3", "-u", "/home/counter.py"]
```

### Build and run

```bash
docker image build -t exercise6 .
docker run exercise6
```

### Expected output

```
Starting counter...
Count: 1
Count: 2
Count: 3
Count: 4
Count: 5
Script finished!
```

### Why `-u` matters here
Without it, Docker may buffer all the `print()` output and dump it all at once at the end (or not show it at all if you're piping/redirecting), making it look like the script hangs instead of counting live. `-u` forces real-time, line-by-line output — perfect for watching a loop with `time.sleep()` in action.

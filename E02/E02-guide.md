# Lab 02 Guide: Containers & Docker Compose

A walkthrough with hints and explanations for exercises 01–05.

## General Tips Across All Exercises

| Task | Command |
|---|---|
| Follow logs live | `docker logs -f <name>` |
| List running containers | `docker ps` |
| Exec into a running container | `docker exec -it <name> bash` |
| Stop a container | `docker stop <name>` |
| Remove a container | `docker rm <name>` |
| Tear down a compose stack | `docker compose down` |

**Golden rule for `COPY` errors:** the path in `COPY <source> <dest>` is relative to the **build context** — the folder you pass to `docker build` (usually `.`), not to wherever the Dockerfile physically sits.

**Golden rule for waiting on MySQL:** the official `mysql` image restarts itself once internally during first-time initialization. Don't try to connect the moment the container starts — watch the logs and wait for the line `ready for connections`.

---

## Exercise 01: Expose Apache

**Goal:** Run a pre-built Apache image and expose it on the host.

```bash
docker run -p 7000:80 cocodolan/php:apache
```

- `-p 7000:80` maps container port 80 (Apache's default) to host port 7000.
- On Apple Silicon (M1/M2/etc.), add `--platform linux/amd64` since the image is built for amd64.

Visit `http://localhost:7000` in your browser. Any response in the terminal logs (even a `GET /` line) means the exercise is complete.

---

## Exercise 02: PHP Server

**Goal:** Build a custom PHP+Apache image that will later need to talk to MySQL.

### The Dockerfile

```dockerfile
FROM php:apache

RUN docker-php-ext-install mysqli

COPY . /var/www/html/
```

- `docker-php-ext-install mysqli` installs the PHP extension needed to talk to MySQL — without it, the site's database features silently fail even after Exercise 05 is wired up correctly.
- `COPY . /var/www/html/` copies everything in the build context (your `.php` files) into Apache's default document root.

### Build and run

```bash
docker build -t l2e2 .
docker run -p 7000:80 l2e2
```

Visit `http://localhost:7000`. The site loading — even with broken database functionality — is expected at this stage; there's no database connected yet.

---

## Exercise 03: Ubuntu MySQL

**Goal:** Manually install and drive a MySQL server inside a plain Ubuntu container, to understand what the official `mysql` image automates for you later.

```bash
docker run -it ubuntu bash
```

Inside the container:

```bash
apt update && apt install -y mysql-server
service mysql start
mysql -u root
```

### Common pitfall: `service mysql start` fails

On newer Ubuntu images (e.g. Ubuntu 26.04 with `mysql-server` 8.4+), you may see:

```
grep: /etc/init.d/mysql: No such file or directory
mysql: unrecognized service
```

This happens because recent `mysql-server` packages rely entirely on **systemd** instead of shipping a classic `/etc/init.d/mysql` script, and containers don't run systemd by default. Check with:

```bash
dpkg -l | grep mysql
ls -la /etc/init.d/ | grep mysql
```

If the package is installed (`dpkg -l` shows it) but no init script exists, start the server manually with `mysqld_safe` instead:

```bash
mkdir -p /var/run/mysqld
chown mysql:mysql /var/run/mysqld

# only needed if /var/lib/mysql is empty/uninitialized:
mysqld --initialize-insecure --user=mysql

mysqld_safe --user=mysql &
```

Give it a few seconds, confirm it's running with `ps aux | grep mysqld`, then connect as usual:

```bash
mysql -u root
```

Once at the `mysql>` prompt, practice the management commands:

```sql
SHOW DATABASES;
CREATE DATABASE test_db;
USE test_db;
CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(50));
INSERT INTO test_table VALUES (1, 'example');
SHOW TABLES;
SELECT * FROM test_table;
DELETE FROM test_table;
DROP TABLE test_table;
DROP DATABASE test_db;
EXIT;
```

**Hint:** every SQL statement needs a trailing `;` — a common source of "nothing happens" confusion is a missing semicolon.

---

## Exercise 04: MySQL Container

**Goal:** Package a MySQL server with pre-loaded configuration into a Dockerfile, instead of setting it up by hand like in Exercise 03.

### Key concept
The official `mysql` image automatically executes any `.sql` file found in `/docker-entrypoint-initdb.d/` the first time the container initializes its data directory. Anything in that script — `CREATE DATABASE`, `CREATE TABLE`, `INSERT` — becomes part of the running server.

### Folder layout

```
L2E4/
├── Dockerfile
└── init.sql
```

### The Dockerfile

```dockerfile
FROM mysql

ENV MYSQL_ALLOW_EMPTY_PASSWORD yes

COPY init.sql /docker-entrypoint-initdb.d/
```

- `MYSQL_ALLOW_EMPTY_PASSWORD yes` lets you log in as `root` with no password — convenient for exercises, never for production.
- `COPY init.sql ...` stages your SQL script exactly where the entrypoint script looks for it.

### Build and run

```bash
docker build -t l2e4 .
docker run --name l2e4 -d l2e4
```

### Wait for it to actually be ready

```bash
docker logs -f l2e4
```

Watch until you see:
```
[Server] /usr/sbin/mysqld: ready for connections.
```
Then `Ctrl+C` out of the log stream (this doesn't stop the container, just detaches your terminal).

### Connect and verify

```bash
docker exec -it l2e4 bash
mysql -u root
```

Inside the MySQL CLI:

```sql
SHOW DATABASES;
USE <your_database_name>;
SHOW TABLES;
SELECT * FROM <your_table_name>;
```

If the database/table from `init.sql` show up with the right data, the exercise is complete.

### Common pitfall
```
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
```
This means you connected *before* MySQL finished initializing. Solution: always confirm `ready for connections` in the logs first, don't just wait a guessed number of seconds.

---

## Exercise 05: Expose Content (Docker Compose)

**Goal:** Wire Exercise 02 (web) and Exercise 04 (database) together into one multi-container system using Docker Compose, instead of running them as two disconnected containers.

### Key concept
Docker Compose gives each service a hostname equal to its service name, on an internal network it creates automatically. This means whatever hostname your app's config expects, your compose service **must be named exactly that** — there's no separate "networking config" step needed for basic service-to-service communication.

### Folder layout

```
E02/
├── docker-compose.yml
├── L2E4/                 <- db service (Exercise 04's Dockerfile)
│   ├── Dockerfile
│   └── init.sql
└── L2E2/                 <- web service (Exercise 02's Dockerfile)
    ├── Dockerfile
    └── config.php  (and other site files)
```

### Step 1 — Check what hostname your app expects

Open `config.php` and look at `$servername`:

```php
$servername = "db_container";
```

Whatever this value is, that's the name your compose service **must** use — this is Information 4 in the exercise sheet.

### Step 2 (OPTIONAL) — Add the auth flag to the sql Dockerfile

Per Information 3 on the exercise sheet, older MySQL versions could block Compose-driven connections due to a default authentication plugin the PHP `mysqli` driver didn't support. The suggested fix was to add a startup flag:

```dockerfile
FROM mysql

ENV MYSQL_ALLOW_EMPTY_PASSWORD yes

COPY init.sql /docker-entrypoint-initdb.d/

CMD ["--default-authentication-plugin=mysql_native_password"]
```

> ⚠️ **Try this only if the plain Exercise 04 Dockerfile (no `CMD` line) doesn't work for you.** `--default-authentication-plugin` was deprecated in MySQL 8.0.27+ and **removed entirely in MySQL 9.x**. The plain `mysql` tag today pulls a 9.x release (confirmed: 9.7.1), so adding this `CMD` causes the server to fail initialization outright:
> ```
> [ERROR] [MY-000067] [Server] unknown variable 'default-authentication-plugin=mysql_native_password'.
> [ERROR] [MY-013236] [Server] The designated data directory /var/lib/mysql/ is unusable.
> [ERROR] [MY-010119] [Server] Aborting
> ```
> **Recommended default: skip this step.** Reuse your Exercise 04 Dockerfile exactly as-is:
> ```dockerfile
> FROM mysql
>
> ENV MYSQL_ALLOW_EMPTY_PASSWORD yes
>
> COPY init.sql /docker-entrypoint-initdb.d/
> ```
> With `MYSQL_ALLOW_EMPTY_PASSWORD` set, a passwordless `root` connection works fine on modern MySQL without the flag — this has been confirmed working end-to-end with the PHP `mysqli` driver.
>
> If you specifically need this flag (e.g. your course requires an older MySQL for another reason), pin the image version instead of using the flag on a 9.x server:
> ```dockerfile
> FROM mysql:5.7
> ...
> CMD ["--default-authentication-plugin=mysql_native_password"]
> ```
> If your data directory ever gets stuck in a broken/aborted state from a failed start (like the error above), remove the container before rebuilding: `docker rm -f db_container` (or the relevant container name/ID).

### Step 3 — Write the docker-compose.yml

```yaml
version: "3"

services:

  db_container:
    build: ./L2E4

  web:
    build: ./L2E2
    depends_on:
      - db_container
    ports:
      - "7000:80"
```

- `db_container:` — the service name **is** the hostname other services see, so it must match `config.php` exactly.
- `build: ./L2E4` / `build: ./L2E2` — each service builds from its own subfolder's Dockerfile; paths are relative to the compose file's location.
- `depends_on: - db_container` — only guarantees start *order*, not that MySQL is ready to accept connections yet (see the pitfall below).
- `ports: - "7000:80"` — same `HOST:CONTAINER` mapping syntax as `docker run -p`.

#### A note on naming

Docker Compose names things at three different levels, and it's easy to mix them up:

- **Service name** (`db_container`, `web` above) — the key under `services:`. This is also the internal DNS hostname other services use to reach it, which is why it must match `config.php`.
- **Project name** — by default, Compose uses the **name of the folder containing `docker-compose.yml`** (e.g. `e02`) as a prefix for everything it creates (containers, networks, volumes). You'll see this if you run `docker ps` after `docker compose up` — containers show up as `e02-db_container-1` and `e02-web-1`, not just `db_container`/`web`.
- **Container name** — auto-generated as `<project>-<service>-<number>` unless you override it.

If you want predictable names instead of relying on the folder, you can set either:

```yaml
name: e02-lab  # sets the project name explicitly, at the top of the file

services:
  db_container:
    build: ./L2E4
    container_name: db_container   # pins the actual container name too
  ...
```

or pass a project name at the command line without editing the file:

```bash
docker compose -p e02-lab up
```

This matters mainly when you're running `docker exec`/`docker logs` against a container and the auto-generated name doesn't match what you expected — check `docker ps` first if a name-based command fails.

### Step 4 — Run it

From inside `E02/`:

```bash
docker compose up
```

### Step 5 — Test it

Visit:
```
http://localhost:7000
```

Try inserting some data through the site — if it saves and shows up, the web and db containers are correctly talking to each other.

### Common pitfalls

- **Web container starts before MySQL is ready.** `depends_on` only waits for the container to *start*, not for MySQL inside it to finish initializing. If your first page load errors out on the database connection, refresh after a few seconds, or restart just the web service:
  ```bash
  docker compose restart web
  ```
- **Hostname mismatch.** If `config.php` says `db_container` but your compose service is named `db` or `sql`, the web container will fail to resolve the hostname. Keep them identical.
- **Auth plugin errors on modern MySQL.** If you added the optional `CMD` flag from Step 2 and see `unknown variable 'default-authentication-plugin=...'` in the logs, the data directory is now marked unusable. Remove the container (`docker rm -f db_container`), delete the `CMD` line from the sql Dockerfile, rebuild, and try again without it.
- **Stale containers/images after edits.** If you change a Dockerfile and `docker compose up` doesn't pick it up, force a rebuild:
  ```bash
  docker compose up --build
  ```

### Tearing down

```bash
docker compose down
```

This stops and removes both containers (and the network Compose created), leaving your images intact for the next `docker compose up`.

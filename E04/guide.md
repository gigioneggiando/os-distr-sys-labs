# Guide for the student assistant

## Recommended path
1. Start from [materials/Resources/code1.c](materials/Resources/code1.c) and ask students to predict the output.
2. Move to [materials/Resources/code2.c](materials/Resources/code2.c) and point out what changes with the mutex.
3. Compare [materials/Resources/code3.c](materials/Resources/code3.c) with the previous version and ask why synchronization is correct but less parallel.
4. Use [materials/Resources/code4.c](materials/Resources/code4.c) as a classic mistake example: the lock must always be released.
5. End with [materials/list_containers.py](materials/list_containers.py) to show an IPC example against Docker.

## How to explain the Docker part
- The `Dockerfile` compiles all the C sources in `materials/Resources/`.
- The script `scheduler.sh` shows a simple example of periodic shell tasks.
- `Ex9.sh` and `Ex10.sh` are used for container startup and cleanup exercises.

## Useful classroom questions
- Why can `counter` produce different results on each run?
- Does the mutex solve correctness, or only mutual exclusion?
- What happens if a thread acquires a lock and never releases it?
- Why use the Docker socket instead of the `docker ps` command?

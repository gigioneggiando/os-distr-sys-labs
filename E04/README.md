# Lab 04 Guide: Multitasking & IPC

This folder contains a self-contained version of the lab on multitasking, synchronization, and IPC.

## Contents
- [explanation.md](explanation.md) with the theoretical background.
- [guide.md](guide.md) with the recommended teaching path for students.
- [materials/](materials) with the original lab code and support scripts.
- [solutions/](solutions) with the question PDF and answer sheet.

## Lab goal
Understand how the behavior of two threads changes when race conditions, mutexes, CPU affinity, and access to the Docker Engine through a Unix socket are introduced.

## Quick start
1. Open a terminal in this folder.
2. Build the image:
   ```bash
   docker build -t lab04-multitasking -f materials/Dockerfile materials
   ```
3. Enter the container:
   ```bash
   docker run -it lab04-multitasking
   ```
4. Compile or run the binaries in `materials/Resources/`, or try the scripts `materials/Ex9.sh` and `materials/Ex10.sh`.

Verified: the image builds (`gcc`/`make` compile `code1`–`code5` from
`materials/Resources/`) and each binary runs and behaves as described in
`solutions/answers.md`. `materials/Ex9.sh` and `materials/Ex10.sh` were also
run directly (outside the container, against the Docker daemon): `Ex9.sh`
created the `exercise_net` network and 10 `bash_container_*` containers, and
`Ex10.sh` cleanly removed all of them and the network, leaving no residue.

## About the question PDF
No blank, professor-issued question sheet for this exercise was found among the
original course files — only an already-annotated walkthrough (`E04-v1.pdf`,
mixed prompts and answers, several blank pages). That file is used as
`solutions/questions.pdf` because it is the closest thing to an official
question sheet available and it covers the same code/scripts as `materials/`.
See the note at the top of `solutions/answers.md` for details.

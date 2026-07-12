## Theoretical background

## What the lab teaches
The lab shows three key ideas:

1. Two threads accessing the same shared variable can produce nondeterministic results.
2. A `mutex` protects a critical section, but using it poorly can serialize too much or block the program.
3. CPU affinity and the operating system scheduler influence the order in which threads run.

## Main concepts

### Race condition
When two threads read and modify `counter` without synchronization, the final value depends on the execution order.

### Mutex
The mutex makes access to the shared variable mutually exclusive. It must always be unlocked, otherwise the other threads will keep waiting.

### Affinity CPU
Pinning a thread to a specific core helps observe scheduler behavior more clearly, but it does not solve race conditions by itself.

### Docker Engine API
`list_containers.py` does not use the classic Docker client: it talks directly to the daemon through the Unix socket and calls the `/containers/json` endpoint.

## Reading the C files
- `code1.c`: version without protection for the shared variable.
- `code2.c`: protection with a mutex in the critical section.
- `code3.c`: mutex held for longer, so parallelism is reduced.
- `code4.c`: deliberately problematic example with a lock that is not released correctly.
- `code5.c`: extreme variant to discuss scheduling and non-terminating code.

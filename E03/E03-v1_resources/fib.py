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
 

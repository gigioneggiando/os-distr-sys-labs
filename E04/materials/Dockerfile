# Uses a lightweight linux base
FROM ubuntu:22.04

# Update packages 
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copies only the .c files
COPY Resources/ /app/

# Compile using make
RUN if [ -f makefile ]; then make; else gcc -o program *.c; fi

# Default command
CMD ["/bin/bash"]

# Build the runnable examples from the HPC pages.
#   make          build everything that this machine has a compiler for
#   make run      build and run them
#
# CUDA is not included: the examples on the CUDA page were not executed when
# the site was written, and are left for you to build with nvcc.

CC      ?= gcc
MPICC   ?= mpicc
CFLAGS  ?= -O2 -Wall
OMPFLAGS = -fopenmp

MPI_BINS = hello overlap
OMP_BINS = reduce hist

all: $(MPI_BINS) $(OMP_BINS)

hello overlap: %: %.c
	$(MPICC) $(CFLAGS) $< -o $@

reduce hist: %: %.c
	$(CC) $(CFLAGS) $(OMPFLAGS) $< -o $@

run: all
	@echo "== MPI: hello =="
	mpirun --oversubscribe -np 4 ./hello | sort
	@echo; echo "== MPI: blocking vs overlapped (5 reps at 4 ranks) =="
	@for r in 1 2 3 4 5; do mpirun --oversubscribe -np 4 ./overlap; done
	@echo; echo "== OpenMP: reduction, bit-reproducibility across thread counts =="
	@for t in 1 4 8; do OMP_NUM_THREADS=$$t ./reduce; done
	@echo; echo "== OpenMP: false sharing =="
	@for t in 1 2 4 8; do OMP_NUM_THREADS=$$t ./hist; done

clean:
	rm -f $(MPI_BINS) $(OMP_BINS)

.PHONY: all run clean

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HALO 4096          /* fat halo, so communication is not free */
#define NINT 200000        /* interior points */
#define STEPS 200

static void work(double *u, int lo, int hi) {
    for (int i = lo; i < hi; i++) u[i] = 0.5 * u[i] + 0.25 * (u[i-1] + u[i+1]);
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    int left = (rank - 1 + size) % size, right = (rank + 1) % size;

    int n = NINT + 2 * HALO;
    double *u = calloc(n, sizeof *u);
    for (int i = 0; i < n; i++) u[i] = rank + 1.0;

    /* --- blocking: communicate, then compute --- */
    MPI_Barrier(MPI_COMM_WORLD);
    double t0 = MPI_Wtime();
    for (int s = 0; s < STEPS; s++) {
        MPI_Sendrecv(&u[HALO], HALO, MPI_DOUBLE, left, 0,
                     &u[HALO + NINT], HALO, MPI_DOUBLE, right, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Sendrecv(&u[NINT], HALO, MPI_DOUBLE, right, 1,
                     &u[0], HALO, MPI_DOUBLE, left, 1,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        work(u, HALO, HALO + NINT);
    }
    double t_block = MPI_Wtime() - t0;

    /* --- overlapped: post, compute interior, wait, compute edges --- */
    MPI_Barrier(MPI_COMM_WORLD);
    t0 = MPI_Wtime();
    MPI_Request req[4];
    for (int s = 0; s < STEPS; s++) {
        MPI_Irecv(&u[0], HALO, MPI_DOUBLE, left, 1, MPI_COMM_WORLD, &req[0]);
        MPI_Irecv(&u[HALO + NINT], HALO, MPI_DOUBLE, right, 0, MPI_COMM_WORLD, &req[1]);
        MPI_Isend(&u[HALO], HALO, MPI_DOUBLE, left, 0, MPI_COMM_WORLD, &req[2]);
        MPI_Isend(&u[NINT], HALO, MPI_DOUBLE, right, 1, MPI_COMM_WORLD, &req[3]);
        work(u, 2 * HALO, NINT);                       /* needs no halo */
        MPI_Waitall(4, req, MPI_STATUSES_IGNORE);
        work(u, HALO, 2 * HALO);                       /* now the edges */
        work(u, NINT, HALO + NINT);
    }
    double t_ovlp = MPI_Wtime() - t0;

    double b, o;
    MPI_Reduce(&t_block, &b, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    MPI_Reduce(&t_ovlp,  &o, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    if (rank == 0)
        printf("ranks=%d  blocking %.3f s   overlapped %.3f s   speedup %.2fx\n",
               size, b, o, b / o);
    free(u);
    MPI_Finalize();
    return 0;
}

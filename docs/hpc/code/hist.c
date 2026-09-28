#include <omp.h>
#include <stdio.h>
#include <stdlib.h>

#define NBIN 8                 /* bins per thread: 8 longs = 64 B = one cache line */
#define N 100000000L

int main(void) {
    int T = omp_get_max_threads();
    unsigned *idx = malloc(N * sizeof *idx);
    unsigned seed = 12345;
    for (long i = 0; i < N; i++) { seed = seed * 1103515245u + 12345u; idx[i] = (seed >> 16) % NBIN; }

    /* (a) adjacent per-thread histograms: neighbouring threads share cache lines */
    long *packed = calloc((size_t)T * NBIN, sizeof *packed);
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        long *mine = packed + (long)omp_get_thread_num() * NBIN;
        #pragma omp for
        for (long i = 0; i < N; i++) mine[idx[i]]++;
    }
    double t_false = omp_get_wtime() - t0;

    /* (b) each thread's histogram padded onto its own cache lines */
    const int PAD = 64 / sizeof(long);                 /* one line of slack */
    long *padded = calloc((size_t)T * (NBIN + PAD), sizeof *padded);
    t0 = omp_get_wtime();
    #pragma omp parallel
    {
        long *mine = padded + (long)omp_get_thread_num() * (NBIN + PAD);
        #pragma omp for
        for (long i = 0; i < N; i++) mine[idx[i]]++;
    }
    double t_pad = omp_get_wtime() - t0;

    long chk = 0; for (int t = 0; t < T; t++) for (int b = 0; b < NBIN; b++) chk += packed[t*NBIN+b];
    printf("threads=%d  false-shared %6.3f s   padded %6.3f s   speedup %.2fx   (check %ld)\n",
           T, t_false, t_pad, t_false / t_pad, chk);
    free(idx); free(packed); free(padded);
    return 0;
}

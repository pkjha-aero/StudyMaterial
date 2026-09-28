#include <omp.h>
#include <stdio.h>

int main(void) {
    const long N = 100000000L;
    double sum = 0.0;

    #pragma omp parallel for reduction(+:sum)
    for (long i = 0; i < N; i++)
        sum += 1.0 / ((double)i + 1.0);

    printf("threads=%d  sum=%.10f\n", omp_get_max_threads(), sum);
    return 0;
}

#include "PerfGroup.h"
#include <perfmon/pfmlib_perf_event.h>
#include <cstdio>

int main() {
    int ret = pfm_initialize();
    if (ret != PFM_SUCCESS) {
        fprintf(stderr, "Cannot initialize library: %s", pfm_strerror(ret));
        return 1;
    }
    std::vector<std::string> counters{"cycles",  // leader
                                      "instructions",
                                      "branches",
                                      "L1-dcache-loads",
                                      "L1-dcache-load-misses",
                                      "L1-dcache-prefetches",
                                      "L1-icache-load-misses",  // leader
                                      "L1-icache-loads",
                                      "branch-load-misses",
                                      "branch-loads",
                                      "dTLB-load-misses",
                                      "dTLB-loads",
                                      "iTLB-load-misses",  // leader
                                      "iTLB-loads",
                                      "branch-instructions",
                                      "branch-misses",
                                      "cache-misses",
                                      "cache-references",
                                      "stalled-cycles-backend",  // leader
                                      "stalled-cycles-frontend"};
    PerfGroup grp;
    if (!grp.init(counters)) {
        fprintf(stderr, "Failed to initialize\n");
        return 1;
    }
    grp.start();
    grp.stop();
    for (int j = 0; j < counters.size(); ++j) {
        printf("%s:%lu ", counters[j].c_str(), grp[j]);
    }
    printf("\n");
}

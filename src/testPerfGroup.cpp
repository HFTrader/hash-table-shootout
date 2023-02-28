#include "PerfGroup.h"
#include <perfmon/pfmlib_perf_event.h>
#include <cstdio>

int main()
{
    int ret = pfm_initialize();
    if (ret != PFM_SUCCESS)
    {
        fprintf(stderr, "Cannot initialize library: %s", pfm_strerror(ret));
        return 1;
    }
    std::vector<std::string> counters = {"cache-misses:u", "cycles:u",
                                         "instructions:u", "branch-misses:u", "instructions:u", "minor-faults:u", "cpu-migrations:u"};
    PerfGroup grp;
    if (!grp.init(counters))
    {
        fprintf(stderr, "Failed to initialize\n");
        return 1;
    }
    grp.start();
    grp.stop();
    for (int j = 0; j < counters.size(); ++j)
    {
        printf("%s:%lu ", counters[j].c_str(), grp[j]);
    }
    printf("\n");
}

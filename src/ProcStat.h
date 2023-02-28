#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct ProcStat {
    int pid;
    char comm[200], state;
    int ppid, pgrp, session, tty_nr, tpgid;
    unsigned int flags;
    unsigned long int minflt, cminflt, majflt, cmajflt, utime, stime;
    long int cutime, cstime, priority, nice, num_threads, itrealvalue;
    unsigned long long int starttime;
    unsigned long int vsize;
    long int rss;
    unsigned long int rsslim;
    void *startcode, *endcode, *startstack, *kstkesp, *kstkeip;
    unsigned long int signal, blocked, sigignore, sigcatch;
    void *wchan;
    unsigned long int nswap, cnswap;
    int exit_signal, processor;
    unsigned int rt_priority, policy;
    unsigned long long int delayacct_blkio_ticks;
    unsigned long int guest_time;
    long int cguest_time;
    void *start_data, *end_data, *start_brk, *arg_start, *arg_end;
    void *env_start, *env_end;
    int exit_code;

    bool read() {
        FILE *procfp = fopen("/proc/self/stat", "r");
        if (procfp == NULL) {
            fprintf(stderr, "Could not open /proc/self/stat\n");
            return false;
        }

        int numitems = ::fscanf(
            procfp,
            "%d %s %c %d %d %d %d %d %u %lu %lu %lu %lu %lu %lu "
            "%ld %ld %ld %ld %ld %ld %llu %lu %ld %lu "
            "%lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu "
            "%d %d %u %u %llu %lu %ld %lu %lu %lu %lu %lu %lu %lu %d",
            &pid, comm, &state, &ppid, &pgrp, &session, &tty_nr, &tpgid, &flags, &minflt,
            &cminflt, &majflt, &cmajflt, &utime, &stime, &cutime, &cstime, &priority,
            &nice, &num_threads, &itrealvalue, &starttime, &vsize, &rss, &rsslim,
            &startcode, &endcode, &startstack, &kstkesp, &kstkeip, &signal, &blocked,
            &sigignore, &sigcatch, &wchan, &nswap, &cnswap, &exit_signal, &processor,
            &rt_priority, &policy, &delayacct_blkio_ticks, &guest_time, &cguest_time,
            &start_data, &end_data, &start_brk, &arg_start, &arg_end, &env_start,
            &env_end, &exit_code);

        ::fclose(procfp);
        if (numitems != 52) {
            fprintf(stderr,
                    "Could not read /proc/self/stat. Read %d items, expected 52\n",
                    numitems);
            return false;
        }

        return true;
    }
};

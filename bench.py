#!/usr/bin/env python3

import sys, os, subprocess, re
from select import select
from subprocess import Popen, PIPE

# samples of use:
#  ./bench.py
#  ./bench.py insert_random_full insert_random_full_reserve
#  APPS='judyHS ska_bytell_hash_map' ./bench.py small_string string

######################################################################
### Fill free to change the following defaults
programs = []
for line in open("apps.txt"):
    line = re.sub("#.*$", "", line).strip()
    if line:
        programs.append(line)

minkeys  =         200
maxkeys  = 2*1000*1000
step_percent =  10 # you may use this variable instead of "interval" for exponetial step
timeout = 0

######################################################################
mypid = os.getpid()
filename = 'output-%d'% ( mypid, )
outfile = open(filename, 'w')

benchtypes = [
    'insert_random_shuffle_range',
    'reinsert_random_shuffle_range',
    'read_random_shuffle_range',
    'insert_random_full',
    'reinsert_random_full',
    'insert_random_full_reserve',
    'read_random_full',
    'read_miss_random_full',
    'delete_random_full',
    'read_random_full_after_delete',
    'iteration_random_full',
    'insert_small_string',
    'reinsert_small_string',
    'insert_small_string_reserve',
    'read_small_string',
    'read_miss_small_string',
    'delete_small_string',
    'read_small_string_after_delete',
    'insert_string',
    'reinsert_string',
    'insert_string_reserve',
    'read_string',
    'read_miss_string',
    'delete_string',
    'read_string_after_delete'
]

numprocs = 1
if len(sys.argv) > 1:
    numprocs = int( sys.argv[1] )

points = []
keys = minkeys
while keys <= maxkeys:
    points.append(keys)
    keys = int(max(keys + 1, keys * (100 + step_percent) / 100))

timeout = 0.1
for nkeys in points:
    for benchtype in benchtypes:
        for program in programs:
                try:
                    events = "cache-misses,branch-misses,cycles,branches,instructions,page-faults,page-faults-min,page-faults-maj,stalled-cycles-frontend,stalled-cycles-backend"
                    command =  [ './build/' + program, str(nkeys), benchtype]
                    procs = list( [ Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for np in range(numprocs) ] )
                    lines = []
                    while procs:
                        for p in procs:
                            if p.poll() is not None:
                                data = p.stdout.readline()
                                lines.append( data )
                                #print( data, file = sys.stderr )
                                #print( "   Process finished" )
                                p.stdout.close()
                                procs.remove(p)
                        outlist = [p.stdout for p in procs]
                        errlist = [p.stderr for p in procs]
                        rlist = select( outlist + errlist, [], [], timeout )[0]
                        for f in rlist:
                            data = f.readline()
                            #print( data, file = sys.stderr )
                            lines.append( data )
                    #print( "Batch", nkeys, benchtype, program, " is done " )
                    for output in lines:
                            words = output.strip().split()
                            if len(words)!=13:
                                continue

                            try:
                                runtime_seconds = float(words[0])
                                memory_usage_bytes = int(words[1])
                                cycles = float(words[2])/nkeys
                                instructions = float(words[3])/nkeys
                                cachemisses = float(words[4])/nkeys
                                branchmisses = float(words[5])/nkeys
                                branches = float(words[6])/nkeys
                                pagefaults = float(words[7])/nkeys
                                pagefaultsmin = float(words[8])/nkeys
                                pagefaultsmaj = float(words[9])/nkeys
                                stalledfront = float(words[10])/nkeys
                                stalledback = float(words[11])/nkeys
                                load_factor = float(words[12])

                            except Exception as e:
                                print( e, file=stderr )

                            statvalues = {'cache-misses':cachemisses,'branch-misses':branchmisses,'cycles':cycles,'instructions':instructions,
                                          'page-faults':pagefaults,'page-faults-min':pagefaultsmin, 'page-faults-maj': pagefaultsmaj, 'branches':branches,
                                          'stalled-cycles-frontend':stalledfront, 'stalled-cycles-backend':stalledback }
                            allstats = [benchtype, nkeys, program, "%0.2f" % load_factor,
                                memory_usage_bytes, "%0.9f" % runtime_seconds ]
                            for event_name in events.split(','):
                                if event_name in statvalues:
                                    value = statvalues[event_name]
                                    allstats.append( "%0.3f" % (value,) )
                                else:
                                    allstats.append( "NaN" )
                            line = ','.join(map(str, allstats ))
                            print( line, file=outfile )


                except KeyboardInterrupt as e:
                    sys.exit(130);
                except subprocess.CalledProcessError as e:
                    if e.returncode == 71: # unknown test type for program?
                        continue # silently ignore this case
                    print("Error with %s" % str(['./build/' + program, str(nkeys), benchtype]), file=sys.stderr)
                    print("Exit status is %d" % e.returncode, file=sys.stderr)
                    print(e.stdout, file=sys.stderr)
                    break

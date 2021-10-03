#!/usr/bin/env python3

import sys, os, subprocess, re

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

minkeys  =     200*1000
maxkeys  = 8*1000*1000
#interval =  2*100*1000
step_percent =  20 # you may use this variable instead of "interval" for exponetial step
best_out_of = 1

######################################################################
mypid = os.getpid()
filename = 'output-%d'% ( mypid, )
outfile = open(filename, 'w')

apps_env = os.environ.get('APPS', None)
if apps_env:
    programs = apps_env.strip().split()

short_names = {
    'random_shuffle_range': [
        'insert_random_shuffle_range', 'reinsert_random_shuffle_range',
        'read_random_shuffle_range'
    ],
    'random_full': [
        'insert_random_full', 'reinsert_random_full',
        'insert_random_full_reserve',
        'read_random_full', 'read_miss_random_full',
        'delete_random_full', 'read_random_full_after_delete',
        'iteration_random_full'
    ],
    'small_string': [
        'insert_small_string', 'reinsert_small_string',
        'insert_small_string_reserve',
        'read_small_string', 'read_miss_small_string',
        'delete_small_string',
        'read_small_string_after_delete'
    ],
    'string': [
        'insert_string', 'reinsert_string',
        'insert_string_reserve',
        'read_string', 'read_miss_string',
        'delete_string',
        'read_string_after_delete'
    ]
}

if ("interval" in dir() and "step_percent" in dir()) or \
   ("interval" not in dir() and "step_percent" not in dir()):
    print("Either (exclusively) 'interval' or 'step_percent' variable should be set")
    sys.exit(1)

if len(sys.argv) > 1:
    benchtypes = []
    for x in sys.argv[1:]:
        benchtypes.extend(short_names.get(x, [x]))
else:
    benchtypes = short_names['random_shuffle_range'] + short_names['random_full'] \
        + short_names['small_string'] + short_names['string']

if "interval" in dir():
    points = range(minkeys, maxkeys + 1, interval)
else:
    points = []
    keys = minkeys
    while keys <= maxkeys:
        points.append(keys)
        keys = int(max(keys + 1, keys * (100 + step_percent) / 100))

for nkeys in points:
    for benchtype in benchtypes:
        for program in programs:
            fastest_attempt = 1000000
            fastest_attempt_data = ''

            for attempt in range(best_out_of):
                try:
                    events = "cache-misses,branch-misses,cycles,branches,instructions,page-faults,page-faults-min,page-faults-maj,stalled-cycles-frontend,stalled-cycles-backend"
                    #perf_prefix = ['perf','stat','-x',',','-e', events ] 
                    command_args =  [ './build/' + program, str(nkeys), benchtype]
                    result = subprocess.run( command_args, capture_output=True )
                    if result.returncode != 0:
                        continue

                    output = result.stdout.decode('utf8').split('\n')
                    words = output[0].strip().split()
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
                    if len(words)==13:
                        stalledfront = float(words[10])/nkeys
                        stalledback = float(words[11])/nkeys
                        load_factor = float(words[12])
                    else:
                        stalledfront = 0
                        stalledback = 0
                        load_factor = float(words[10])

                    statvalues = {'cache-misses':cachemisses,'branch-misses':branchmisses,'cycles':cycles,'instructions':instructions,
                    'page-faults':pagefaults,'page-faults-min':pagefaultsmin, 'page-faults-maj': pagefaultsmaj, 'branches':branches,
                    'stalled-cycles-frontend':stalledfront, 'stalled-cycles-backend':stalledback }
                    
                except KeyboardInterrupt as e:
                    sys.exit(130);
                except subprocess.CalledProcessError as e:
                    if e.returncode == 71: # unknown test type for program?
                        continue # silently ignore this case

                    print("Error with %s" % str(['./build/' + program, str(nkeys), benchtype]), file=sys.stderr)
                    print("Exit status is %d" % e.returncode, file=sys.stderr)
                    print(e.stdout, file=sys.stderr)
                    break

                allstats = [benchtype, nkeys, program, "%0.2f" % load_factor,
                                memory_usage_bytes, "%0.6f" % runtime_seconds ]
                for event_name in events.split(','):
                    if event_name in statvalues: 
                        value = statvalues[event_name]
                        allstats.append( "%0.3f" % (value,) )
                    else:
                        allstats.append( "NaN" )
                line = ','.join(map(str, allstats  ))
                #print( line )

                if runtime_seconds < fastest_attempt:
                    fastest_attempt = runtime_seconds
                    fastest_attempt_data = line

            if fastest_attempt != 1000000:
                print(fastest_attempt_data, file=outfile)
                #print(fastest_attempt_data)

        # Print blank line
        if fastest_attempt != 1000000:
            print(file=outfile)
            #print()

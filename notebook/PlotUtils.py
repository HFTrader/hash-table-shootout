import os, sys, json
import numpy as np
import matplotlib.pyplot as plt


fontsize = 10
dpi = 100

def load_data_file( filename ):
    with open( filename, 'r' ) as f:
        lines = [ line.strip() for line in f.read().split('\n') ]
    #print( len(lines) )
    #reinsert_random_shuffle_range,200000,std_unordered_map,0.57,10334208,0.008698,0.263,0.748,247.605,99.448,539.946,0.020
    temp = {}
    for line in lines:
        if not line: continue
        testname,numkeys,container,loadfactor,memsize,timesecs,branchmisses,cachemisses,branches, \
          instructions,cycles,pagefaults,pagefaultsmin,pagefaultsmaj = line.split(',')
        numkeys = int(numkeys)
        branches = float(branches)
        cycles = float(cycles)
        instpercycle = float(instructions)/float(cycles) if cycles > 0 else float('nan')
        branchmisspct = 100*float(branchmisses)/float(branches) if branches > 0 else float('nan')
        branchmisspct = min(branchmisspct,10)
        instpercycle = min(instpercycle,2)
        values = {'loadfactor':float(loadfactor),'memsize':float(memsize)/numkeys,'timesecs':1e9*float(timesecs)/numkeys, \
                 'branchmisses':float(branchmisses),'cachemisses':float(cachemisses),'branches':float(branches), \
                 'instructions':float(instructions),'cycles':float(cycles),'pagefaults':float(pagefaults),'pagefaults-min':float(pagefaultsmin),'pagefaults-maj':float(pagefaultsmaj), 
                 'instpercycle':instpercycle,'branchmisspct': branchmisspct }
        numkeys = int(numkeys)
        for metric,value in values.items():
            key = (testname,container,numkeys,metric)
            temp.setdefault(key,[]).append( value )
    testbycontainer = {}
    for (testname,container,numkeys,metric),values in temp.items():
        average = np.median( values )
        testbycontainer.setdefault((testname,container),{}).setdefault(numkeys,{})[metric] = average
    return testbycontainer

def slice( dataset, fields, containers, tests ):
    for (testname,container),aggvalues in dataset.items():
        if container not in containers:
            continue
        if testname not in tests:
            continue
        keys = aggvalues.keys()
        for j,field in enumerate(fields):
            if field not in fields:
                continue
            values = sorted( [ (key,aggvalues[key][field]) for key in keys ] )
            yield field,testname,container,values

def plot_metrics( setname, alltests, fields, containers, tests ):
    allcontainers = set( [ container for (testname,container) in alltests.keys() ])
    if containers:
        allcontainers = allcontainers and set(containers)
    numfields = len(fields)
    for (testname,container),aggvalues in alltests.items():
        if container not in containers:
            continue
        if testname not in tests:
            continue
        fig = plt.figure(figsize=(10,8), constrained_layout = True )
        fig.suptitle( "Set:%s  Container:%s  Test:%s" % (setname,container,testname), fontsize=14 )
        axs = fig.subplots( int((numfields-1)/4 + 1), 4)
        axs = axs.flat
        for ax in axs[numfields:]:
            ax.remove()
        numkeys = aggvalues.keys()
        for j,field in enumerate(fields):
            ax = axs[j]
            values = sorted( [ (nk,aggvalues[nk][field]) for nk in numkeys ] )
            x,y = zip(*values)
            ax.plot( x,y, 'ko-', markersize=2 )
            ax.set_ylabel( field, fontsize = fontsize )
            ax.grid( True )

        #for j in (4,5,6,7):
        #    axs[j].set_xlabel( 'Hash map size', fontsize = fontsize )

        #fig.tight_layout()
        os.makedirs( 'charts', exist_ok = True )
        filename = 'charts/metrics_%s_%s_%s.png' % (setname, testname, container,)
        plt.show()
        fig.savefig( filename, dpi=dpi )
        plt.close()
        print(setname, filename)

def plot_tests( setname, alltests, fields, containers, tests ):
    allcontainers = set( [ container for (testname,container) in alltests.keys() ])
    if containers:
        allcontainers = allcontainers and set(containers)
    for field in fields:
        for container in allcontainers:
            validtests = set()
            for testname,co1 in alltests.keys():
                if co1 != container:
                    continue
                if tests and (testname not in tests):
                    continue
                validtests.add( testname )

            validtests = sorted( list(validtests) )
            numtests = len(validtests)
            fig = plt.figure(figsize=(10,8), constrained_layout = True )
            fig.suptitle( 'Set:%s Container:%s  Metric:%s' % (setname,container,field,), fontsize = 14 )
            axs = fig.subplots( int((numtests-1)/4 + 1), 4)
            axs = axs.flat
            for ax in axs[numtests:]:
                ax.remove()
            for j,testname in enumerate(validtests):
                aggvalues = alltests[(testname,container)]
                numkeys = aggvalues.keys()
                values = sorted( [ (nk,aggvalues[nk][field]) for nk in numkeys ] )
                x,y = zip( *values )

                ax = axs[j]
                ax.plot( x, y, 'ko-', markersize=2 )
                ax.set_title( testname,  fontsize = fontsize )
                ax.set_xscale( 'log')
                ax.grid( True )

            os.makedirs( 'charts', exist_ok = True )
            filename = 'charts/operations_%s_%s_%s.png' % (setname,field,container )
            plt.show()
            fig.savefig( filename, dpi=dpi )
            plt.close()
            #print(setname, filename)

def plot_containers( setname, alltests, fields, containers, tests ):
    allcontainers = set( [ container for (testname,container) in alltests.keys() ])
    if containers:
        allcontainers = allcontainers and set(containers)
    validtests = set()
    for testname,co1 in alltests.keys():
        if tests and (testname not in tests):
            continue
        validtests.add( testname )

    for field in fields:
        for testname in validtests:
            numcontainers = len(allcontainers)
            fig = plt.figure(figsize=(10,8), constrained_layout = True )
            fig.suptitle( 'Set:%s Test:%s  Metric:%s' % (setname,testname,field,), fontsize = 14 )
            #axs = fig.subplots(1,1)
            axs = fig.subplots( int((numcontainers-1)/3 + 1), 3)
            axs = axs.flat
            for ax in axs[numcontainers:]:
                ax.remove()
            xydata = []
            maxy = 0
            miny = 1E9
            for j,container in enumerate(allcontainers):
                aggvalues = alltests.get((testname,container))
                if not aggvalues:
                    continue
                numkeys = aggvalues.keys()
                values = sorted( [ (nk,aggvalues[nk][field]) for nk in numkeys ] )
                x,y = zip( *values )
                xydata.append( (axs[j],container,x,y) )
                maxy = max( (maxy, max(y)) )
                miny = min( (miny, min(y)) )

            for ax,container,x,y in xydata:
                ax.set_title( container, fontsize = fontsize )
                ax.plot( x, y, 'ko-', markersize=2 )
                ax.set_xscale( 'log')
                ax.set_ylim( [miny,maxy] )
                ax.grid( True )

            os.makedirs( 'charts', exist_ok = True )
            filename = 'charts/containers_%s_%s_%s.png' % (setname,field,container )
            plt.show()
            fig.savefig( filename, dpi=dpi )
            plt.close()

def plot_containers2( setname, alltests, fields, containers, tests ):
    allcontainers = set( [ container for (testname,container) in alltests.keys() ])
    if containers:
        allcontainers = allcontainers and set(containers)
    validtests = set()
    for testname,co1 in alltests.keys():
        if tests and (testname not in tests):
            continue
        validtests.add( testname )

    for field in fields:
        for testname in validtests:
            numcontainers = len(allcontainers)
            fig = plt.figure(figsize=(10,8), constrained_layout = True )
            fig.suptitle( 'Set:%s Test:%s  Metric:%s' % (setname,testname,field,), fontsize = 14 )
            axs = fig.subplots(1,1)
            #axs = fig.subplots( int((numcontainers-1)/4 + 1), 4)
            #axs = axs.flat
            #for ax in axs[numcontainers:]:
            #    ax.remove()
            for j,container in enumerate(allcontainers):
                aggvalues = alltests.get((testname,container))
                if not aggvalues:
                    continue
                numkeys = aggvalues.keys()
                values = sorted( [ (nk,aggvalues[nk][field]) for nk in numkeys ] )
                x,y = zip( *values )

                ax = axs
                ax.plot( x, y, markersize=2, label=container )
            ax.set_yscale( 'log')
            ax.set_xscale( 'log')
            ax.grid( True )
            ax.legend()

            os.makedirs( 'charts', exist_ok = True )
            filename = 'charts/containers_%s_%s_%s.png' % (setname,field,container )
            plt.show()
            fig.savefig( filename, dpi=dpi )
            plt.close()

#-------------------------------------------------------------------------------
# Name:        o2n
# Purpose:     read SET from OPTISTRUCT bulk data format file,
#              write SET to NASTRAN case control format file
#
# Author:      Kyle Meehan
#
# Created:     19/06/2017
# Copyright:   (c) meeha 2017
# Licence:     none (totally free)
#-------------------------------------------------------------------------------
import itertools
import fileinput, string, sys, os

def o2n():
    #
    # o2n is a totally free converter from OPTISTRUCT bulk data format file to NASTRAN case control format file
    #
    # next step pluck set ID and set TYPE
    # and then detect end the SET,
    # and then write "ELEM" type SETs to the outfile.
    #
    fn='OPTISTRUCT_SET.fem'
    fn_ElSet='NASTRAN_SET.dat'
    if not os.path.exists(fn):
        print("OPTISTRUCT_SET_file does not exist in o2n, OPTISTRUCT_SET_file= "+ fn)
        sys.exit()
    #input all the lines of the file into "lines_list"
    with open(fn, 'rb') as fi:
        lines_list = fi.readlines()
    #scan lines for a set
    set_list = []
    found_set = 0
    for line in lines_list:
        words=line.split()
        #skip blank lines (no words on the line)
        if words:
            if found_set:
                if words[0].lower().strip()=='+':
                    #if at set extension, extract up to 8 set elements off the line
                    set_list.extend(words[1:8])
                    pass
                else:
                    #if at end of ELEM type set, output element list to NASTRAN case control format
                    if set_type.lower().strip()=='elem':
                        ElSet_writer(fn_ElSet,set_ID,set_list)
                        pass
                    #reset set_list and found_set
                    found_set = 0
                    set_list=[]
                    pass
            if words[0].lower().strip()=='set':
                found_set = 1
                #extract set ID and type off the line
                set_ID = words[1]
                set_type = words[2]
                print(set_ID, set_type)
                pass
    # if here and found_set==1, set still needs to be written
    # write set
    if found_set:
        found_set = 0
        #if at end of ELEM type set, output element list to NASTRAN case control format
        if set_type.lower().strip()=='elem':
            ElSet_writer(fn_ElSet,set_ID,set_list)
        pass






def grouper(n, iterable):
    '''
    grouper returns list slices in
    '''
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk

def ElSet_writer(fn_ElSet,id_ElSet,ElSet_list):
    '''
    ElSet_writer - write ElSet_list to fn_ElSet with id_ElSet in NASTRAN case control format

$example NASTRAN case control set format
SET 1 = 10023   , THRU    , 10098   , 10115   , THRU    , 10118   ,
        10350   , THRU    , 10389   , 10399   , THRU    , 10406   ,
        10444   , THRU    , 10447   , 10453   , THRU    , 10455   ,
        10461   , THRU    , 10468

$example set format 2
SET 101 = 1,4,5,
        41097053,41097054,41097056,41097057,41097059,41097060,
        1073,1075 THRU 1179,
        1000 THRU 1070

    '''
    with open(fn_ElSet, 'wb') as f:
        eslen= len(ElSet_list)
        nchunks=eslen/6
        chunklen=nchunks*6
        chunkrem=eslen%6
##        f.write(" len= "+str(eslen)+"\n")
##        f.write(" len/6= "+str(eslen/6)+"\n")
##        f.write(" len%6= "+str(eslen%6)+"\n")
        #header
        f.write("SET "+str(id_ElSet)+" = ")
        ichunk=0
        # change from 0 to 5 remainder to 1 to 6 remainder
        if chunkrem==0:
            chunkrem=6
        for chunk in grouper(6, ElSet_list):
            ichunk=ichunk+1
            if nchunks==0:
                # less than 1 full set of 6, up to 5 remainder
                f.write("".join((str(x).ljust(8)+", ") for x in ElSet_list[eslen-chunkrem:eslen-1]))
                f.write(ElSet_list[-1])
                pass
            elif ichunk<nchunks:
                # 1 full set of 6, with continuation
                f.write("".join((str(x).ljust(8)+", ") for x in chunk))
                f.write("\n        ")
            elif ichunk==nchunks:
                if chunkrem!=6:
                    # last full chunk, with continuation
                    f.write("".join((str(x).ljust(8)+", ") for x in chunk))
                    f.write("\n        ")
                # up to 6 remainder, no continuation
                f.write("".join((str(x).ljust(8)+", ") for x in ElSet_list[eslen-chunkrem:eslen-1]))
                f.write(ElSet_list[-1])
                f.write("\n")
                pass

def main():
    o2n()
    pass

if __name__ == '__main__':
    main()

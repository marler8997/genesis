def lcc_template(*, name, version, libc, libc_dev, binutils):
    # TODO: need to get this from the binutils object somehow
    binutils_as_path = 'bin/i686-linux-gnu-as'
    binutils_ld_path = 'bin/i686-linux-gnu-ld'
    # TODO: need to get this from libc/libc_dev somehow
    libc_ld_so_path = 'lib/libc.so'
    libc_lib_path = 'lib'
    libc_dev_crt1 = 'lib/crt1.o'
    libc_dev_crti = 'lib/crti.o'

    return {'in':[libc, libc_dev, binutils],'ops':[
        {'op':'fetchArchive',
         'url':'https://github.com/drh/lcc/archive/v'+version+'.tar.gz',
         'inHash':'ocmfxwaivnsxsgrw5ahjevcpuv72u6ym',
         'outHash':'f6o7ykbnwlskhnp7nbch3qsucprvi25w',
         'to':'@stage'},
        {'op':'mkdir','path':'@stage/out'},
        {'op':'makeFile','path':'@stage/out/genesis.c','content':f'''#include <string.h>
static char rcsid[] = "$Id$";

#ifndef LCCDIR
#define LCCDIR "@finalout"
#define LIBC_DEV "@{libc_dev}"
#endif

char *suffixes[] = {{ ".c", ".i", ".s", ".o", ".out", 0 }};
char inputs[256] = "";
char *cpp[] = {{ LCCDIR "/bin/cpp",
    "-U__GNUC__", "-D_POSIX_SOURCE", "-D__STDC__=1", "-D__STRICT_ANSI__",
    "-Dunix", "-Di386", "-Dlinux",
    "-D__unix__", "-D__i386__", "-D__linux__", "-D__signed__=signed",
    "-D__DEFINED_va_list",
    "-Dva_list=...",
    "-D__DEFINED___isoc_va_list",
    "-D__isoc_va_list=...",
    "$1", "$2", "$3", 0 }};
char *include[] = {{"-I" LIBC_DEV "/include"}};
char *com[] = {{LCCDIR "/bin/rcc", "-target=x86/linux", "$1", "$2", "$3", 0 }};
char *as[] = {{ "@{binutils}/{binutils_as_path}", "-o", "$3", "$1", "$2", 0 }};
char *ld[] = {{
    "@{binutils}/{binutils_ld_path}",
    "-m", "elf_i386",
    "-dynamic-linker", "@{libc}/{libc_ld_so_path}",
    "-o", "$3",
    "@{libc_dev}/{libc_dev_crt1}", "@{libc_dev}/{libc_dev_crti}",
    //LCCDIR "/gcc/crtbegin.o",
    "$1", "$2",
    //"-L" LCCDIR,
    //"-llcc",
    //"-L" LCCDIR "/gcc", "-lgcc", "-lc", "-lm",
      "-L@{libc}/{libc_lib_path}",
      "-lc",
    //LCCDIR "/gcc/crtend.o", "/usr/lib/crtn.o",
    0 }};

extern char *concat(char *, char *);

int option(char *arg) {{
      if (strncmp(arg, "-lccdir=", 8) == 0) {{
        if (strcmp(cpp[0], LCCDIR "/gcc/cpp") == 0)
            cpp[0] = concat(&arg[8], "/gcc/cpp");
        include[0] = concat("-I", concat(&arg[8], "/include"));
        include[1] = concat("-I", concat(&arg[8], "/gcc/include"));
        ld[9]  = concat(&arg[8], "/gcc/crtbegin.o");
        ld[12] = concat("-L", &arg[8]);
        ld[14] = concat("-L", concat(&arg[8], "/gcc"));
        ld[19] = concat(&arg[8], "/gcc/crtend.o");
        com[0] = concat(&arg[8], "/rcc");
    }} else if (strcmp(arg, "-p") == 0 || strcmp(arg, "-pg") == 0) {{
        ld[7] = "/usr/lib/gcrt1.o";
        ld[18] = "-lgmon";
    }} else if (strcmp(arg, "-b") == 0)
        ;
    else if (strcmp(arg, "-g") == 0)
        ;
    else if (strncmp(arg, "-ld=", 4) == 0)
        ld[0] = &arg[4];
    else if (strcmp(arg, "-static") == 0) {{
        ld[3] = "-static";
        ld[4] = "";
    }} else
        return 0;
    return 1;
}}
'''},
        {'op':'run','cmd':['make',
                           '-C', '@stage/lcc-'+version,
                           'BUILDDIR=@stage/out',
                           'HOSTFILE=@stage/out/genesis.c',
                           #'HOSTFILE=@stage/lcc-'+version+'/etc/linux.c',
                           'all']},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/out/bprint','dst':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/out/cpp','dst':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/out/lburg','dst':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/out/lcc','dst':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/out/rcc','dst':'@tmpout/bin'},
        # TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Add 'depend' ops
        # TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ]}
'''
add_lcc('4_2', True,
        'binutils-cross-linux32-linux64-prebuilt', 'bin/i686-linux-gnu-as', 'bin/i686-linux-gnu-ld',
        'musl',
        # TODO: need to switch to musl-linux32
        obj_set.resolve_name('musl-libc-1.1.19-linux32-prebuilt'),
        'lib/libc.so', # in musl, libc.so is also the dynamic linker
        'lib',
        obj_set.resolve_name('musl-libc-dev-1.1.19-linux32-prebuilt'),
        'lib/crt1.o',
        'lib/crti.o'
)
'''

# commented out because can't find binutils variation on windows
#obj_set.add_variation_set('lcc', lcc_template).add({
#    'version':['4_2'],
#    #'binutils':[obj_set.alias_to_hash_name('binutils-cross-linux32-linux64-prebuilt')],
#    'binutils':[obj_set.get_variation('binutils-cross-linux32', platform='linux32')],
#    'libc':[obj_set.get_variation('musl', platform='linux32')],
#    'libc_dev':[obj_set.get_variation('musl-dev', platform='linux32')],
#})

# commented out because can't find binutils variation on windows
#obj_set.add_variation_set('lcc-bootstrap', lcc_template).add({
#    'version':['4_2'],
#    #'binutils':[obj_set.alias_to_hash_name('binutils-cross-linux32-linux64-prebuilt')],
#    'binutils':[obj_set.get_variation('binutils-cross-linux32', platform='linux32')],
#    'libc':[obj_set.get_variation('musl', platform='linux32')],
#    'libc_dev':[obj_set.get_variation('musl-dev', platform='linux32')],
#})



'''
add_lcc('4_2', True,
        #obj_set.get_variation('binutils', cross='linux32', platform='linux64', 'bin/i686-linux-gnu-as', 'bin/i686-linux-gnu-ld',
        obj_set.alias_to_hash_name('binutils-cross-linux32-linux64-prebuilt'), 'bin/i686-linux-gnu-as', 'bin/i686-linux-gnu-ld',
        'musl',
        # TODO: need to switch to musl-linux32
        obj_set.get_variation('musl', debian_platform='i386'),
        'lib/libc.so', # in musl, libc.so is also the dynamic linker
        'lib',
        obj_set.get_variation('musl-dev', debian_platform='i386'),
        'lib/crt1.o',
        'lib/crti.o'
)
'''

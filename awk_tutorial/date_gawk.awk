#! /usr/bin/awk -f
# originally a gawk file 

BEGIN {
    format = "%a %b %e %H:%M:%S %Z %Y";
    print strftime(format);
}
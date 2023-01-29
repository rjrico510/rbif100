#!/usr/bin/gawk -f
# renamed since this works in awk
{
    print tolower($0);
}
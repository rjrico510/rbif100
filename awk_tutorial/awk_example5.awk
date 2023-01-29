#!/usr/bin/awk -f
# changed 100 to 3 from example
# example has bug in braces
{ if (NR > 3) {
	print NR, $0;
}
}
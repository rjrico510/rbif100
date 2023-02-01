#!/bin/sh
sed '
/one/ {
      N
	  /two/ {
			N
			/three/ {
			        N
					s/one\ntwo\nthree/1+2+3/
					}
			}
	  }
'
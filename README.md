Asma
====

This language is an attempt to make programming in the Hack language
(of "The Elements of Computing Systems", not Facebook's [Hack][1]!)

It is designed to abstract the A and C commands, but still stay on the
"Assembly" side of languages than providing higher level constructs.
Asma operations do not map 1:1 to Hack Assembly, but still provide the
same functionality: Only the native Hack operators are supported.

A simple example, computing `n + n+1 + ... + x-1 + x`

	# Computes n + n+1 + ... + x-1 + x
	# Inputs:
	# 	R2: Lower bound of the sequence
	# 	R1: Upper bound of the sequence
	# Outputs:
	# 	R2: The result of the summation
    START:
    	start = R0
    	end = R1
    	i = start
    	result = 0

    LOOP:
    	goto END if i - n == 0

    	result = result + i

    	i = i + 1
    	goto LOOP

    END:
    	R2 = result

You might notice the code is both shorter and more readable than the
interleaved A and C commands of the native Hack Assembly. To keep
debugging rather simple without the need of any special mechanism, the
compiler automatically adds the Asma source as a comment above every
translated operation.

[1]: http://hacklang.org/
primes = []
for x in range(1, 1000):
    z = x
    for y in range(2, x):
        if not(x % y):
            z = None
            break
    if z: primes.append(z)
    if len(primes) == 161: break
diffs = []
for p in range(1, len(primes)):
    #print primes[p], '\t', primes[p] - primes[p-1]
    diffs.append(primes[p] - primes[p-1])
for p in range(0, len(diffs)):
    print diffs[p] % 5,
print ''

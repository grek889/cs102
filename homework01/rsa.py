def is_prime(n: int) -> bool:
    """
    >>> is_prime(2)
    True
    >>> is_prime(11)
    True
    >>> is_prime(8)
    False
    """
    # PUT YOUR CODE HERE
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    c = 3
    while c * c <= n and n % c != 0:
        c += 2
        
    return c * c > n
    
def generate_keypair(p: int, q: int): 
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')

    n = p*q
    # PUT YOUR CODE HERE

    phi = (p-1)*(q-1)
    # PUT YOUR CODE HERE

    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)

    # Use Euclid's Algorithm to verify that e and phi(n) are comprime
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    # Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, phi)
    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))
def gcd(a: int, b: int) -> int:
    """
    >>> gcd(12, 15)
    3
    >>> gcd(3, 7)
    1
    """
    # PUT YOUR CODE HERE
    while b != 0:
        a, b = b, a % b
    return a
def multiplicative_inverse(e: int, phi: int) -> int:
    """
    >>> multiplicative_inverse(7, 40)
    23
    """
    # PUT YOUR CODE HERE
    x = phi
    y = e
    arr = []
    while x % y != 0:
        arr.append(x // y)
        r = x
        x = y
        y = r % y
    x = 0
    y = 1
    arr[::-1]
    for i in range(len(arr)):
        r = x
        x = y
        y = r - y * arr[i]
    return y % phi
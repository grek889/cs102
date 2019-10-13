def encrypt_caesar(plaintext, k = 3) -> str:
    """
        >>> encrypt_caesar("PYTHON")
        'SBWKRQ'
        >>> encrypt_caesar("python")
        'sbwkrq'
        >>> encrypt_caesar("Python3.6")
        'Sbwkrq3.6'
        >>> encrypt_caesar("")
        ''
        """
    ciphertext = ''
    for ch in plaintext:
        if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            code = ord(ch) + k
            if 'a' <= ch <= 'z' and code > ord('z'):
                code -= 26
            elif 'A' <= ch <= 'Z' and code > ord('Z'):
                code -= 26
            ciphertext += chr(code)
        else:
            ciphertext += ch
    return ciphertext

def decrypt_caesar(ciphertext, k = 3) -> str:
    """
        >>> decrypt_caesar("SBWKRQ")
        'PYTHON'
        >>> decrypt_caesar("sbwkrq")
        'python'
        >>> decrypt_caesar("Sbwkrq3.6")
        'Python3.6'
        >>> decrypt_caesar("")
        ''
        """
    plaintext = ''
    for ch in ciphertext:
        if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            code = ord(ch) - k
            if 'a' <= ch <= 'z' and code < ord('a'):
                code += 26
            elif 'A' <= ch <= 'Z' and code < ord('A'):
                code += 26
            plaintext += chr(code)
        else:
            plaintext += ch
    return plaintext


plaintext = str(input(' Enter Your message: '))
k = int(input('Enter you key: '))
while k > 26:
    k = int(input('Enter you key: '))

ciphertext = encrypt_caesar(plaintext, k)
print("Cod: " + ciphertext)
print("Not Cod: " + decrypt_caesar(ciphertext, k))
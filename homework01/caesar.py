def encrypt_caesar(plaintext: str) -> str:
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
    # PUT YOUR CODE HERE
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    encrypt= input(massage)
    key = 3
    ciphertext = ""
    for letter in encrypt:
        position = alphabet.find(letter)
        newPosition = position + key
        if letter in alphabet: 
            ciphertext = ciphertext + alphabet[newPosition]
        else:
            ciphertext = ciphertext + letter
    print(ciphertext)
    return ciphertext    
def decrypt_caesar(ciphertext: str) -> str:
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
    # PUT YOUR CODE HERE
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzp"
    encrypt= input(massage)
    key = '3'
    plaintext = ""
    for letter in encrypt:
        position = alphabet.find(letter)
        newPosition = position - key - 78
        if letter in alphabet: 
            plaintext = plaintext + alphabet[newPosition]
        else:
            plaintext = plaintext + letter
    return plaintext
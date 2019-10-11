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
encrypt = input('Enter a clear massage: ')
key = int(input('please enter a key(number from 1-25): '))

encrypted = ""
for letter in encrypt:
    position = alphabet.find(letter)
    newPosition = position + key
    if letter in alphabet: 
        encrypted = encrypted + alphabet[newPosition]
    else:
        encrypted = encrypted + letter
print("Your cipher is: ", encrypted)
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
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
encrypt = input('Enter a clear massage: ')
key = int(input('please enter a key(number from 1-25): '))
encrypt = encrypt.lower()
encrypted = ""
for letter in encrypt:
    position = alphabet.find(letter)
    newPosition = position - key
    if letter in alphabet: 
        encrypted = encrypted + alphabet[newPosition]
    else:
        encrypted = encrypted + letter
print("Your cipher is: ", encrypted)
    return plaintext

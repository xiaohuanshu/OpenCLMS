import random
import string


# generate random password
def generate_password(length=8):
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    size = length
    return ''.join(random.choice(chars) for _ in range(size))


if __name__ == '__main__':
    print(generate_password(8))

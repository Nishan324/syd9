def encrypt_file(shift1, shift2):
    with open("raw_text.txt", "r") as infile, open("encrypted_text.txt", "w") as outfile:
        for char in infile.read():
            if char.islower():
                if 'a' <= char <= 'm':
                    shift = shift1 * shift2
                    new_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                elif 'n' <= char <= 'z':
                    shift = shift1 + shift2
                    new_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                else:
                    new_char = char

            elif char.isupper():
                if 'A' <= char <= 'M':
                    shift = shift1
                    new_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                elif 'N' <= char <= 'Z':
                    shift = shift2 ** 2
                    new_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                else:
                    new_char = char
            else:
                new_char = char

            outfile.write(new_char)



def decrypt_file(shift1, shift2):
    with open("encrypted_text.txt", "r") as infile, open("decrypted_text.txt", "w") as outfile:
        for char in infile.read():
            if char.islower():
                if 'a' <= char <= 'm':
                    shift = shift1 * shift2
                    new_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                elif 'n' <= char <= 'z':
                    shift = shift1 + shift2
                    new_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                else:
                    new_char = char

            elif char.isupper():
                if 'A' <= char <= 'M':
                    shift = shift1
                    new_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                elif 'N' <= char <= 'Z':
                    shift = shift2 ** 2
                    new_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                else:
                    new_char = char
            else:
                new_char = char

            outfile.write(new_char)


def verify_decryption():
    with open("raw_text.txt", "r") as file1, open("decrypted_text.txt", "r") as file2:
        if file1.read() == file2.read():
            print("Decryption successful! Files match.")
        else:
            print("Decryption failed! Files do not match.")

def main():
    shift1 = int(input("Enter shift1 value: "))
    shift2 = int(input("Enter shift2 value: "))

    encrypt_file(shift1, shift2)
    decrypt_file(shift1, shift2)
    verify_decryption()
main()

#Read the encrypted content
with open("encrypted.bin", "rb") as f:
    ciphertext = f.read()

#known plaintext prefix for TryHackMe flags (4 bytes)
known_prefix = b"THM{"

#Recover the 4-byte key by XORing the first 4 bytes of ciphertext with THM{
key = bytes([ciphertext[i] ^ known_prefix[i] for i in range(4)])
print(f"[*] Recovered key: {key}")

#Decrypt the entire ciphertext using the recovered 4-byte key
flag = bytes([ciphertext[i] ^ key[i % 4] for i in range(len(ciphertext))])
print(f"[+] Flag: {flag.decode(errors='ignore')}")


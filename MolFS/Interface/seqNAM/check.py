a = "random_file"
b = a + ".dna-decoded"
fa = open(a, "rb").readlines()
fb = open(b, "rb").readlines()
for i in range(len(fb)):
    fa_ = " ".join(str(ord(c)) for c in fa[i])
    fb_ = " ".join(str(ord(c)) for c in fb[i])
    if fa_ != fb_:
        print(fa_)
        print(fb_)

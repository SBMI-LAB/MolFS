# -*- coding: utf-8 -*-

from MolFS.Binary import *


### Test 1
PathIn = "Test/Source/"
PathOut = "Test/Destiny/"

#filein = "image.jpeg"
#filein = "text.txt"
filein = "document.docx"


## Creating Hex file
#content = binaryRead( PathIn+filein )
#binaryWriteHex(content, PathOut + filein + ".txt")


## Reading Hex file
content2 = HexRead(PathOut + filein + ".txt")
binaryWrite(content2, PathOut + filein)



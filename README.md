## The Molecular File System

The Molecular File System is inspired by electronic file system schemes such as the Linear Tape File System (LTFS), Multi-session CD-R and distributed version control systems, like GIT. Using these schemes as reference, the MolFS incorporates an Indexing system, multi-session and differential file generation.

The architecture of the MolFS provides Management modules for Session, Indexing and the Molecular device interface, and defines controllers for logical defined objects such as Folders, Files, Extents and Blocks.

**Table of Contents**

[TOCM]

### Requirements

This implementation requires Python 3.7 or newer, and PyQt5 for the Graphical User Interface - under development. 
To use the Molecular File System with a custom DNA storage scheme, it requires to have one interface (see guideline for creating a Molecular Device interface)


### Using the MolFS


```Python
# Run the code in the top-level folder
from MolFS.MolFSGen import *

fs = MolFS("dummy") 
# Calling molecular device (dummy here is the name in this example, see Molecular Device Interface how to define an interface)

fs.StartFS("LabelName")

fs. mkdir("FolderName1") 	# Create folder
fs.cd("FolderName1")			# Change folder file
fs.add(  AbsolutePathFile  )	# Add a file

fs.cd("..")			#Up folder
fs.mkdir("FolderName2")
fs.cd("FolderName2")
fs.add(AbsolutePathFile2)

fs.setUseZlib(True)		# Compresses the data blocks

fs. CloseSession()		# Generate the data blocks using the Molecular Device
```

### Graphical User Interface (Under development)

The Graphical User Interface runs using PyQt5, and shows a file manager window similar to Windows Explorer. This version is under development and is not yet functional.

### Molecular Device Interface

To use a custom DNA storage scheme (we call here Molecular Device), it requires a Python script located in the folder MolFS/Interface, with the following conditions:

- The script file must be lowercase. The name (without the extension) will be used by MolFS to determine the Molecular device. 
- Must have functions to transform a binary file to DNA sequences and viceversa
- It is recommended to incorporate a barcode that encodes the Block and Pool numbers.
- Must have a function to classify single DNA strands to determine the corresponding Block and Pool

The dummy example is under construction. 
Contact me: jeguerrero@aggies.ncat.edu for further information and/or example using an existing Molecular Device interface.







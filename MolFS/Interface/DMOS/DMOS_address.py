
import math

class DMOS_Address:
    
    def encode(self,number):
        bnumber=format(number, '#044b')[2:]
                       
        base = 16
        numbers = []
        for k in range(0,base):
            numbers.append(k)
        n=base
        Nm = number
        S= []
        perNum = ""
        for i in range(1,n+1):
            j = math.floor( Nm / math.factorial(n-i) )
            
            # Kn =  math.remainder(Nm, math.factorial (n-i))
            Kn = Nm % math.factorial (n-i)
#            print (i, j, n-i, math.factorial(n-i), Kn, Nm)
            if j > 0:
                perNum += hex(numbers[j])[2:]
                numbers.remove(numbers[j])
#                Nm =  abs(math.remainder(Nm, math.factorial (n-i)))
#                Nm =  math.remainder(Nm, math.factorial (n-i))
                Nm = Nm % math.factorial (n-i)
            else:
                perNum += hex(numbers[j])[2:]
                numbers.remove(numbers[j])
        
#        print(bnumber)        
        return perNum
    
    
    
    
    def decode(self, strAddress):
        base = 16
        
        if len(strAddress) != base:
            print("Address length error")
            return -1
        
        address = []
        for H in strAddress:
            address.append( int(H,16) )
        
        numbers = []
        for k in range(0,base):
            numbers.append(k)
        n=base
        
        Nm = 0
        
        
        
        for i in range(1,n+1):
            
            if numbers[0] == address[0]:
                numbers.remove(numbers[0])
                address.remove(address[0])
            else:
                nadd = address[0]
                ind = numbers.index(nadd)
                
                factor = math.factorial(n-i) * (ind)
                Nm += factor
                
                numbers.remove(nadd)
                address.remove(nadd)
                
        return Nm
                
                
                
            
        

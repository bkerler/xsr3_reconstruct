#!/usr/bin/env python3
import os
import sys

def main():
   filesize = os.stat("onenand.bin").st_size
   filesize_oob = os.stat("onenand.oob").st_size
   print(hex(filesize//0x200))
   print(hex(filesize_oob//0x10))
   with open("flash.bin","wb") as wf:
       with open("onenand.bin","rb") as rf:
           with open("onenand.oob","rb") as rrf:
               data=-1
               while data!=b"":
                   data=rf.read(0x200)
                   oob=rrf.read(0x10)
                   wf.write(data)
                   wf.write(oob)

   print("Done.")
main()

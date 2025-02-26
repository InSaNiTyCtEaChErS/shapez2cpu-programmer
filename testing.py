import base64
import gzip
import json

#use these specific strings. it should end up with either 254 or 255 in A after run.
# cla clx cly lda
# 127 tax cla lda
# 127 add adsout stalu 


# put your opcodes and their assembly codes here
lookup = {
    'lda': 0b00000000,  # register manipulation opcodes
    'tax': 0b00000001,
    'tay': 0b00000010,
    'cla': 0b00000011,
    'clx': 0b00000100,
    'cly': 0b00000101,
    'adsout': 0b00000110, #alu opcodes
    'stalu': 0b00000111,
    'add': 0b00001000,  
    'sub': 0b00001001,
    'and': 0b00001010,
    'or': 0b00001011,
    'xor': 0b00001100,
    'not': 0b00001101,
    'sec': 0b00001110,  #carry flag opcodes
    'clc': 0b00010001,  
    'txa': 0b00010010,  #extra register opcodes
    'tya': 0b00010011,
    'staramp0': 0b00010100,  #ram page 0
    'ldaramp0': 0b00010101,
    'bcc': 0b00010110,  #movement opcodes
    'bcs': 0b00010111,
    'jmp': 0b00011000,  
    'staramp1-255': 0b00110001,  #ram pages 1 to 255
    'ldaramp1-255':0b00110010,
         #basic operators
    'empty' :0b00000000,
    'set' :0b11111111

}

# code generator function
# a line of code looks like this
# operation arg1 arg2 output
# you may need to change accordingly, or adjust your language to be like this
def code_gen(code):
  print(type(code))

  # splitting the code into its lines
  if type(code) is str:
    lines = code.lower().split("\n")
    lines.pop()
  else:
    lines = code
  
  machine_code = []

  for i in lines:
    opcodes = []
    comment = False

    # splitting the line into its parts
    parts = i.split()

    for j in parts:
      # split at OR symbol
      s_parts = j.split("|") 

      # check if comment 
      if j == '#':
        comment = True 

      # end if is comment
      if comment:
        break

      # handling the smaller opcode parts
      s_opcode = 0
      for k in s_parts:
        # try lookup opcode, else treat as an integer arg.

        try:
          s_opcode = s_opcode | lookup[k]
        except KeyError:
          s_opcode = s_opcode | int(k)

      # add assembled opcode to assembled list 
      opcodes.append(s_opcode)

    # converting to shapes
    if len(opcodes) > 1:
      # opcodes = binary strings
      converted = [f'{i:08b}' for i in opcodes] # convert to binary bits padded to 8
      converted = converted[:4]
      encoded = []

      
        #---------# this is where your shape signal generating code goes
        # this preset sets all 0s to Ru and all 1s to Cu
      encode_lookup = {
      '000':'u',
      '001':'r',
      '010':'y',
      '011':'g',
      '100':'c',
      '101':'b',
      '110':'m',
      '111':'w'
      }

      shape = ""

      for byte in converted:

        if byte[0] == "0":
           shape += "C"
        else:
          shape += "R"
        print(f"The current shape code is <{shape}>.")

        lookupKey = byte[1:4]
        print(f"The lookup key is <{lookupKey}>.")

        shape += encode_lookup[lookupKey]
        print(f"The current shape code is now <{shape}>.")

        if byte[4] == "0":
          shape += "C"
        else:
          shape += "R"
        print(f"The current shape code is <{shape}>.")

        lookupKey = byte[5:8]
        print(f"The lookup key is <{lookupKey}>.")

        shape += encode_lookup[lookupKey]
        print(f"The current shape code is now <{shape}>.")



        #---------# this is where it ends

      out = shape[:8] + ":" + shape[8:] # convert each byte to shape code
      print(out)

      encoded.append(out)

    # add all to final list
    machine_code.append(encoded)

  return machine_code

# create shapez BP
def BPify(program):
  prefix = "SHAPEZ2-2-"
  suffix = "$"

  # get BP sample
  with open('LEG to SHAPEZ assembler/blueprint.txt', 'r') as f:
    blueprint = f.read()
    f.close()

  # decode BP sample from b64, gzip, json
  decoded = gzip.decompress(base64.b64decode(blueprint))
  obj = json.loads(decoded)

  # set instruction counters
  i = 0
  j = 0

  rechecking = []

  for building in obj["BP"]["Entries"]:
    # stop when out of bytes
    if i > len(program) - 1:
      break
    
    try:
      if building["L"] == 1:
        rechecking.append(i)
        continue
    except KeyError:
      pass
    
    # fetch data
    data = program[i][0]
    print(data)

    # make stem of `C` field
    print(hex(len(data))[2:])
    stem = b'\x06\x01\x01' + bytes.fromhex(hex(len(data))[2:]) + b"\x00"
    print(stem)
    
    # make shape signal into bytes
    signal = bytes(data, 'utf-8')
    print(signal)

    print(stem + signal)

    # set `C` field with b64 encoded data, decoded from bytes to a string
    building["C"] = base64.b64encode(stem + signal).decode('utf-8')
    print(building["C"])

    i += 1
  
  print(rechecking)

  for idx in rechecking:
    i = 0

    # stop when out of bytes
    if i > len(program) - 1:
      break

    building = obj["BP"]["Entries"][idx]
    
    # fetch data
    data = program[i][0]
    print(data)

    # make stem of `C` field
    stem = b'\x06\x01\x01' + bytes.fromhex(hex(len(data))[2:]) + b"\x00"
    print(stem)
    
    # make shape signal into bytes
    signal = bytes(data, 'utf-8')
    print(signal)

    print(stem + signal)

    # set `C` field with b64 encoded data, decoded from bytes to a string
    building["C"] = base64.b64encode(stem + signal).decode('utf-8')
    print(building["C"])

    i+=1


  print(obj)
  
  obj_bytes = json.dumps(obj).encode('utf-8')
  print(obj_bytes)

  # encode the new object
  encoded = str(base64.b64encode(gzip.compress(obj_bytes)).decode('utf-8'))
  print(encoded)

  # return BP with prefix and suffix
  return prefix + encoded + suffix

# main function
def main():
  user_text = ""
  print("Enter your code below:")
  
  # user input over multiple lines
  while True:
    new_text = input()
    if new_text == "end":
      print("")
      break
    user_text += f"{new_text}\n"

  output = code_gen(user_text)
  
  BP = BPify(output)

  with open('LEG to SHAPEZ assembler/output.txt', 'w') as f:
    f.write(BP)
    f.close()

  print("Turned into a blueprint!")


if __name__ == "__main__":
  main()
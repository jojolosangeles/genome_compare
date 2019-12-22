import sys

class NWriter:
  def __init__(self, fileName, n):
    self.fileNumber = 1
    self.fileName = fileName
    self.numberLines = n
    self.lineBuffer = []
  
  def writeFile(self):
    with open(self.fileName + "." + str(self.fileNumber), "w") as outFile:
      for line in self.lineBuffer:
        outFile.write(line)
    self.fileNumber += 1 

  def add(self, line):
    self.lineBuffer.append(line)
    if len(self.lineBuffer) == self.numberLines:
      self.writeFile()
      self.lineBuffer = []

fileName = sys.argv[1]
numberLines = 100
if len(sys.argv) > 2:
  numberLines = int(sys.argv[2])
lines = open(fileName, "r").readlines()

nw = NWriter(fileName, numberLines)
for line in lines:
  nw.add(line)
nw.writeFile()

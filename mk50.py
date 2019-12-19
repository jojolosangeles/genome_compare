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

print(sys.argv)
fileName = sys.argv[1]
lines = open(fileName, "r").readlines()
numberLines = 100

nw = NWriter(fileName, numberLines)
for line in lines:
  nw.add(line)
nw.writeFile()

"""
These are generators for processing a long sequence data source
"""
def excludeLinesStartingWith(s):
    def acceptFn(line):
        return len(line.strip()) > 0 and not line.startswith(s)

    return acceptFn

defaultLineProcessing = excludeLinesStartingWith(">")

class DataSourceFilter:
    """
    This takes in a data stream and yields a stream containing only data to be processed
    (e.g. ignoring comment lines)

    Yields (dataStartOffset, dataEndOffset, data)

    The data offsets refer to the offset in the original data stream, e.g. file seek location in source data file
    """
    def __init__(self, filePath, acceptFunction=defaultLineProcessing):
        self.filePath = filePath
        self.accept = acceptFunction

    def sequences(self):
        dataOffset = 0
        with open(self.filePath, "r") as inFile:
            for line in inFile:
                if self.accept(line):
                    stripped_line = line.strip()
                    yield((dataOffset, dataOffset + len(stripped_line), stripped_line))
                dataOffset += len(line)


class SegmentGenerator:
    """
    Takes in a stream of data sequences, and yields larger sequences of a fixed size

    Yields: (dataStartOffset, dataEndOffset, segmentStartOffset, segmentEndOffset, segmentData)

    'dataStartOffset' and 'dataEndOffset' refer to the offset in the original data stream.
    'segmentStartOffset' and 'segmentEndOffset' refer to the offset in the entire sequence of segments yielded
    """
    def __init__(self, dataSourceFilter, segmentSize):
        self.dataSourceFilter = dataSourceFilter
        self.segmentSize = segmentSize

    def segments(self):
        segmentStartOffset = 0
        segmentDataStartOffset = 0
        segmentDataEndOffset = 0
        segmentData = ""
        for sequenceStartOffset, sequenceEndOffset, data in self.dataSourceFilter.sequences():
            if segmentData == "":
                # first time, initialize segment
                segmentDataStartOffset = sequenceStartOffset
                segmentData = data
                segmentDataEndOffset = sequenceEndOffset
            else:
                # add to segment
                segmentData += data
                segmentDataEndOffset = sequenceEndOffset

            while len(segmentData) > self.segmentSize:
                remainingSegmentData = segmentData[self.segmentSize:]
                segmentData = segmentData[:self.segmentSize]
                yield (segmentDataStartOffset,
                       segmentDataEndOffset - len(remainingSegmentData),
                       segmentStartOffset,
                       segmentStartOffset + self.segmentSize,
                       segmentData)
                segmentData = remainingSegmentData
                segmentDataStartOffset = segmentDataEndOffset - len(segmentData)
                segmentDataEndOffset - len(remainingSegmentData)
                segmentStartOffset += self.segmentSize

        yield (segmentDataStartOffset, segmentDataEndOffset, segmentStartOffset, segmentStartOffset + len(segmentData), segmentData)

AT_CG_SPLIT = (('CG', 'C G'), ('GC', 'G C'), ('AT', 'A T'), ('TA', 'T A'), ('N', ''))

def wordSplitterFactory(replaceXwithY):
    def replaceFunction(line):
        for x,y in replaceXwithY:
            line = line.replace(x, y)
        return line
    return replaceFunction

def wordFilterFactory(minWordLen):
    def wordFilterFunction(line):
        data = line.split()
        data = [ word for word in data if len(word) >= minWordLen ]
        return " ".join(data)
    return wordFilterFunction

class SegmentProcessor:
    def __init__(self, segmentGenerator, dataProcessor):
        self.segmentGenerator = segmentGenerator
        self.dataProcessor = dataProcessor

    def segments(self):
        for dataStartOffset, dataEndOffset, segmentStartOffset, segmentEndOffset, segmentData in self.segmentGenerator.segments():
            segmentData = self.dataProcessor(segmentData)
            yield (dataStartOffset, dataEndOffset, segmentStartOffset, segmentEndOffset, segmentData)


if __name__ == "__main__":
    # import sys
    #
    # print("DataSourceFilter TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # for startDataOffset, endDataOffset,data in dsf.sequences():
    #     print(startDataOffset, endDataOffset, data)
    #
    # print("SegmentGenerator TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # sg = SegmentGenerator(dsf, 20)
    # for startDataOffset, endDataOffset, segmentStartOffset, segmentEndOffset, segmentData in sg.segments():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {segmentStartOffset}:{segmentEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("WordSplitter TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # sg = SegmentGenerator(dsf, 20)
    # sp = SegmentProcessor(sg, wordSplitterFactory(AT_CG_SPLIT))
    # for startDataOffset, endDataOffset, segmentStartOffset, segmentEndOffset, segmentData in sp.segments():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {segmentStartOffset}:{segmentEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("WordFilter TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # sg = SegmentGenerator(dsf, 20)
    # sp = SegmentProcessor(sg, wordSplitterFactory(AT_CG_SPLIT))
    # wf = SegmentProcessor(sp, wordFilterFactory(5))
    # for startDataOffset, endDataOffset, segmentStartOffset, segmentEndOffset, segmentData in wf.segments():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {segmentStartOffset}:{segmentEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("END OF TESTS")
    import sys

    species = sys.argv[1]
    chromosome = sys.argv[2]
    fileToProcess = sys.argv[3]
    segmentSize = int(sys.argv[4])
    minWordSize = int(sys.argv[5])

    dsf = DataSourceFilter(fileToProcess)
    sg = SegmentGenerator(dsf, segmentSize)
    sp = SegmentProcessor(sg, wordSplitterFactory(AT_CG_SPLIT))
    wf = SegmentProcessor(sp, wordFilterFactory(minWordSize))
    for startDataOffset, endDataOffset, segmentStartOffset, segmentEndOffset, segmentData in wf.segments():
        print(f"{species} {chromosome} {startDataOffset} {endDataOffset} {segmentStartOffset} {segmentEndOffset} {segmentData}")

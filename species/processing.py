import gzip

"""
These are generators for processing a long sequence data source.

The data source includes non-sequence text like comments.  The offsets provided are for both
the original source file and for the filtered data.

The final data records are for fixed size filtered segments.
Each segment record contains:

- dataSourceStartOffset, dataSourceEndOffset (dsSO, dsEO) -- where to find the data in the original source file
- filteredSequenceStartOffset, filteredSequenceEndOffset (fsSO, fsEO) -- offset in the complete filtered sequence
- filteredSequence -- the raw data sequence
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

    Yields (dataSourceStartOffset, dataSourceEndOffset, data)

    The data offsets refer to the offset in the original data stream, e.g. file seek location in source data file
    """
    def __init__(self, filePath, acceptFunction=defaultLineProcessing):
        self.filePath = filePath
        self.accept = acceptFunction

    def open_datasource(self, datasource):
        ext = datasource.split(".")[-1]
        if ext == "gz":
            return gzip.open(datasource, "rt")
        else:
            return open(datasource, "r")

    def sequences(self):
        dataOffset = 0
        with self.open_datasource(self.filePath) as inFile:
            for line in inFile:
                if self.accept(line):
                    stripped_line = line.strip()
                    yield((dataOffset, dataOffset + len(stripped_line), stripped_line))
                dataOffset += len(line)


class SegmentGenerator:
    """
    Takes in small data sequences, and yields larger sequences of a fixed size

    Yields: (dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData, orientation)

    'dataSourceStartOffset' and 'dataSourceEndOffset' refer to the offset in the original data stream.
    'filteredSequenceStartOffset' and 'filteredSequenceEndOffset' refer to the offset in the entire sequence of segments yielded
    'orientation' is always True
    """
    def __init__(self, dataSourceFilter, segmentSize):
        self.dataSourceFilter = dataSourceFilter
        self.segmentSize = segmentSize

    def segments(self):
        filteredSequenceStartOffset = 0
        segmentdataSourceStartOffset = 0
        segmentdataSourceEndOffset = 0
        segmentData = ""
        for sequenceStartOffset, sequenceEndOffset, data in self.dataSourceFilter.sequences():
            if segmentData == "":
                # first time, initialize segment
                segmentdataSourceStartOffset = sequenceStartOffset
                segmentData = data
                segmentdataSourceEndOffset = sequenceEndOffset
            else:
                # add to segment
                segmentData += data
                segmentdataSourceEndOffset = sequenceEndOffset

            while len(segmentData) > self.segmentSize:
                remainingSegmentData = segmentData[self.segmentSize:]
                segmentData = segmentData[:self.segmentSize]
                yield (segmentdataSourceStartOffset,
                       segmentdataSourceEndOffset - len(remainingSegmentData),
                       filteredSequenceStartOffset,
                       filteredSequenceStartOffset + self.segmentSize,
                       segmentData,
                       True)
                segmentData = remainingSegmentData
                segmentdataSourceStartOffset = segmentdataSourceEndOffset - len(segmentData)
                segmentdataSourceEndOffset - len(remainingSegmentData)
                filteredSequenceStartOffset += self.segmentSize

        yield (segmentdataSourceStartOffset, segmentdataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceStartOffset + len(segmentData), segmentData, True)

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
        for dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData, orientation in self.segmentGenerator.segments():
            segmentData = self.dataProcessor(segmentData)
            yield (dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData, orientation)


class SearchSampler:
    def __init__(self):
        pass

def prepare_for_es(fileToProcess, targetFile, segmentSize, wordSplitter, wordFilter):
    dsf = DataSourceFilter(fileToProcess)
    sg = SegmentGenerator(dsf, segmentSize)
    sp = SegmentProcessor(sg, wordSplitter)
    wf = SegmentProcessor(sp, wordFilter)
    for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData, orientation in wf.segments():
        targetFile.write(f"{species} {chromosome} {startDataOffset} {endDataOffset} {filteredSequenceStartOffset} {filteredSequenceEndOffset} {segmentData}\n")


class ForwardInverseSampleExtractor:
    def __init__(self, segmentGenerator, sampleSize, marginSize, numberSamples):
        self.segmentGenerator = segmentGenerator
        self.sampleSize = sampleSize
        self.marginSize = marginSize
        self.numberSamples = numberSamples

    def comp(self, val):
        if val == 'A':
            return 'T'
        elif val == 'C':
            return 'G'
        elif val == 'G':
            return 'C'
        elif val == 'T':
            return 'A'
        else:
            return val

    def revcomp(self, s):
        l = [self.comp(v) for v in reversed(s)]
        return "".join(l)

    def segments(self):
        return self.samples()

    def samples(self):
        for dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData, orientation in self.segmentGenerator.segments():
            for sample in range(numberSamples):
                sampleOffsetInSegment = (self.marginSize * (sample + 1) + self.sampleSize * sample)
                data = segmentData[sampleOffsetInSegment:(sampleOffsetInSegment + self.sampleSize)]
                yield (dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, data, True)
                revCompData = self.revcomp(data)
                yield (dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, revCompData, False)

def prepare_samples(fileToProcess, targetFile, segmentSize, wordSplitter, wordFilter, sampleSizePercent, numberSamples):
    dsf = DataSourceFilter(fileToProcess)
    sg = SegmentGenerator(dsf, segmentSize)
    singleSampleSize = int(segmentSize*sampleSizePercent/100)
    marginSize = int(int(segmentSize - singleSampleSize * numberSamples) / (numberSamples + 1))
    fig = ForwardInverseSampleExtractor(sg, singleSampleSize, marginSize, numberSamples)
    sp = SegmentProcessor(fig, wordSplitter)
    wf = SegmentProcessor(sp, wordFilter)

    for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, data, orientation in wf.segments():
        targetFile.write(f"{species} {chromosome} {startDataOffset} {endDataOffset} {filteredSequenceStartOffset} {filteredSequenceEndOffset} {orientation} {data}\n")


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
    # for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData in sg.samples():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {filteredSequenceStartOffset}:{filteredSequenceEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("WordSplitter TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # sg = SegmentGenerator(dsf, 20)
    # sp = SegmentProcessor(sg, wordSplitterFactory(AT_CG_SPLIT))
    # for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData in sp.samples():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {filteredSequenceStartOffset}:{filteredSequenceEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("WordFilter TEST")
    # dsf = DataSourceFilter(sys.argv[1])
    # sg = SegmentGenerator(dsf, 20)
    # sp = SegmentProcessor(sg, wordSplitterFactory(AT_CG_SPLIT))
    # wf = SegmentProcessor(sp, wordFilterFactory(5))
    # for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData in wf.samples():
    #     print(f"data {startDataOffset}:{endDataOffset}, segment {filteredSequenceStartOffset}:{filteredSequenceEndOffset}, data={segmentData}, len is {len(segmentData)}")
    #
    # print("END OF TESTS")
    import sys

    species = sys.argv[1]
    chromosome = sys.argv[2]
    fileToProcess = sys.argv[3]
    segmentSize = int(sys.argv[4])
    minWordSize = int(sys.argv[5])
    targetFolder = sys.argv[6]

    # get samples at same time, includes reverse complement samples
    sampleSizePercent = int(sys.argv[7])
    numberSamples = int(sys.argv[8])

    with open(f"{targetFolder}/{species}.{chromosome}.{segmentSize}.{minWordSize}.processed", "w") as targetFile:
        prepare_for_es(fileToProcess, targetFile, segmentSize, wordSplitterFactory(AT_CG_SPLIT), wordFilterFactory(minWordSize))

    with open(f"{targetFolder}/{species}.{chromosome}.{segmentSize}.{minWordSize}.samples", "w") as targetFile:
        prepare_samples(fileToProcess, targetFile, segmentSize, wordSplitterFactory(AT_CG_SPLIT), wordFilterFactory(minWordSize), sampleSizePercent, numberSamples)

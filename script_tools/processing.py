import gzip
import random

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
                       segmentData)
                segmentData = remainingSegmentData
                segmentdataSourceStartOffset = segmentdataSourceEndOffset - len(segmentData)
                segmentdataSourceEndOffset - len(remainingSegmentData)
                filteredSequenceStartOffset += self.segmentSize

        yield (segmentdataSourceStartOffset, segmentdataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceStartOffset + len(segmentData), segmentData)


AT_CG_SPLIT = {'CG': 'C G', 'GC': 'G C', 'AT': 'A T', 'TA': 'T A', 'N': ''}


def wordSplitterFactory(replaceXwithY):
    def replaceFunction(line):
        line = line.upper()
        for x,y in replaceXwithY.items():
            line = line.replace(x, y)
        return line
    return replaceFunction


COMPLEMENT = { 'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', ' ': ' ' }


def revcomp(s):
    return ''.join([COMPLEMENT[v] for v in reversed(s)])


def deleterFactory(numberSubsequences, subsequenceLength):
    """Returns a function that deletes random subsequences and their reverse complement"""
    sequencesToDelete = []
    for i in range(numberSubsequences):
        seqToDel = ''.join(random.choice("ACGT") for i in range(subsequenceLength))
        sequencesToDelete.append(seqToDel)
        sequencesToDelete.append(revcomp(seqToDel))

    def sequenceDeleterFunction(line):
        for s in sequencesToDelete:
            line = line.replace(s, '')
        return line
    return sequenceDeleterFunction


def wordFilterFactory(minWordLen):
    """Returns a function that removes words less than 'minWordLen' from a string"""
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
        for dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData in self.segmentGenerator.segments():
            segmentData = self.dataProcessor(segmentData)
            yield (dataSourceStartOffset, dataSourceEndOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData)


def prepare_for_es(fileToProcess, targetFile, segmentSize, deleter, wordSplitter, wordFilter, sampler):
    """convert each continuous sequence into a much smaller sequence of words"""
    dsf = DataSourceFilter(fileToProcess)
    sg = SegmentGenerator(dsf, segmentSize)
    d = SegmentProcessor(sg, deleter)
    sp = SegmentProcessor(d, wordSplitter)
    wf = SegmentProcessor(sp, wordFilter)
    for startDataOffset, endDataOffset, filteredSequenceStartOffset, filteredSequenceEndOffset, segmentData in wf.segments():
        location = f"{species} {chromosome} {startDataOffset} {endDataOffset} {filteredSequenceStartOffset} {filteredSequenceEndOffset}"
        targetFile.write(f"{location} {segmentData}\n")
        sampler.write_samples(location, segmentData)


class Sampler:
    def __init__(self, output_file, sample_size_percent, number_samples):
        self.output_file = output_file
        self.sample_size_percent = sample_size_percent
        self.number_samples = number_samples

    def write_samples(self, location, segment_data):
        words = segment_data.split()
        words_per_sample = int(len(words)*self.sample_size_percent/100)
        words_between = int((len(words) - words_per_sample*self.number_samples)/self.number_samples)
        left = int(words_between/2)
        for i in range(self.number_samples):
            start = left + i * (words_between + words_per_sample)
            data = ' '.join(words[start:(start + words_per_sample)])
            orientation = "same"
            self.output_file.write(f"{location} {orientation} {data}\n")
            orientation = "reversed"
            self.output_file.write(f"{location} {orientation} {revcomp(data)}\n")


# https://gist.github.com/gajeshbhat/67a3db79a6aecd1db42343190f9a2f17
def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)


if __name__ == "__main__":
    import sys

    species = sys.argv[1]
    chromosome = sys.argv[2]
    fileToProcess = sys.argv[3]
    segmentSize = convert_str_to_number(sys.argv[4])
    minWordSize = int(sys.argv[5])
    targetFolder = sys.argv[6]

    # get samples at same time, includes reverse complement samples
    sampleSizePercent = int(sys.argv[7])
    numberSamples = int(sys.argv[8])

    # number of random subsequences of given length to remove, 0 for number subsequences does nothing
    numberSubsequencesToDelete = 0
    deletedSubsequenceLength = 0
    if len(sys.argv) > 9:
        numberSubsequencesToDelete = int(sys.argv[9])
        deletedSubsequenceLength = int(sys.argv[10])

    with open(f"{targetFolder}/processed/{species}.{chromosome}.{segmentSize}.{minWordSize}.processed", "w") as targetFile, \
         open(f"{targetFolder}/samples/{species}.{chromosome}.{segmentSize}.{minWordSize}.samples", "w") as sampleFile:
        deleter = deleterFactory(numberSubsequencesToDelete, deletedSubsequenceLength)
        wordSplitter = wordSplitterFactory(AT_CG_SPLIT)
        wordFilter = wordFilterFactory(minWordSize)
        sampler = Sampler(sampleFile, sampleSizePercent, numberSamples)
        prepare_for_es(fileToProcess, targetFile, segmentSize, deleter, wordSplitter, wordFilter, sampler)


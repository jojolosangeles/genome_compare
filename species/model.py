import collections

# species, chromosome, start location, end location
SpeciesSequence = collections.namedtuple('SpeciesSequence', 'sp chr sloc eloc')

class Match:
    def __init__(self, sp1_seq, sp2_seq, orientation, score):
        self.sp1_seq = sp1_seq
        self.sp2_seq = sp2_seq
        self.orientation = orientation
        self.score = score




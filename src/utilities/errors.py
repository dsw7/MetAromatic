class Error(Exception):
    pass

class InvalidCutoffsError(Error):
    """ Raised when invalid cutoffs are provided """
    pass

class InvalidPDBFileError(Error):
    """ Raised when an invalid PDB entry code is provided """
    pass

class MissingPDBFileError(Error):
    """ Raised when the PDB file to be deleted does not exist """
    pass

class NoMetCoordinatesError(Error):
    """ Raised when no methionine coordinates exist in dataset """
    pass

class NoAromaticCoordinatesError(Error):
    """ Raised when no methionine coordinates exist in dataset """
    pass

class InvalidModelError(Error):
    """ Raised when no aromatic coordinates exist in dataset """
    pass

class NoResultsError(Error):
    """ Raised when no aromatic interactions meeting imposed criteria exist in dataset """
    pass

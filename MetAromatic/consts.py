from numpy import sin, cos, pi

# Logging
LOGRECORD_FORMAT = "%(asctime)s %(threadName)s %(levelname)s %(message)s"
ISO_8601_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Linear algebra
# See https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula "Matrix notation" section
SCAL1 = sin(pi / 2)
SCAL2 = 1 - cos(pi / 2)
ROOT_2 = 2**0.5

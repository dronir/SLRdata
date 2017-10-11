# Python package for satellite laser ranging file formats

This package contains functions to parse CPF (predicts) and CRD (ranging
observations) files in Python.

See the ILRS documentation of the file formats for their definitions and
details.

These were written for personal use, implementing mostly just features that
were necessary at the moment. No warranty or future maintenance is promised.
Feature request will be considered. Packaging for PyPI is also a possibility if
there is demand.

## Installation

Python 3 is required, as well as the packages listed in `requirements.txt`. I
recommend using a virtualenv and running:

```
$ pip install -r requirements.txt
$ python setup.py install
```

## Usage

### Consolidated Prediction Format

The CPF parser was written in order to interpolate predicts in the way
described in the CPF format specification (see
https://ilrs.cddis.eosdis.nasa.gov/data_and_products/formats/cpf.html).

It works relatively simply. The `parse_CPF` function takes in the raw contents
of a CPF file, and produces a `Prediction` object, which wraps the data and an
interpolator (a `BarycentricInterpolator` from `scipy` is used).

Calling the `interpolate(t)` method, where `t` is a `datetime` object returns
the interpolated position as a `numpy` array. A `ValueError` will be raised if
the `t` is outside the valid interpolation range of the prediction file.

#### Example

```python
>>> from SLRdata import parse_CPF
>>> from datetime import datetime

>>> raw_data = open("todays_predict_file.cpf", "r").read()
>>> my_predict = parse_CPF(raw_data)

>>> timestamp = datetime.utcnow()
>>> my_predict.interpolate(timestamp)
array([  712048.91907249,  5057248.90826335, -5784879.0715739 ])
```

### Consolidated Ranging Data

The CRD format is more complex and parsed in a much more complicated way. 

1. The parser returns collection of dictionaries representing observation 
    "units" (defined by the H1 header lines, ended by the H9 header). 
2. A unit dictionary has a list of "sessions", defined by H4 headers, ended by 
    the H9 header.
3. Each session is a dictioanry containing session parameters and a numpy
    array with the observed data.

Currently only the bare minimum of ranging data is parsed: the timestamp
(second of day) and the observed delay. More values are added as needed.

Station and target data are also parsed into dictionaries, accessed with the
`"station"` and `"target"` keywords. The CRD specification allows target and
station data both at the unit level (after a H1 headers, but before a H4
header), or for each separate session (after a H4 header). This flexibility
leads to a complication: the parser puts the `"station"` and `"target"`
keywords either in the unit dictionary or the session dictionary, depending on
where they are defined in the file. It is up to the user to make sure these
are found correctly (see example below).

#### Examples

```python
>>> from SLRdata import parse_CRD

>>> raw_data = open("ranging_file.crd", "r").read()
>>> Units = parse_CRD(raw_data)

>>> unit = Units[0]

>>> unit.keys()
dict_keys(['format', 'version', 'time', 'sessions', 'station', 'target'])

>>> unit["station"]
{'name': 'BORL', 'ID': 7811, 'system': 38, 'occupancy': 2, 'timescale': 7}

>>> unit["sessions"][0]["data"]
array([[  6.56007011e+04,   1.42107683e-02],
       [  6.56021011e+04,   1.41864711e-02],
       [  6.56028011e+04,   1.41743928e-02],
       ..., 
       [  6.58627011e+04,   1.37161761e-02],
       [  6.58628011e+04,   1.37175978e-02],
       [  6.58630011e+04,   1.37204455e-02]])
```

Here's how to get the station of a session, while falling back to the unit
level if it is not found. The Python dictionaries' `get` method defaults to its
second parameter if the requested key is not found in the dictionary:

```python
>>> session = unit["sessions"][0]

>>> session["station"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'station'

>>> session.get("station", unit["station"])
{'name': 'BORL', 'ID': 7811, 'system': 38, 'occupancy': 2, 'timescale': 7}
```


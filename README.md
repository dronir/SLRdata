
# Python package for satellite laser ranging file formats

This package contains functions to parse CPF (predicts) and CDF (observations) files in Python.

See the ILRS documentation of the file formats for their definitions and details.

These were written for personal use, implementing mostly just features that were necessary
at the moment. No warranty or future maintenance is promised. Feature request
will be considered. Packaging for PyPI is also a possibility if there is demand.

## Usage

### Consolidated Prediction Format

The CPF parser was written in order to interpolate predicts in the way described
in the CPF format specification 
(see https://ilrs.cddis.eosdis.nasa.gov/data_and_products/formats/cpf.html).

It works relatively simply. The `parse_CPF` function takes in the raw contents
of a CPF file, and produces a `Prediction` object, which wraps the data
and an interpolator (a `BarycentricInterpolator` from `scipy` is used).

Calling the `interpolate(t)` method, where `t` is a `datetime` object returns
the interpolated position as a `numpy` array. A `ValueError` will be raised
if the `t` is outside the valid interpolation range of the prediction file.

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


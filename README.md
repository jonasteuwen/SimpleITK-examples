SimpleITK examples in Python
============================

In this repository you will find a couple of examples on how to use SimpleITK with Python. If you want any specific example, please open an issue.
An open source viewer (and more) for medical images is [Slicer 3D](http://slicer.org).


Current:
 - *dcm_to_nrrd.py*: reads a complete dicom series from a folder and converts this to a nrrd file. Reads the window and level tags, and crops the image to this.
 - *resample_isotropically.py*: An example to read in a image file, and resample the image to a new grid.
 - *resample_tests.py*: Several ways to downsample an image.
 - *apply_lut.py*: in some DICOM files there is a tag VOILUTFunction. This is an example on how to apply this.
 
TODO
----
 - Juypter notebooks
 - More examples

# encoding: utf-8
"""Some dicom images require a VOILUTFunction to be applied before display.
This example script reads in the image, apply the function and writes out
back to dicom.

Reads:
- http://dicom.nema.org/MEDICAL/dicom/2014c/output/chtml/part03/sect_C.11.2.html
- http://dicom.nema.org/medical/dicom/2014c/output/chtml/part03/sect_C.7.6.3.html#sect_C.7.6.3.1.2
"""
import dicom
import numpy as np
import SimpleITK as sitk


def display_metadata(dcm_file, expl):
    """Reads a dicom file, and  takes an explanation variable

    Parameters
    ----------
    dcm_file : str
      path to dicom file
    expl : str
      name of corresponding Window Center Width Explanation.

    Returns
    -------
    center, width, VOILUTFunction, total_bits
    """
    dcm = dicom.read_file(dcm_file)
    explanation = dcm.WindowCenterWidthExplanation
    idx = explanation.index(expl)
    center = dcm.WindowCenter[idx]
    width = dcm.WindowWidth[idx]

    if hasattr(dcm, 'VOILUTFunction'):
        lut_func = dcm.VOILUTFunction.strip()
    else:
        lut_func = ''

    if dcm.SamplesPerPixel == 1:
        if dcm.PhotometricInterpretation == 'MONOCHROME1':
            raise NotImplementedError('The image needs to be inverted. Not implemented.')

    return center, width, lut_func, dcm.BitsStored


def apply_window_level(dcm_file):
    image = sitk.ReadImage(dcm_file)
    center, width, lut_func, bits_stored = display_metadata(dcm_file, 'SOFTER')

    if lut_func == 'SIGMOID':
        print('Applying `SIGMOID`.')
        image = sigmoid_lut(image, bits_stored, center, width)
    elif lut_func == '':
        print('Applying `LINEAR`.')
        image = linear_lut(image, bits_stored, center, width)
    else:
        raise NotImplementedError('`VOILUTFunction` can only be `SIGMOID`, `LINEAR` or empty.')

    return image


def sigmoid_lut(image, out_bits, center, width):
    """If VOILUTFunction in the dicom header is equal to SIGMOID,
    apply this function for visualisation.
    """
    array = sitk.GetArrayFromImage(image).astype(np.float)
    array = np.round((2**out_bits - 1)/(1 + np.exp(-4*(array - center)/width))).astype(np.int)
    ret_image = sitk.GetImageFromArray(array)
    ret_image.SetSpacing(image.GetSpacing())
    ret_image.SetOrigin(image.GetOrigin())
    ret_image.SetDirection(image.GetDirection())

    return ret_image


def linear_lut(image, out_bits, center, width):
    """If VOILUTFunction in the dicom header is equal to LINEAR_EXACT,
    apply this function for visualisation.
    """
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    min_max = sitk.MinimumMaximumImageFilter()
    min_max.Execute(image)

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound,
                                    min_max.GetMinimum(),
                                    min_max.GetMaximum())

    return image


def normalize_dicom(dcm_file, dcm_out):
    image = apply_window_level(dcm_file)
    sitk.WriteImage(image, dcm_out)

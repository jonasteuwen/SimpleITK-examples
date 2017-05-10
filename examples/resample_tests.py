# encoding: utf-8
"""In this example we generate a couple of different ways to downsample
a medical image.

1) Crop to window and level, with rescaling to uint8.
2) Crop to window and level.
3) Resample linearly without filter.
4) Resample with Gaussian filter, and then linearly.
5) Resample to a integer multiplier.

1) and 2) are meant to compare if the noise and level of detail in
the image gets destroyed because of the quantization of the intensity values.
whereas 3,4 and 5) are meant to compare the different resampling modes.

The images in this example have a spacing of (0.085, 0.085, 1.0).

Reads:
- http://dicom.nema.org/MEDICAL/dicom/2014c/output/chtml/part03/sect_C.11.2.html
"""
import SimpleITK as sitk
import os
from glob import glob
import dicom
from dicom import read_dicom_series
from resample_isotropically import resample_sitk_image

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def resample_type1(image_folder):
    image = read_dicom_series(image_folder)
    dcm_file = glob(os.path.join(image_folder, '*.dcm'))[0]
    dcm = dicom.read_file(dcm_file)
    assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
        'Needs window and level for this resampling.'
    center = dcm.WindowCenter
    width = dcm.WindowWidth
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    min_max = sitk.MinimumMaximumImageFilter()
    min_max.Execute(image)

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound,
                                    min_max.GetMinimum(),
                                    min_max.GetMaximum())

    writer = sitk.ImageFileWriter()
    writer.SetFileName('im_resampled_window_level_uint8.nrrd')
    writer.Execute(image)


def resample_type2(image_folder):
    image = read_dicom_series(image_folder)
    dcm_file = glob(os.path.join(image_folder, '*.dcm'))[0]
    dcm = dicom.read_file(dcm_file)
    assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
        'Needs window and level for this resampling.'
    center = dcm.WindowCenter
    width = dcm.WindowWidth
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound, 0, 255)
    image = sitk.Cast(image, sitk.sitkUInt8)

    writer = sitk.ImageFileWriter()
    writer.SetFileName('im_resampled_window_level_full_range.nrrd')
    writer.Execute(image)


def resample_type3(image_folder):
    image = read_dicom_series(image_folder)
    dcm_file = glob(os.path.join(image_folder, '*.dcm'))[0]
    dcm = dicom.read_file(dcm_file)
    assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
        'Needs window and level for this resampling.'
    center = dcm.WindowCenter
    width = dcm.WindowWidth
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound, 0, 255)

    image = sitk.Cast(image, sitk.sitkUInt8)
    resampled_image = resample_sitk_image(
            image, spacing=(0.2, 0.2, 1),
            interpolator='linear', fill_value=0
        )
    sitk.WriteImage(resampled_image, 'im_resampled_linear.nrrd')


def resample_type4(image_folder, sigma):
    """Apply a Gaussian filter before downsampling.
    By the Nyquist-Shannon theorem we can only reliably reproduce
    information up to the Nyquist frequency. As this frequency
    is scaled by the same factor as the downsampling, we cannot have
    frequencies above alpha*Nyquist frequence in the image.
    We use a Gaussian filter as a low-pass filter.

    As the Gaussian is the same in the frequency domain,
    we can reduce the amount of information in a 85um grid,
    to one of 200um.
    Approximately, sigma = 85/200 *1/(2*sqrt(pi)), where the normalization
    is from the choice of Gaussian. Hence sigma ~ 0.11, or ~1.412 image units.
    """
    image = read_dicom_series(image_folder)
    # 0,1,2 <-> (x,y,z)
    image = sitk.RecursiveGaussian(image, sigma=sigma*0.2, direction=0)
    image = sitk.RecursiveGaussian(image, sigma=sigma*0.2, direction=1)

    dcm_file = glob(os.path.join(image_folder, '*.dcm'))[0]
    dcm = dicom.read_file(dcm_file)
    assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
        'Needs window and level for this resampling.'
    center = dcm.WindowCenter
    width = dcm.WindowWidth
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound, 0, 255)
    image = sitk.Cast(image, sitk.sitkUInt8)

    resampled_image = resample_sitk_image(
            image, spacing=(0.2, 0.2, 1),
            interpolator='linear', fill_value=0)
    sitk.WriteImage(resampled_image, 'im_resampled_gaussian_sigma_{}.nrrd'.format(sigma))


def resample_type5(image_folder):
    image = read_dicom_series(image_folder)
    dcm_file = glob(os.path.join(image_folder, '*.dcm'))[0]
    dcm = dicom.read_file(dcm_file)
    assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
        'Needs window and level for this resampling.'
    center = dcm.WindowCenter
    width = dcm.WindowWidth
    lower_bound = center - (width - 1)/2
    upper_bound = center + (width - 1)/2

    image = sitk.IntensityWindowing(image,
                                    lower_bound, upper_bound, 0, 255)
    image = sitk.Cast(image, sitk.sitkUInt8)
    resampled_image = resample_sitk_image(
            image, spacing=(0.255, 0.255, 1),  # 0.085*3
            interpolator='linear', fill_value=0)
    sitk.WriteImage(resampled_image, 'im_resampled_integer_multiple.nrrd')


if __name__ == '__main__':
    dcm_folder = 'path_to_folder'
    resample_type1(dcm_folder)
    resample_type2(dcm_folder)
    resample_type3(dcm_folder)
    resample_type4(dcm_folder, 0.1)
    resample_type4(dcm_folder, 0.2)
    resample_type4(dcm_folder, 0.5)
    resample_type4(dcm_folder, 0.9)
    resample_type4(dcm_folder, 1)
    resample_type5(dcm_folder)

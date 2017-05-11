# encoding: utf-8
import SimpleITK as sitk
import logging
import dicom

logger = logging.getLogger(__name__)

def read_dicom_series(folder):
    """Read a folder with DICOM files and outputs a SimpleITK image.
    Assumes that there is only one DICOM series in the folder.

    Parameters
    ----------
    folder : string
      Full path to folder with dicom files.

    Returns
    -------
    SimpleITK image.
    """
    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(folder.encode('ascii'))

    assert len(series_ids) == 1, 'Assuming only one series per folder.'

    filenames = reader.GetGDCMSeriesFileNames(folder, series_ids[0],
                                              False,  # useSeriesDetails
                                              False,  # recursive
                                              True)  # load sequences
    reader.SetFileNames(filenames)
    image = reader.Execute()

    logger.info('Read DICOM series from {} ({} files).\nSize: {}\n'
                'Spacing: {}'.format(folder, len(filenames),
                                     image.GetSize(), image.GetSpacing()))

    return image

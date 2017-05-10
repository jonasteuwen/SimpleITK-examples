# encoding: utf-8
import SimpleITK as sitk
import dicom
from tqdm import tqdm


def dcm_to_nrrd(folder, to_path, intensity_windowing=True, compression=False):
    """Read a folder with DICOM files and convert to a nrrd file.
    Assumes that there is only one DICOM series in the folder.

    Parameters
    ----------
    folder : string
      Full path to folder with dicom files.
    to_path : string
      Full path to output file (with .nrrd extension). As the file is
      outputted through SimpleITK, any supported format can be selected.
    intensity_windowing: bool
      If True, the dicom tags 'WindowCenter' and 'WindowWidth' are used
      to clip the image, and the resulting image will be rescaled to [0,255]
      and cast as uint8.
    compression : bool
      If True, the output will be compressed.
    """
    reader = sitk.ImageSeriesReader()
    series_ids = reader.GetGDCMSeriesIDs(folder)

    assert len(series_ids) == 1, 'Assuming only one series per folder.'

    filenames = reader.GetGDCMSeriesFileNames(folder, series_ids[0])
    reader.SetFileNames(filenames)
    image = reader.Execute()

    if intensity_windowing:
        dcm = dicom.read_file(filenames[0])
        assert hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'),\
            'when `intensity_windowing=True`, dicom needs to have the `WindowCenter` and `WindowWidth` tags.'
        center = dcm.WindowCenter
        width = dcm.WindowWidth

        lower_bound = center - (width - 1)/2
        upper_bound = center + (width - 1)/2

        image = sitk.IntensityWindowing(image,
                                        lower_bound, upper_bound, 0, 255)
        image = sitk.Cast(image, sitk.sitkUInt8)  #  after intensity windowing, not necessarily uint8.

    writer = sitk.ImageFileWriter()
    if compression:
        writer.UseCompressionOn()

    writer.SetFileName(to_path)
    writer.Execute(image)


def main():
    folders = ['/data/folder1/', '/data/folder2']
    for folder in tqdm(folders):
        dcm_to_nrrd(folder, '~', intensity_windowing=True)

if __name__ == '__main__':
    main()

import os
import re
import sys

from docx import opendocx, getdocumenttext
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter
from unidecode import unidecode

###############################################################################
# Functions for converting various format files to .txt
###############################################################################
def file_to_txt(file_path, dst_dir, ret_fname=False):
    """
    Takes a file path and writes the file in txt format to dst_dir.
    If file is already .txt, then simply copies the file.

    Parameters
    ----------
    file_path : string
        file for processing
    dst_dir : string
        destination directory
    ret_fname : bool
        if True will return file_name for successfully processed files.

    Notes
    -----
    Currently only support pdf, txt, rtf, doc and docx.

    """
    try:
        file_path = _filepath_clean_copy(file_path)
    except IOError:
        sys.stdout.write('unable to clean file_name %s \n'%file_path)
    file_name = os.path.split(file_path)[1]
    name, ext = os.path.splitext(file_name)
    ext = re.sub(r'\.', '', ext)
    try:
        out = eval('_%s_to_txt'%ext)(file_path, dst_dir) #calls one of the _to_txt()
        if out: sys.stdout.write('unable to process file %s'%file_path)
        if ret_fname: return file_name
    except NameError:
        sys.stdout.write('file type %s not supported, skipping %s \n'%(ext,
            file_name))
        pass

def _filepath_clean_copy(file_path):
    """
    creates a copy of the file with chars which need to be escaped
    replaced with a '_';

    Returns
    -------
    file_name : str
        clean file name

    """
    dir_name, file_name = os.path.split(file_path)
    name, ext = os.path.splitext(file_name)
    if re.search(r'[,\s|:\'\.]', name):
        clean_name = re.sub(r'[,\s|:\'\.]', '_', name)
        clean_file_name = clean_name + ext
        clean_file_path = os.path.join(dir_name, clean_file_name)
        shutil.copyfile(file_path, clean_file_path)
    else:
        clean_file_path = file_path
    return clean_file_path

def _txt_to_txt(file_path, dst_dir):
    """
    Simply copies the file to the target dir.
    """
    file_name = os.path.split(file_path)[1]
    file_dst = os.path.join(dst_dir, file_name)
    return subprocess.call(['cp', file_path, file_dst])


def _pdf_to_txt(file_path, dst_dir):
    """
    Uses the pdftotxt unix util, with --layout option, to convert file_name
    to .txt and save in dst_dir

    Notes
    -----
    Download and install Xpdf from http://www.foolabs.com/xpdf/download.html
    Follow the instruciton in INSTALL - should work on most *nix systems.
    """
    file_name = os.path.split(file_path)[1]
    file_dst = os.path.join(dst_dir, re.sub(r'\.pdf$', '.txt', file_name))
    with open(file_dst, 'w') as f:
        return subprocess.call(["pdftotext",  "-layout", file_path], stdout=f)


def _doc_to_txt(file_path, dst_dir):
    """
    Uses catdoc unix util to convert file_name
    to .txt and save in dst_dir.

    Notes
    -----
    To install catdoc:
        apt-get catdoc on unix/linux
        brew install on mac
    """
    file_name = os.path.split(file_path)[1]
    file_dst = os.path.join(dst_dir, re.sub(r'\.doc$', '.txt', file_name))
    with open(file_dst, 'w') as f:
        return subprocess.call(["catdoc",  "-w", file_path], stdout=f)


def _docx_to_txt(file_path, dst_dir):
    """
    Uses the docx python module to extract text from a docx file and save
    to .txt in dst_dir.
    """
    file_name = os.path.split(file_path)[1]
    file_dst = os.path.join(dst_dir, re.sub(r'\.docx$', '.txt', file_name))
    doc = opendocx(file_path)
    txt = '\n'.join(getdocumenttext(doc))
    txt = unidecode(txt)
    with open(file_dst, 'w') as f:
        f.write(txt)
    return 0

def _rtf_to_txt(file_path, dst_dir):
    """
    Uses the pyth python module to extract text from a rtf file and save
    to .txt in dst_dir.
    """
    file_name = os.path.split(file_path)[1]
    file_dst = os.path.join(dst_dir, re.sub(r'\.rtf$', '.txt', file_name))
    doc = Rtf15Reader.read(open(file_path))
    txt = PlaintextWriter.write(doc).getvalue()
    txt = unidecode(txt)
    with open(file_dst, 'w') as f:
        f.write(txt)
    return 0


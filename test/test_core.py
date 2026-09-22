
from organizer.core import get_category
def test_sanity():
    assert 1+1 == 2

def test_get_category_image():
    assert get_category("photo.jpg") == "Images"

def test_get_category_document():
    # a .pdf should return "Documents"
    assert get_category("file.pdf") == "Documents"

def test_get_category_unknown():
    # an extension not in CATEGORIES, like .xyz, should return "Others"
    assert get_category("file.xyz") == "Others"

def test_get_category_uppercase():
    # "PHOTO.JPG" should still return "Images" — .lower() should handle this
    assert get_category("PHOTO.JPG") == "Images"

from organizer.core import get_category, clean_filename

def test_clean_filename_basic():
    assert clean_filename("final_report FINAL (2).docx") == "Final_Report_Final_2.docx"

def test_clean_filename_preserves_extension_case():
    assert clean_filename("final_report FINAL (2).DOCX") == "Final_Report_Final_2.DOCX"

from organizer.core import unique_path

def test_unique_path_no_collision(tmp_path):
    destination = tmp_path / "report.pdf"
    assert unique_path(destination) == destination

def test_unique_path_with_collision(tmp_path):
    destination = tmp_path / "report.pdf"
    destination.touch()

    result = unique_path(destination)
    assert result == tmp_path / "report_1.pdf"
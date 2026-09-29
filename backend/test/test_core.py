from organizer.core import get_category

TEST_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png"],
    "Documents": [".pdf", ".docx"],
}

def test_get_category_multi_part_extension():
    categories = {"Archives": [".zip", ".tar.gz"]}
    assert get_category("backup.tar.gz", categories) == "Archives"

def test_get_category_plain_gz_does_not_match_tar_gz():
    categories = {"Archives": [".tar.gz"]}
    assert get_category("notes.gz", categories) == "Others"

def test_get_category_longest_extension_wins():
    categories = {"Compressed": [".gz"], "Archives": [".tar.gz"]}
    assert get_category("backup.tar.gz", categories) == "Archives"

def test_sanity():
    assert 1+1 == 2

def test_get_category_image():
    assert get_category("photo.jpg", TEST_CATEGORIES ) == "Images"

def test_get_category_document():
    assert get_category("file.pdf", TEST_CATEGORIES) == "Documents"

def test_get_category_unknown():
    assert get_category("file.xyz", TEST_CATEGORIES) == "Others"

def test_get_category_uppercase():
    assert get_category("PHOTO.JPG", TEST_CATEGORIES) == "Images"


from organizer.core import get_category, clean_filename, organize_file

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

def test_organize_file_moves_and_categorizes(tmp_path):
    source_file = tmp_path / "photo.jpg"
    source_file.touch()

    destination_root = tmp_path / "organized"

    organize_file(source_file, destination_root, TEST_CATEGORIES)
    
    assert (destination_root / "Images" / "Photo.jpg").exists()
    assert not source_file.exists()
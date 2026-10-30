from organizer.demo import main, run_demo


def test_demo_sorts_sample_files(tmp_path):
    run_demo(tmp_path)

    organized = tmp_path / "Organized"
    downloads = tmp_path / "Downloads"
    assert (organized / "Documents" / "Final_Report_Final_2.docx").exists()
    assert (organized / "Images" / "Img_2041.PNG").exists()
    assert (organized / "Archives" / "Backup.Tar.gz").exists()
    assert (organized / "Others" / "Notes.xyz").exists()
    # Two files with the same cleaned name: the second gets a number.
    assert (organized / "Documents" / "Invoice.pdf").exists()
    assert (organized / "Documents" / "Invoice_1.pdf").exists()
    # Still downloading, so it stays where it is.
    assert (downloads / "Movie.mp4.crdownload").exists()


def test_demo_keeps_file_contents(tmp_path):
    run_demo(tmp_path)

    assert (tmp_path / "Organized" / "Images" / "Img_2041.PNG").read_text() == (
        "sample content of IMG 2041.PNG"
    )


def test_demo_prints_before_and_after(tmp_path, capsys):
    main([str(tmp_path / "demo")])

    output = capsys.readouterr().out
    assert "Before" in output
    assert "After" in output
    assert "IMG 2041.PNG" in output
    assert "Img_2041.PNG" in output
    assert str(tmp_path / "demo") in output


def test_demo_refuses_a_folder_that_is_not_empty(tmp_path, capsys):
    (tmp_path / "important.txt").write_text("keep me")

    try:
        main([str(tmp_path)])
    except SystemExit as exit_info:
        assert exit_info.code == 1
    else:
        raise AssertionError("demo should refuse a folder that is not empty")

    assert "not empty" in capsys.readouterr().err
    assert (tmp_path / "important.txt").read_text() == "keep me"

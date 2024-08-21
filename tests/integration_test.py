from orbiter.__main__ import run


def test_integration():
    run("just docker-build-binary", shell=True, capture_output=True, text=True)

    output = run("just docker-run-binary", shell=True, capture_output=True, text=True)
    assert "Available Origins" in output.stdout
    assert (
        "Adding local .pyz files ['/data/astronomer_orbiter_translations.pyz'] to sys.path"
        in output.stdout
    )
    assert "Finding files with extension=xml in /data/workflow" in output.stdout

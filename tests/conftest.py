"""
Fixtures for ansible-sign tests
"""

import gnupg
import os
import pytest
import shutil


@pytest.fixture
def gpg_home_with_secret_key(tmp_path):
    """
    Creates a GPG home (in a temporary directory) and generates a private key
    inside of that GPG home.

    Returns the path to the GPG home.
    """
    gpg = gnupg.GPG(gnupghome=tmp_path)
    key_params = gpg.gen_key_input(
        key_length=2048,
        name_real="TEMPORARY ansible-sign TEST key",
        name_comment="Generated by ansible-sign test fixture",
        name_email="foo@example.com",
        passphrase="doYouEvenPassphrase",
    )
    gpg.gen_key(key_params)
    yield tmp_path


@pytest.fixture
def unsigned_project_with_checksum_manifest(tmp_path):
    """
    Creates a project directory (at a temporary location) with a generated, but
    unsigned, checksum manifest, ready for signing.

    Uses the 'manifest-success' checksum fixture directory as its base.
    """

    shutil.copytree(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "checksum",
            "manifest-success",
        ),
        tmp_path,
        dirs_exist_ok=True,
    )
    yield tmp_path

"""
This module handles GPG signature verification and generation for Ansible
content. It makes use of python-gnupg (which ultimately shells out to GPG).

The primary supported method of signing content is with a detached signature,
but this module should work with inline signatures as well.
"""

import argparse
import gnupg
import os
import sys
import tempfile

from ansible_signatory import __version__
from ansible_signatory.signing.base import SignatureVerifier, SignatureVerificationResult

__author__ = "Rick Elrod"
__copyright__ = "(c) 2022 Red Hat, Inc."
__license__ = "MIT"


class GPGVerifier(SignatureVerifier):
    def __init__(self, pubkey, manifest_path=None, detached_signature_path=None):
        super(GPGVerifier, self).__init__()

        if pubkey is None:
            raise RuntimeError("pubkey must not be None")
        self.pubkey = pubkey

        if manifest_path is None:
            raise RuntimeError("manifest_path must not be None")

        self.manifest_path = manifest_path
        self.detached_signature_path = detached_signature_path

    def verify(self) -> SignatureVerificationResult:
        detached_mode = False
        if self.detached_signature_path is not None:
            if not os.path.exists(self.detached_signature_path):
                return SignatureVerificationResult(
                    success=False,
                    summary="The specified detached signature path does not exist.",
                )
            detached_mode = True

        extra = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            gpg = gnupg.GPG(gnupghome=tmpdir)
            import_result = gpg.import_keys(self.pubkey)
            extra["gpg_pubkeys_imported"] = import_result.count
            extra["gpg_fingerprints"] = import_result.fingerprints

            if detached_mode:
                with open(self.detached_signature_path, "rb") as sig:
                    verified = gpg.verify_file(sig, self.manifest_path)
            # else:
            # TODO: what is the python-gnupg call for inline sig?
            # verified =

            if not verified:
                extra["stderr"] = verified.stderr
                return SignatureVerificationResult(
                    success=False,
                    summary="Signature verification of checksum file failed.",
                    extra_information=extra,
                )

            extra["stderr"] = verified.stderr
            extra["fingerprint"] = verified.fingerprint
            extra["creation_date"] = verified.creation_date
            extra["status"] = verified.status
            extra["timestamp"] = verified.timestamp

            return SignatureVerificationResult(
                success=True,
                summary="Verification of checksum file succeeded.",
                extra_information=extra,
            )
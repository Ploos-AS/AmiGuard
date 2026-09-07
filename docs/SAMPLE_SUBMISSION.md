# AmiGuard community malware sample submissions

AmiGuard is building an independent open-source antivirus engine for classic Amiga systems, including AmigaOS / Kickstart 1.2+ and Motorola 68000.

## Submission status

**Submission channel coming shortly.**

Do **not** attach suspected malware to GitHub issues, pull requests, discussions, or commits.

## Why samples are needed

AmiGuard does not consider a named malware detection verified without sample-backed evidence. A real detection must pass provenance review, static analysis, clean-corpus regression, explicit signature lifecycle gates, and native Amiga runtime qualification before the scanner may legitimately return `INFECTED` for that family.

Historic antivirus collections are often not redistributed to new projects, and AmiGuard deliberately does not depend on `xvs.library` as its detection engine. Authentic historical samples are therefore important for independent verification.

## Material of interest

We are interested in original or historically preserved examples of:

- bootblock viruses;
- file and link viruses;
- trojans;
- infected Amiga HUNK executables or libraries;
- infected ADFs or other disk images;
- old private antivirus/research collections;
- recovered media or BBS-era archives with credible provenance.

Please preserve original artifacts unchanged. Do not execute suspected malware solely to identify it for AmiGuard.

Useful accompanying information includes SHA-256, original filename, approximate date, source/provenance, known or suspected malware name, previous antivirus verdicts, and historical notes.

## Research handling

The intended workflow is:

`isolated intake → SHA-256/provenance → neutral static analysis → human review → candidate signature/verifier → trusted clean-corpus regression → visible native Amiga runtime qualification → verified detection`

Receipt of a sample does not itself establish that the artifact is malware. Research states remain neutral until verified.

Samples will not automatically be committed to the public repository. Public metadata may be sanitized to avoid personal paths or unnecessary identifying information.

## EICAR

EICAR is used only as a harmless antivirus interoperability safe-test. It is not Amiga malware and is not a real-malware detection claim.

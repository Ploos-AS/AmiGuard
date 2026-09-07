# AmiGuard community malware sample submissions

AmiGuard is building an independent open-source antivirus engine for classic Amiga systems, including AmigaOS / Kickstart 1.2+ and Motorola 68000.

## Submission status

**Public sample submission is live at https://amiguard.ploos.no/.**

Use that service to submit suspected Amiga malware for defensive research. Do **not** attach suspected malware to GitHub issues, pull requests, discussions, or commits.

The public intake service is intentionally write-only:

- one sample file per submission;
- explicit consent is required;
- maximum sample size is 16 MiB;
- the service assigns a random submission ID;
- SHA-256, size, receipt time, and consent state are recorded;
- the original client filename is not retained;
- no public sample retrieval or download endpoint exists;
- intake does not execute, extract, or publicly serve submitted samples.

After a successful browser submission, keep the receipt's submission ID and SHA-256 if you need to refer to the sample later.

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

Useful accompanying information includes SHA-256, original filename, approximate date, source/provenance, known or suspected malware name, previous antivirus verdicts, and historical notes. Because the public service intentionally does not retain the client filename or additional free-form provenance fields, keep those notes separately for later reference with the submission ID when needed.

## Privacy and retention

Only submit material you are authorized to provide for defensive malware research. Do not submit personal documents, credentials, private communications, or unrelated data.

Unclassified submissions are normally retained for up to 90 days. Material selected as research evidence may be retained longer when needed for AmiGuard development. Samples are kept in dedicated quarantine storage and are not automatically committed to the public repository.

## Research handling

The workflow is:

`isolated intake → SHA-256/provenance → neutral static analysis → human review → candidate signature/verifier → trusted clean-corpus regression → visible native Amiga runtime qualification → verified detection`

Receipt of a sample does not itself establish that the artifact is malware. Research states remain neutral until verified.

Public metadata may be sanitized to avoid personal paths or unnecessary identifying information.

## EICAR

EICAR is used only as a harmless antivirus interoperability safe-test. It is not Amiga malware and is not a real-malware detection claim.

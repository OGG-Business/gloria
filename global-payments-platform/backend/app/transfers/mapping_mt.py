def mt103_from_pacs008(pacs_xml: str) -> str:
    # Minimal illustrative mapping; real mapping requires full schema knowledge
    return f"{'{'}1:F01BANKBEBBAXXX0000000000{'}'}{'{'}2:O1031200BANKBEBBAXXX00000000001200000000{'}'}{'{'}32A:200101USD100,00{'}'}{'{'}50K:/DEBTORIBAN\nDEBTOR NAME{'}'}{'{'}59:/CREDITORIBAN\nCREDITOR NAME{'}'}{'{'}70:REFERENCE{'}'}{'{'}71A:OUR{'}'}"
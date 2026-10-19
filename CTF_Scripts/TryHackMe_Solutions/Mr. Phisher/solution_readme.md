
Challenge Overview

• Room Name: Mr. Phisher
• Difficulty: Easy
• Objective: Analyze a malicious Microsoft Word Document Macro-Enabled file (.docm) to extract a hidden flag.

Analysis Steps


1. Initial File Inspection

The challenge provides a file named MrPhisher.docm. Because modern Microsoft Office files are essentially zipped archives containing XML configurations and media assets, the structure can be listed natively using the unzip tool:
bash
unzip -l MrPhisher.docm
Use code with caution.
The output reveals a specific binary file embedded within the document structure:
word/vbaProject.bin
This file serves as the OLE storage container where Microsoft Word embeds Visual Basic for Applications (VBA) macro scripts.

2. Extracting the Macro Script

Since static text tools like strings break up text strings when reading packed OLE structures, the document was inspected using the built-in LibreOffice Macro Editor to guarantee uncorrupted text retrieval:
1. Open MrPhisher.docm in LibreOffice Writer and select Disable Macros at the prompt.
2. Navigate to Tools > Macros > Edit Macros.
3. Expand MrPhisher.docm > Project > Modules and select NewMacros.
The editor exposes the primary function:
vba
Rem Attribute VBA_ModuleType=VBAModule
Option VBASupport 1
Sub Format()
Dim a()
Dim b As String
a = Array(102, 109, 99, 100, 127, 100, 53, 62, 105, 57, 61, 106, 62, 62, 55, 110, 113, 114, 118, 39, 36, 118, 47, 35, 32, 125, 34, 46, 46, 124, 43, 124, 25, 71, 26, 71, 21, 88)
For i = 0 To UBound(a)
b = b & Chr(a(i) Xor i)
Next
End Sub
Use code with caution.

3. Deobfuscating the Payload

The macro routine uses an array obfuscation technique. It loops through an array of numbers, applies a bitwise XOR operation using the current loop index counter i, and joins the transformed outputs back into character values (Chr).
This logic can be replicated safely in Python using a list structure to preserve index tracking:
bash
python3 -c 'a =; print("".join(chr(val ^ i) for i, val in enumerate(a)))'
Use code with caution.

Flag

text
flag{a39a07a239aacd40c948d852a5c9f8d1}
Use code with caution.
Would you like help adapting this writeup into a formal PDF report, or are you ready to jump into another malware analysis challenge? Let me know what you want to tackle next.

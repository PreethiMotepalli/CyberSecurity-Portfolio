# TryHackMe: Mr. Phisher Writeup

A comprehensive walkthrough detailing the step-by-step analysis and extraction of a hidden flag from a malicious Microsoft Word Macro-Enabled Document (`.docm`) inside the TryHackMe **Mr. Phisher** room.

---

## 🔍 Challenge Overview
* **Room Name:** [Mr. Phisher](https://tryhackme.com)
* **Category:** Malware Analysis / Reverse Engineering
* **Difficulty:** Easy
* **Objective:** Perform static analysis on a suspicious macro-enabled document to discover the flag hidden within its obfuscated source code.

---

## 🛠️ Tools Used
* **Linux CLI Utilities:** `unzip`, `python3`
* **Office Suite:** LibreOffice Writer (Basic IDE Module Editor)

---

## 📋 Methodology & Steps

### 1. File Structure Enumeration
Modern Microsoft Office formats (like `.docx` and `.docm`) are actually renamed ZIP containers. We can inspect the internal file mapping securely using the `unzip` tool without triggering any document contents:

```bash
unzip -l MrPhisher.docm
```

**Key Discovery:**
```text
 Length      Date    Time    Name
---------  ---------- -----   ----
...
    12288  1980-01-01 00:00   word/vbaProject.bin
...
```
The presence of `word/vbaProject.bin` confirms that this document houses an embedded **OLE Compound File** containing Visual Basic for Applications (VBA) macro scripts—a common mechanism for real-world phishing execution.

### 2. Static Macro Extraction
Because OLE binaries store compressed and packed streams, standard text scraping utilities like `strings` break up sequences and corrupt array data. To read the pristine source code without executing any malicious triggers, we leverage the safe sandbox environment inside LibreOffice:

1. Right-click `MrPhisher.docm` and open it with **LibreOffice Writer**.
2. When prompted with the security warning, strictly select **"Disable Macros"**.
3. In the application header, navigate to: **Tools ➔ Macros ➔ Edit Macros**.
4. In the left directory tree, expand: `MrPhisher.docm` ➔ `Project` ➔ `Modules` and select **`NewMacros`**.

The complete, uncorrupted extraction routine is revealed in the IDE window:

```vba
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
```

### 3. Deobfuscation & Payload Reverse Engineering
The script implements a basic string obfuscation puzzle:
* **The State Array:** An explicit numerical array `a` holds the encrypted characters.
* **The Mathematical Transform:** A sequential `For` loop steps through each index (`i`). It runs a bitwise **`XOR` logical operation** against the decimal value at that index, translating the outcome back into a standard ASCII string character (`Chr`).

We can safely mirror this dynamic reconstruction sequence via the Linux terminal using Python. By packaging the numbers into an ordered list `[]`, we prevent position shifting and solve the math:

```bash
python3 -c 'a = [102, 109, 99, 100, 127, 100, 53, 62, 105, 57, 61, 106, 62, 62, 55, 110, 113, 114, 118, 39, 36, 118, 47, 35, 32, 125, 34, 46, 46, 124, 43, 124, 25, 71, 26, 71, 21, 88]; print("".join(chr(val ^ i) for i, val in enumerate(a)))'
```

---

## 🏁 Flag
```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```

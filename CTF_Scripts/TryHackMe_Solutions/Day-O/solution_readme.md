# TryHackMe - Day-O Writeup

A comprehensive walkthrough and technical breakdown of the **Day-O** memory forensics and malware analysis room on TryHackMe. 

## Case Overview
* **Room Complexity:** Medium
* **Incident Profile:** A workstation user (`s.reyes`) reported an application freeze while reviewing a document package. A subsequent memory capture revealed an unexpected executable region mapped inside a user process space.
* **Objective:** Audit the memory dump, trace the entry vector, isolate the payload handler, and extract the underlying data decryption components.

---

## 🛠️ Tactical Breakdown & Solution Steps

### 1. Process Discovery & Triage
The baseline operating system information and process tree structure were evaluated using Volatility 3:
```bash
# Analyze OS profile properties
vol -f memory.mem windows.info

# Audit the process tree map for anomalies
vol -f memory.mem windows.pstree
```
* **Suspicious Target:** An untrusted executable was detected running out of the user's Downloads directory path: `\Device\HarddiskVolume1\Users\s.reyes\Downloads\DocumentReview\ReviewClient.exe`.
* **Identified Binary:** `ReviewClient.exe` (**PID: 6260**)

### 2. Memory Space Analysis
Scanning Virtual Address Descriptors (VAD) for hidden executable regions using the `malfind` plugin to locate injected code or shellcode stubs:
```bash
vol -f memory.mem windows.malfind --pid 6260
```
* **Private Allocation Region:** An executable memory region with `PAGE_EXECUTE_READWRITE` permissions was successfully identified.
* **Starting Virtual Address:** `0x8e0000`

### 3. File Context & Evasion Vectors
Auditing active operational handle tables to determine where the application read the initial bytecode payload from disk:
```bash
vol -f memory.mem windows.handles --pid 6260
```
* **Target File Reference:** `\Device\HarddiskVolume1\Users\s.reyes\Downloads\DocumentReview\review-cover.png`
* **MITRE ATT&CK Mapping:** **T1027.009 (Embedded Payloads)**. The malware embedded its primary stage shellcode directly as an overlay at the end of a legitimate image structure rather than dynamically encoding it into pixel bits via steganography. The MITRE ATT&CK sub-technique best describes how the payload is stored in the recovered PNG file: Tactic: Defense Evasion (Stealth), Technique: Obfuscated Files or Information (T1027), Sub-Technique **`T1027.009`** corresponds to Embedded Payloads

### 4. Code Extraction & Deobfuscation Logic
Dumping the raw executable VAD memory boundaries for offline reverse engineering in Ghidra:
```bash
vol -f memory.mem windows.malfind --pid 6260 --dump
```
* **Generated File:** `pid.6260.vad.0x8e0000-0x8e0fff.dmp`
When analyzed statically inside Ghidra, the payload initializes a dynamic string lookup loop by parsing the Process Environment Block (PEB) to locate core Windows execution frameworks out of the loaded module list without declaring static imports. 
* **Target Resolution API:** The shellcode builds string character arrays little-endian on the stack to dynamically resolve and load **`kernel32.WinExec`**.

### 5. Runtime Emulation & Key Recovery
To bypass custom math translation loops (`SUB byte ptr [RSP + RCX*0x1], 0x25`) that dynamically deobfuscate text inside memory, the payload environment was emulated inside a virtual environment using **Speakeasy**:
```bash
# Initialize the forensic module environment
source ~/Desktop/artifacts/tools/venv/bin/activate

# Emulate the shellcode stream to catch API parameters
python3 -m speakeasy -t pid.6260.vad.0x8e0000-0x8e0fff.dmp -r -a x86
```
The emulator cleanly intercepted the `kernel32.WinExec` layer as it processed an obfuscated PowerShell execution sequence. Normalizing the scrambled base64 command line block exposed the core 64-character encryption key passed as a runtime argument to handle the stage-2 storage extraction.
* **Document Cache AES-256 Key:** `7d714a7267e88abc1afd223830cb74d7c840f677ff165fbec9c134595f06faa8`

The Final Flag: `THM{2b3cc75adab999202e1879af542b2c11}`

---

## 🛡️ Defensive Takeaways
1. **Directory Monitoring:** Closely monitor and restrict execution configurations for unsigned processes running natively within volatile user paths such as `\Downloads\` or `\AppData\`.
2. **Overlay Checking:** Enforce deep file-structure validation tools capable of identifying out-of-boundary tracking flags or trailing appended payloads (`.009`) hidden inside common rich media file headers like PNGs.
3. **Behavioral Visibility:** Relying entirely on static file signature scans (`strings`) will fall short when dealing with dynamic memory-only PEB walkers. Emulation tools (`speakeasy`) and forensic volatile memory frameworks are vital for trapping keys at execution time.

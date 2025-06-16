# Documentation to initialize and run Piper TTS in Linux Operating System

## Pre-requisites<br>
         
  1. **Python**
     
     a. Check version
       ```
       python --version
       ```
     b. Install if needed  
       ```
       sudo apt update && sudo apt install python3
       ```
  <br>
  <br>
  <br>
  
  2. **Required Python Modules**

     a. All the neccessary modules are a part of the python standard library  
       &nbsp;&nbsp;&nbsp;```os, sys, tarfile, urllib.request, shutil, glob, subprocess``` <br><br>
     b. Any additional pip installations are not required.
  <br>
  <br>
  <br>
  
  3. **File Permissions and Directory** <br><br>
     a. Permissions to write in the script directory<br><br>
     b. By default, the given script would set executable permissions. However, writing permissions can be   
      &nbsp;&nbsp;&nbsp;&nbsp;manually allocated should there be any problems. [Read More](https://www.redhat.com/en/blog/linux-file-permissions-explained)<br><br>
     c. Make sure that all the downloaded files (script, voice module (.onnx) and config (.json) files are in the same directory).
     
  <br>
  <br>
  <br>  
  
  5. **System Architecture** <br><br>
    a. ARM64 (aarch64) - for Raspberry Pi 4/5 <br><br>
    b. x86_64 - for standard Linux PCs <br><br>
    c. Script currently configured for ARM64 (Raspberry Pi)
  <br>
  <br>
  <br>
  
  6. **Audio Libraries (Optional)** <br>
    a. For audio playback testing:
      ```
       sudo apt install alsa-utils
      ```
      <br>
     
     b. Test with: 
     ``` 
     aplay output.wav 
     ```
     <br>
     <br>
     <br>
 ### Quick Update commands
 ```
sudo apt update
python3 piper_tts_script.py
 ```

<br>
<br>
<br>

## Troubleshooting
- If permission errors occur, ensure you have write access to the directory  
- If download fails, check internet connection and firewall settings  
- For audio issues, check ALSA configuration:
  ```
  aplay -l
  ```

<br>
<br>
<br>

##  Supported Voice Models  
- Download from [HERE](https://github.com/rhasspy/piper/blob/master/VOICES.md)  
- Make sure you download both: onnx file and json file (within the script directory)  

<br>
<br>
<br>
  
## First Run
  1. Place your .txt file, .onnx model, and .json config in the script directory
   
  2. Run:
     ```
     python3 piper_tts_script.py
     ```  
  
  3. Script will automatically download and setup Piper binary  
  
  4. Follow prompts to select text file (if multiple exist)  
  
  5. Output .wav file will be created with same name as input .txt file 

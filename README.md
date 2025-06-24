Livermore Loops
===============

This repositoty is a UI for the Livermore Loops cli benchmark tool.

[Livermore Loops cli Github Repository](https://github.com/waverian/lfk-mp-benchmark)

Objective
---------

Benchmark CPUs:

- x86
    - Intel
    - AMD  
- Arm: armv7, aarch64 variants
    - Qualcom
    - Apple
    - Samsung
    - Nvidia
    - Raspberry Pi 

Interfaces
----------

cli

 - Refer to https://github.com/waverian/lfk-mp-benchmark

Kivy UI

 - This Repo https://github.com/waverian/benchmarkapp

Architectures
-------------

- x86
- x86_64
- arm
- aarch64

OS
--

- Linux
- Windows
- macOS
- Android
- iOs

Fetaures of Kivy UI
-------------------

- Run Benchmark
    - Show Benchmark + CPU + OS Details
    - Show Benchmark Results
- Graphs for comparison with historical data/benchmarks
    - Show current machine benchmark Results
    - Show Historical benchmark Results.
- Museum
    - Show historical data for CPUs
    
Permissions
-----------

On Android < API 29 Our App currently asks for permissions for extrenal storage.
Android API 29 onwards has mediastore which helps us share file,
saved in external storage; without having to ask for permissions.
API < 29 we explicitly ask for permissions and based on state of permissions,
enable sharing if permissions is granted.

This should idealy be replaced with using FileProvider which fascilitates
targetted permissions just for the file being shares, after support for it has been included in
p4a and buildozer.

Install Instructions
--------------------


Clone the source.

    git clone https://github.com/waverian/benchmarkapp
    cd benchmarkapp

Create a venv & activate it.

    python3 -m venv ./venv
    source venv/bin/activate

Install requirements.

    pip install -r requirements.txt

Run App.

    python benchmarkapp/main.py


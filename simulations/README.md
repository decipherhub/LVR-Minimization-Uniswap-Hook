# Simulation Scripts for Diamond Protocol

Inspired by [LVR simulation scripts](https://github.com/The-CTra1n/LVR) from @The-CTra1n, 
this python scripts simulate the behaviours of various method suggested in the [thesis on Diamond protocol](https://eprint.iacr.org/2022/1420.pdf)
and [LVR minimization research on ethresearch](https://ethresear.ch/t/lvr-minimization-in-uniswap-v4/15900), and generate relative outputs as a form
of graph pngs.

## How to run scripts

1. Create venv and configure .env files to decide where to save png files
```
python3 -m venv .venv
cp .env.example .env
vi .env

// Inside .env, insert an appropriate path for the graphs to be saved.
PATH_FOR_PNGS="/YOUR_PATH/"
```

2. Activate venv
```
source .venv/bin/activate
```

3. Install requirements
```
pip install -r requirements.txt
```

4. Run scripts and deactivate
```
python Slippage.py

deactviate
```
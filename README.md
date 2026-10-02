# dedicated-portfolio-calculator
Optimize a treasury portfolio against given cash flows to minimize cost. 

Project for APPM 4720 - Open Topics in Applied Mathematics: Mathematical Finance instructed by Dr. Daniel Brown.

## Build and Run

### Requirements

- Python 3.11 or newer
- Git

### Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/<your-username>/dedicated-portfolio-calculator.git
cd dedicated-portfolio-calculator
python -m venv .venv
```

Activate the environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the project and its dependencies (defined in `pyproject.toml`):

```bash
pip install -e .
```

This installs NumPy, pandas, SciPy, and QuantLib.

### Run

Start the calculator from the repository root:

```bash
python -m portfolio_calculator.main
```

or use the installed command:

```bash
portfolio-calculator
```

The program is interactive. It prompts in the terminal for:

1. The settlement date
2. The path to the bond price file (Treasury market prices, one row per security)
3. The path to the cash flow requirements file (dates and amounts)
4. The path to output the resulting portfolio as a .csv file

If no feasible portfolio exists for the inputs, the program says so and asks you to re-enter them. Otherwise it writes the minimum-cost portfolio as a .csv of CUSIPs and principal amounts.

### Troubleshooting

- `ModuleNotFoundError: No module named 'portfolio_calculator'`: the package is not installed in the active environment. Activate the virtual environment and run `pip install -e .` again.
- QuantLib fails to install: confirm you are on Python 3.11 or newer, and that `pip` is up to date (`python -m pip install --upgrade pip`).

> AI Acknowledgement: Claude Sonnet 5.5 was used to copy and paste error messages into for explanation and debugging. It was also used to partially generate the Build and Run section above.
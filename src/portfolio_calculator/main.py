"""
main.py

User script for the calculator. User specifies inputs and output path.
"""

import pandas as pd
from portfolio_calculator.calculator import Calculator

def main():
    portfolio_constructed = False
    output_successful = False

    while not output_successful:
        while not portfolio_constructed:
            settlement_date_input = input("Enter settlement date (yyyy-mm-dd): ")
            date_parsed = False

            while not date_parsed:
                try:
                    settlement_date = pd.to_datetime(settlement_date_input)
                    date_parsed = True
                except:
                    print("Error parsing settlement date. Please re-enter the date in format yyyy-mm-dd.")
                    settlement_date_input = input("Enter settlement date (yyyy-mm-dd): ")
                
            bond_prices_input = input("Specify bond prices path (csv): ")
            bond_prices_read = False

            while not bond_prices_read:
                try:
                    bond_prices = pd.read_csv(bond_prices_input, header=None)
                    bond_prices_read = True
                except:
                    print("Error reading bond prices file. Please re-enter the path to the csv file.")
                    bond_prices_input = input("Specify bond prices path (csv): ")

            cash_flows_input = input("Specify cash flows path (csv): ")
            cash_flows_read = False

            while not cash_flows_read:
                try:
                    cash_flows = pd.read_csv(cash_flows_input)
                    cash_flows_read = True
                except:
                    print("Error reading cash flows file. Please re-enter the path to the csv file.")
                    cash_flows_input = input("Specify cash flows path (csv): ")

            cash_flow_dates_parsed = False

            while not cash_flow_dates_parsed:
                try:
                    cash_flows = pd.read_csv(cash_flows_input)
                    cash_flows['dates'] = pd.to_datetime(cash_flows['dates'])
                    cash_flow_dates_parsed = True
                except:
                    print("Error parsing cash flow dates. Please ensure the 'dates' column contains dates of a valid format.")
                    cash_flows_input = input("Specify cash flows path (csv): ")

            output_path = input("Specify output path (csv): ")

            calculator = Calculator(settlement_date, bond_prices, cash_flows)

            try:
                portfolio = calculator.construct_portfolio()
            except Exception as e:
                print(f"Error constructing portfolio: {e}")
                print("Please re-enter the inputs.")
            else:
                if portfolio is not None:
                    portfolio_constructed = True
                else:
                    print("No feasible portfolio could be constructed with the given inputs. Please re-enter the inputs.")

        try:
            portfolio.to_csv(output_path, index=False)
            output_successful = True
            print(f"Portfolio successfully written to {output_path}.")
        except Exception as e:
            print(f"Error writing output file: {e}")
            print("Please re-enter the output path.")
            output_path = input("Specify output path (csv): ")


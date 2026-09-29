"""
calculator.py

This module contains the Calculator class, which performs the optimization for a given portfolio.
"""

class Calculator:
    def __init__(self, settlement_date, bond_prices, cash_flows):
        self.settlement_date = settlement_date
        self.bond_prices = bond_prices
        self.cash_flows = cash_flows
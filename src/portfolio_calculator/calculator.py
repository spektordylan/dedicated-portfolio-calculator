"""
calculator.py

This module contains the Calculator class, which performs the optimization for a given portfolio.
"""

import pandas as pd
import QuantLib as ql
from scipy.optimize import linprog

class Calculator:
    def __init__(self, settlement_date, bond_prices, cash_flows):
        """
        Initialize the calculator with settlement date given as datetime object, bond prices given as a pandas DataFrame, and cash flows given as a pandas DataFrame.
        """
        self.settlement_date = settlement_date
        self.bond_prices = bond_prices
        self.cash_flows = cash_flows

    def construct_portfolio(self):
        """
        Method for constructing the optimal portfolio called by the user script in main.py. 
        
        Returns:
            portfolio (pd.DataFrame)
                DataFrame with two columns:
                - 'CUSIP': the CUSIPs of the bonds in the optimal portfolio.
                - 'Principal': the principal amounts of these bonds.
        """
        clean_bond_price_data = self.__clean_bond_price_date()

        bond_data_with_dirty_prices = self.__calculate_dirty_bond_prices(clean_bond_price_data)


    def __clean_bond_price_data(self):
        """
        Private method for cleaning the bond prices DataFrame. This method is called by construct_portfolio().
        (Note conflicting terminology - we are cleaning the data but the bond prices also happen to be clean prices.)
        
        Returns:
            cleaned_bond_prices (pd.DataFrame)
        """
        bond_prices = self.bond_prices.copy()

        bond_prices.columns = ['CUSIP', 'Security_Type', 'Rate', 'Maturity_Date', 'Call_Date', 'Buy', 'Sell']

        # call date is always blank for Treasuries, calculator does not need sell price
        bond_prices = bond_prices.drop(columns=['Call_Date', 'Sell'])

        # filter to desired security types
        filtered_bond_prices = bond_prices.query(
            'Security_Type in ["MARKET BASED BILL", "MARKET BASED NOTE", "MARKET BASED BOND"] and Buy != 0'
        )
        return filtered_bond_prices.dropna()


    def __calculate_dirty_bond_prices(self, clean_bond_prices):
        """
        Private method for converting clean bond price data into dirty prices. This method is called by construct_portfolio().
        Dirty price is per $100 of principal.

        Returns:
            dirty_bond_prices (pd.DataFrame)
                Dataframe with new Dirty_Price column
        """
        dirty_prices = []

        settlement_date = self.settlement_date
        ql_settlement_date = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
        
        for bond in clean_bond_prices:
            security_type = bond['Security_Type']

            if security_type == "MARKET BASED BILL":
                dirty_prices.append(bond['Buy'])
                continue

            clean_price = bond['Buy']
            maturity_date = bond['Maturity Date']
            ql_maturity_date = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

            schedule = ql.Schedule(ql_settlement_date, ql_maturity_date, ql.Period(ql.Semiannual), ql.NullCalendar(), 
                                   ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, 
                                   ql.date.isEndOfMonth(ql_maturity_date))

            rate = bond['Rate']

            ql_bond = ql.FixedRateBond(0, 100.0, schedule, [rate], ql.ActualActual(ql.ActualActual.Bond, schedule))

            accrued_interest = ql_bond.accruedAmount(ql_settlement_date)
            dirty_prices.append(accrued_interest + clean_price)

        return clean_bond_prices.assign(Dirty_Price=dirty_prices)
"""

def bondCashFlows(settlementDate: date, maturityDate: date, couponRate: float, principal: float = 100) -> Tuple[List[date], List[float]]:
    
    Calculate the cash flows for a treasury note or bond.

    Returns a tuple of two lists. The first list is the dates of the cash flows, and the second list is the cash flow amounts. 
    The cash flow amounts are for $100 of principal.
    

    previous_coupon_date = __previous_coupon_date(settlementDate, maturityDate)
    next_coupon_date = __move_months(previous_coupon_date, 6)

    cashFlows = []
    cashFlowDates = []

    while next_coupon_date <= maturityDate:
        cashFlows.append(couponRate / 2 * principal)
        cashFlowDates.append(next_coupon_date)
        next_coupon_date = __move_months(next_coupon_date, 6)

    cashFlows[-1] += principal

    return cashFlowDates, cashFlows"""

"""
calculator.py

This module contains the Calculator class, which performs the optimization for a given portfolio.
"""

class Calculator:
    def __init__(self, settlement_date, bond_prices, cash_flows):
        """
        Initialize the calculator with settlement date given as pandas datetime, bond prices given as a pandas DataFrame, and cash flows given as a pandas DataFrame.
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

        dirty_bond_prices = self.__calculate_dirty_bond_prices(clean_bond_price_data)


    def __clean_bond_price_data(self):
        """
        Private method for cleaning the bond prices DataFrame. This method is called by construct_portfolio().
        (Note conflicting terminology - we are cleaning the data but the bond prices also happen to be clean prices.)
        
        Returns:
            cleaned_bond_prices (pd.DataFrame)
        """
        bond_prices = self.bond_prices.copy()

        bond_prices.columns = ['CUSIP', 'Security Type', 'Rate', 'Maturity Date', 'Call Date', 'Buy', 'Sell']

        # call date is always blank for Treasuries, calculator can ignore sell price
        bond_prices = bond_prices.drop(columns=['Call Date', 'Sell'])

        # filter to desired security types
        filtered_bond_prices = bond_prices.query('Security Type in ["MARKET BASED BILL", "MARKET BASED NOTE", "MARKET BASED BOND"]')

        return filtered_bond_prices.dropna()


    def __calculate_dirty_bond_prices(self, clean_bond_prices):
        """
        Private method for converting clean bond price data into dirty prices.

        Returns:
            dirty_bond_prices (pd.DataFrame)
        """
        # convert to dirty prices


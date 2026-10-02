"""
calculator.py

This module contains the Calculator class, which constructs the desired portfolio.
"""

import pandas as pd
import QuantLib as ql
from scipy.optimize import milp, LinearConstraint
import numpy as np

class Calculator:
    def __init__(self, settlement_date, bond_prices, cash_flows):
        """
        Initialize the calculator with settlement date given as datetime object, bond prices given as a pandas DataFrame, and cash flows given as a pandas DataFrame.
        """
        self.settlement_date = settlement_date
        self.bond_prices = bond_prices
        self.cash_flows = cash_flows

        self.ql_settlement_date = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)

    def construct_portfolio(self):
        """
        Method for constructing the optimal portfolio called by the user script in main.py. 
        
        Returns:
            portfolio (pd.DataFrame)
                DataFrame with two columns:
                - 'CUSIP': the CUSIPs of the bonds in the optimal portfolio.
                - 'Principal': the principal amounts of these bonds.
        """
        clean_bond_price_data = self.__clean_bond_price_data()

        bond_data_with_dirty_prices = self.__calculate_dirty_bond_prices(clean_bond_price_data)

        bond_data_with_matched_cash_flows = self.__find_and_match_cash_flows(bond_data_with_dirty_prices)

        # assemble A matrix of cash flows matched to each cash flow requirement
        A = np.array(bond_data_with_matched_cash_flows['Matched_Cash_Flows'].tolist()).T
        # append submatrix representing rolling surplus cash flow
        m, n = A.shape 
        A = np.hstack([A, -np.eye(m) + np.diag(np.ones(m - 1), k=-1)])

        # assemble b vector of cash flow requirements
        b = np.array(self.__clean_cash_flow_data()['cfs'].tolist())

        # assemble c vector of dirty prices (minimizing total cost to purchase bonds)
        c = np.array(bond_data_with_matched_cash_flows['Dirty_Price'].tolist() + [0] * m)

        # solve linear program
        # uses milp instead of linprog to better handle integer constraint on bond amounts
        constraints = LinearConstraint(A, b, b) # use b for lower and upper for equality constraint
        integrality = np.concatenate([np.ones(n), np.zeros(m)]) # all bond amounts must be integers
        res = milp(c, constraints=constraints, integrality=integrality)

        if res.success:
            output = self.__build_output_dataframe(res.x[:n], bond_data_with_matched_cash_flows)
            print(f'Total cost: {res.fun}')
            return output
        else:
            return None


    def __clean_bond_price_data(self):
        """
        Private method for cleaning the bond prices DataFrame. This method is called by construct_portfolio().
        (Note conflicting terminology - we are cleaning the data but the bond prices also happen to be clean prices.)
        
        Returns:
            cleaned_bond_prices (pd.DataFrame)
        """
        bond_prices = self.bond_prices.copy()

        bond_prices.columns = ['CUSIP', 'Security_Type', 'Rate', 'Maturity_Date', 'Call_Date', 'Buy', 'Sell', 'End_of_Day']

        # call date is always blank for Treasuries, calculator does not need sell price or end of day
        bond_prices = bond_prices.drop(columns=['Call_Date', 'Sell', 'End_of_Day'])

        # filter to desired security types
        filtered_bond_prices = bond_prices.query(
            'Security_Type in ["MARKET BASED BILL", "MARKET BASED NOTE", "MARKET BASED BOND"] and Buy != 0'
        )

        filtered_bond_prices['Maturity_Date'] = pd.to_datetime(filtered_bond_prices['Maturity_Date'], errors='coerce')
        return filtered_bond_prices.dropna().reset_index(drop=True)


    def __clean_cash_flow_data(self):
        """
        Private method for cleaning the cash flows DataFrame. This method is called by construct_portfolio().
        
        Returns:
            cleaned_cash_flows (pd.DataFrame)
        """
        cash_flows = self.cash_flows.copy()
        cash_flows.columns = ['dates', 'cfs']
        cash_flows['dates'] = pd.to_datetime(cash_flows['dates'], errors='coerce')

        cash_flows = cash_flows.dropna()

        # filter to cash flow dates after settlement date only, 
        # not possible to satisfy cash flow requirements before settlement date
        filtered_cash_flows = cash_flows.query('dates >= @self.settlement_date')

        return filtered_cash_flows.sort_values(by='dates').reset_index(drop=True)


    def __calculate_dirty_bond_prices(self, clean_bond_prices):
        """
        Private method for converting clean bond price data into dirty prices. This method is called by construct_portfolio().
        Dirty price is per $100 of principal.

        Returns:
            dirty_bond_prices (pd.DataFrame)
                Dataframe with new Dirty_Price column
        """
        ql_settlement_date = self.ql_settlement_date

        dirty_prices = []
        
        for bond in clean_bond_prices.itertuples():
            if bond.Security_Type == "MARKET BASED BILL":
                dirty_prices.append(bond.Buy)
                continue

            clean_price = bond.Buy
            maturity_date = bond.Maturity_Date
            ql_maturity_date = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

            schedule = ql.Schedule(ql_settlement_date - ql.Period(ql.Semiannual), ql_maturity_date, ql.Period(ql.Semiannual), ql.NullCalendar(), 
                                   ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, 
                                   ql.Date.isEndOfMonth(ql_maturity_date))

            rate = bond.Rate

            ql_bond = ql.FixedRateBond(0, 100.0, schedule, [rate], ql.ActualActual(ql.ActualActual.Bond, schedule))

            accrued_interest = ql_bond.accruedAmount(ql_settlement_date)
            dirty_prices.append(accrued_interest + clean_price)

        return clean_bond_prices.assign(Dirty_Price=dirty_prices)


    def __find_and_match_cash_flows(self, bond_data_with_dirty_prices):
        """
        Private method for finding cash flows for each method and matching with cash flow constraints. This method is called by construct_portfolio().
        
        Returns:
            bond_data_with_cash_flows (pd.DataFrame)
                Dataframe with new Matched_Cash_Flows column
        """
        bond_data = bond_data_with_dirty_prices.copy()
        ql_settlement_date = self.ql_settlement_date

        cash_flows = self.__clean_cash_flow_data()

        num_cf_reqs = cash_flows.shape[0]

        bond_data['Matched_Cash_Flows'] = [[0] * num_cf_reqs for _ in range(bond_data.shape[0])]

        for bond in bond_data.itertuples():
            if bond.Security_Type == "MARKET BASED BILL":
                for i, cash_flow_req in cash_flows.iterrows():
                    if bond.Maturity_Date <= cash_flow_req['dates']:
                        bond.Matched_Cash_Flows[i] = 100
                        break
            else:
                ql_maturity_date = ql.Date(bond.Maturity_Date.day, bond.Maturity_Date.month, bond.Maturity_Date.year)

                # this time, need to keep track of weekends and holidays
                calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond) 

                schedule = ql.Schedule(ql_settlement_date - ql.Period(ql.Semiannual), 
                                       ql_maturity_date, 
                                       ql.Period(ql.Semiannual), 
                                       calendar, 
                                       ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, 
                                       ql.Date.isEndOfMonth(ql_maturity_date))

                rate = bond.Rate

                ql_bond = ql.FixedRateBond(0, 100.0, schedule, [rate], ql.ActualActual(ql.ActualActual.Bond, schedule))

                # quantlib is confusing, just gonna filter cashflows after settlement just in case
                # should have cleaner solution in future, but for now this works
                bond_cashflows = ql_bond.cashflows()
                start_index = 0

                for cash_flow in bond_cashflows:
                    if cash_flow.date() <= ql_settlement_date:
                        start_index += 1
                    else:
                        break

                for cash_flow in bond_cashflows[start_index:]:
                    for i, cash_flow_req in cash_flows.iterrows():
                        if cash_flow.date() <= ql.Date(cash_flow_req['dates'].day, cash_flow_req['dates'].month, cash_flow_req['dates'].year):
                            bond.Matched_Cash_Flows[i] += cash_flow.amount()
                            break # want to match each cash flow to the earliest cash flow requirement, and not duplicate cash flow after

        return bond_data
        

    def __build_output_dataframe(self, bond_amounts, bond_data_with_matched_cash_flows):
        """
        Private method for building the output DataFrame. This method is called by construct_portfolio().
        
        Returns:
            output (pd.DataFrame)
                DataFrame with two columns:
                - 'CUSIP': the CUSIPs of the bonds in the optimal portfolio.
                - 'Principal': the principal amounts of these bonds.
        """
        output = pd.DataFrame({
            'CUSIP': bond_data_with_matched_cash_flows['CUSIP'],
            'Principal': np.round(bond_amounts) * 100
        })

        return output[output['Principal'] > 0]
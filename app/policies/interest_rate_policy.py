from typing import Optional
from camelot.io import read_pdf
import os


class InterestRatePolicy:
    def __init__(self, path) -> None:
        self.path = path
        self.mt = None
        self._data = None

    @property
    def data(self):
        """
        read and parse Interest rate pdf policy
        """
        modification_timestamp = os.path.getmtime(self.path)
        if self._data is None or self.mt is None or self.mt != modification_timestamp:
            t = read_pdf(self.path, flavor="network")
            df = t[0].df
            header_row_index = df.index[(df.iloc[:, 0] == 'Overall Risk') & (
                df.iloc[:, 1] == 'Interest Rate')].tolist()[0]
            df.columns = df.iloc[header_row_index]
            df = df.iloc[header_row_index+1:].reset_index(drop=True)
            self._data = {r[1].strip().capitalize(): float(
                r[2].strip('% ')) for r in df.itertuples()}
            self.mt = modification_timestamp
        return self._data

    def policy_data(self):
        """Get all interest rate  policies as dict 
        with header (list of string) and data (list of lists)."""
        return {
            "header": ["overall risk", "interest_rate_percentage"],
            "data": [[key, value] for key, value in self.data.items()]
        }

    def get_interest_rate_percent_for_risk(self, risk: str) -> Optional[float]:
        """_summary_

        Args:
            risk (str): "Low"/"Medium"/"High"

        Returns:
            Optional[float]: _description_
        """
        data = self.data
        return data.get(risk, None)

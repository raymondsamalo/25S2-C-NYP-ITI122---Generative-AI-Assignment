from typing import Optional
from camelot.io import read_pdf
import os

class RiskPolicy:
    def __init__(self, max_credit_score:Optional[int], min_credit_score:Optional[int], account_status:str, overall_risk:str) -> None:
        self.max_credit_score=max_credit_score
        self.min_credit_score=min_credit_score
        self.account_status=account_status
        self.overall_risk=overall_risk

    def credit_score_is_within(self, credit_score:int)->bool:
        if self.max_credit_score is None and self.min_credit_score is None:
            return False
        if self.max_credit_score is None and self.min_credit_score <=credit_score:
            return True
        if self.min_credit_score is None and self.max_credit_score > credit_score:
            return True
        return credit_score>=self.min_credit_score and credit_score<self.max_credit_score

    def is_matching(self, credit_score:int, account_status:str)->bool:
        return account_status==self.account_status and self.credit_score_is_within(credit_score)
    
    def __str__(self) -> str:
        return f"min: {self.min_credit_score} max: {self.max_credit_score} status: {self.account_status} risk: {self.overall_risk}"

class OverallRiskPolicy:
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
        if self._data is None or self.mt is None or self.mt!= modification_timestamp:
            t=read_pdf(self.path, flavor="network")
            df=t[0].df
            header_row_index= df.index[(df.iloc[:,0]=='Credit Score') & (df.iloc[:,1]=='Account Status')].tolist()[0]
            df.columns = df.iloc[header_row_index]
            df = df.iloc[header_row_index+1:].reset_index(drop=True)
            temp= []
            for r in df.itertuples():
                try:
                    credit_scores = r[1].split(" ") # camelot sometimes detect as - U+2013 sometimes as a U+002d
                    try:
                        min_credit_score = int(credit_scores[0].strip())
                    except ValueError:
                        min_credit_score = None

                    try:
                        max_credit_score = int(credit_scores[-1].strip())
                    except ValueError:
                        max_credit_score = None
                    account_status = r[2].strip().capitalize()
                    risk = r[3].strip().capitalize()
                    rp= RiskPolicy(max_credit_score=max_credit_score,
                                        min_credit_score=min_credit_score,
                                        account_status=account_status,
                                        overall_risk=risk)
                    temp.append(rp)
                except Exception as e:
                    print(e,r, len(r))
            self._data=temp
            self.mt = modification_timestamp
        return self._data
    
    def get_risk(self,  credit_score:int, account_status:str)->Optional[str]:
        """_summary_

        Args:
            risk (str): "Low"/"Medium"/"High"

        Returns:
            Optional[float]: _description_
        """
        for r in self.data:
            rp:RiskPolicy = r
            if rp.is_matching(credit_score=credit_score, account_status=account_status):
                return rp.overall_risk
        return None
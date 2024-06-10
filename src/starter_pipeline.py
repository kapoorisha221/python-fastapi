###read all the audio files 
## Get all the id data from the excel - done
## create funcion to map and add the data in mapping.json for calls 

import pandas as pd
import os, math
from config.config import AzureConfig, LocalConfig
from logs.logger import get_Info_Logger, get_Error_Logger

class starter_class:
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()
    cred = AzureConfig()
    path = LocalConfig()

    def read_data_csv(self):
        print("getting data from csv using read_data_csv")
        s1_call_ids = []
        s1_agent_ids = []
        s1_agent_names = []
        s1_call_dates = []
        s1_comments = []

        s2_call_ids = []
        s2_agent_ids = []
        s2_agent_names = []
        s2_call_dates = []
        s2_comments = []

        s3_call_ids = []
        s3_agent_ids = []
        s3_agent_names = []
        s3_call_dates = []
        s3_comments = []

        sheet_names = [self.cred.sheet1 , self.cred.sheet2, self.cred.sheet3]
        sheet1_res = {}
        sheet2_res = {}
        sheet3_res = {}

        for sheet_name in sheet_names:
            print("sheet_name: ", sheet_name)
            df = pd.read_excel(self.cred.audio_data, sheet_name=sheet_name)
            print(f"the columns in sheet {sheet_name}: ", df.columns)

            for index, row in df.iterrows():
                # print("inner loop _______________________")
                call_id = row["Call id"]
                agent_id = row["Agent id"]
                agent_name = row["Agent name"]
                call_date = row["Call Date"]
                comment = row["Comment"]
                if sheet_name == self.cred.sheet1:
                    sheet_name = self.cred.sheet1
                    # print(sheet_name)
                    if not (pd.isna(call_id) or pd.isna(agent_id)):
                        s1_call_ids.append(int(call_id))
                        s1_agent_ids.append(int(agent_id))
                        s1_agent_names.append(agent_name)
                        s1_call_dates.append(call_date)
                        s1_comments.append(comment if pd.notna(comment) else '')
                    sheet1_res = {"sheetname": sheet_name,"callids": s1_call_ids, "agentids": s1_agent_ids, "agentnames": s1_agent_names, "calldates":s1_call_dates, "comments":s1_comments}
                
                if sheet_name == self.cred.sheet2:
                    
                    sheet_name = self.cred.sheet2
                    # print(sheet_name)
                    if not (pd.isna(call_id) or pd.isna(agent_id)):
                        s2_call_ids.append(int(call_id))
                        s2_agent_ids.append(int(agent_id))
                        s2_agent_names.append(agent_name)
                        s2_call_dates.append(call_date)
                        s2_comments.append(comment if pd.notna(comment) else '')
                    sheet2_res = {"sheetname": sheet_name,"callids": s2_call_ids, "agentids": s2_agent_ids, "agentnames": s2_agent_names, "calldates":s2_call_dates, "comments":s2_comments}

                if sheet_name == self.cred.sheet3:
                    sheet_name = self.cred.sheet3
                    # print(sheet_name)
                    if not (pd.isna(call_id) or pd.isna(agent_id)):
                        s3_call_ids.append(int(call_id))
                        s3_agent_ids.append(int(agent_id))
                        s3_agent_names.append(agent_name)
                        s3_call_dates.append(call_date)
                        s3_comments.append(comment if pd.notna(comment) else '')
                    sheet3_res = {"sheetname": sheet_name,"callids": s3_call_ids, "agentids": s3_agent_ids, "agentnames": s3_agent_names, "calldates":s3_call_dates, "comments":s3_comments}

        return sheet1_res, sheet2_res, sheet3_res



if __name__ == "__main__":
    obj = starter_class()
    obj.read_data_csv()
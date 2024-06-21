import pandas as pd
from config.config import AzureConfig, LocalConfig
from logs.logger import get_Info_Logger, get_Error_Logger

class fetch_data_class:
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()
    def __init__(self):
        self.cred = AzureConfig()
        self.path = LocalConfig()

    def read_data_csv(self):
        print("getting data from csv using read_data_csv")
        s1_call_ids = []
        s1_agent_ids = []
        s1_agent_names = []
        s1_call_dates = []
        s1_casetrigger = []
        s1_calltype = []

        s2_call_ids = []
        s2_agent_ids = []
        s2_agent_names = []
        s2_call_dates = []
        s2_casetrigger = []
        s2_calltype = []

        s3_call_ids = []
        s3_agent_ids = []
        s3_agent_names = []
        s3_call_dates = []
        s3_casetrigger = []
        s3_calltype = []

        s4_call_ids = []
        s4_agent_ids = []
        s4_agent_names = []
        s4_call_dates = []
        s4_casetrigger = []
        s4_calltype = []

        s5_call_ids = []
        s5_agent_ids = []
        s5_agent_names = []
        s5_call_dates = []
        s5_casetrigger = []
        s5_calltype = []

        combined_data = []

        sheet_names = [self.path.sheet1, self.path.sheet2, self.path.sheet3, self.path.sheet4, self.path.sheet5]
        for sh in sheet_names:
            print("sheet name: ", sh)
        sheet1_res = {}
        sheet2_res = {}
        sheet3_res = {}
        sheet4_res = {}
        sheet5_res = {}

        for sheet_name in sheet_names:
            print("sheet_name: ", sheet_name)
            df = pd.read_excel(self.path.audio_data, sheet_name=sheet_name)
            print(f"the columns in sheet {sheet_name}: ", df.columns)

            for index, row in df.iterrows():
                call_id = row["Call id"]
                agent_id = row["Agent id"]
                agent_name = row["Agent name"]
                call_date = row["Call Date"]
                casetrigger = row["Case Trigger"]
                calltype = row["Call Type"]

                if not (pd.isna(call_id) or pd.isna(agent_id)):
                    combined_entry = {
                        "sheet_name": sheet_name,
                        "call_id": int(call_id),
                        "agent_id": int(agent_id),
                        "agent_name": agent_name if pd.notna(agent_name) else '',
                        "call_date": call_date if pd.notna(call_date) else '',
                        "casetrigger": casetrigger if pd.notna(casetrigger) else '',
                        "calltype": calltype if pd.notna(calltype) else ''
                    }
                    combined_data.append(combined_entry)
                    
                    if sheet_name == self.cred.sheet1:
                        s1_call_ids.append(int(call_id))
                        s1_agent_ids.append(int(agent_id))
                        s1_agent_names.append(agent_name)
                        s1_call_dates.append(call_date)
                        s1_casetrigger.append(casetrigger if pd.notna(casetrigger) else '')
                        s1_calltype.append(calltype if pd.notna(calltype) else '')
                        sheet1_res = {"sheetname": sheet_name, "callids": s1_call_ids, "agentids": s1_agent_ids, "agentnames": s1_agent_names, "calldates": s1_call_dates, "casetrigger": s1_casetrigger, "calltype": s1_calltype}
                    
                    elif sheet_name == self.cred.sheet2:
                        s2_call_ids.append(int(call_id))
                        s2_agent_ids.append(int(agent_id))
                        s2_agent_names.append(agent_name)
                        s2_call_dates.append(call_date)
                        s2_casetrigger.append(casetrigger if pd.notna(casetrigger) else '')
                        s2_calltype.append(calltype if pd.notna(calltype) else '')
                        sheet2_res = {"sheetname": sheet_name, "callids": s2_call_ids, "agentids": s2_agent_ids, "agentnames": s2_agent_names, "calldates": s2_call_dates, "casetrigger": s2_casetrigger, "calltype": s2_calltype}
                    
                    elif sheet_name == self.cred.sheet3:
                        s3_call_ids.append(int(call_id))
                        s3_agent_ids.append(int(agent_id))
                        s3_agent_names.append(agent_name)
                        s3_call_dates.append(call_date)
                        s3_casetrigger.append(casetrigger if pd.notna(casetrigger) else '')
                        s3_calltype.append(calltype if pd.notna(calltype) else '')
                        sheet3_res = {"sheetname": sheet_name, "callids": s3_call_ids, "agentids": s3_agent_ids, "agentnames": s3_agent_names, "calldates": s3_call_dates, "casetrigger": s3_casetrigger, "calltype": s3_calltype}
                    
                    elif sheet_name == self.cred.sheet4:
                        s4_call_ids.append(int(call_id))
                        s4_agent_ids.append(int(agent_id))
                        s4_agent_names.append(agent_name if pd.notna(agent_name) else '')
                        s4_call_dates.append(call_date if pd.notna(call_date) else '')
                        s4_casetrigger.append(casetrigger if pd.notna(casetrigger) else '')
                        s4_calltype.append(calltype if pd.notna(calltype) else '')
                        sheet4_res = {"sheetname": sheet_name, "callids": s4_call_ids, "agentids": s4_agent_ids, "agentnames": s4_agent_names, "calldates": s4_call_dates, "casetrigger": s4_casetrigger, "calltype": s4_calltype}
                    
                    elif sheet_name == self.cred.sheet5:
                        s5_call_ids.append(int(call_id))
                        s5_agent_ids.append(int(agent_id))
                        s5_agent_names.append(agent_name if pd.notna(agent_name) else '')
                        s5_call_dates.append(call_date if pd.notna(call_date) else '')
                        s5_casetrigger.append(casetrigger if pd.notna(casetrigger) else '')
                        s5_calltype.append(calltype if pd.notna(calltype) else '')
                        sheet5_res = {"sheetname": sheet_name, "callids": s5_call_ids, "agentids": s5_agent_ids, "agentnames": s5_agent_names, "calldates": s5_call_dates, "casetrigger": s5_casetrigger, "calltype": s5_calltype}


        return sheet1_res, sheet2_res, sheet3_res, sheet4_res, sheet5_res, combined_data



if __name__ == "__main__":
    obj = fetch_data_class()
    sheet1_res, sheet2_res, sheet3_res, sheet4_res, sheet5_res, combined_data = obj.read_data_csv()
    print("Combined Data: ", combined_data)


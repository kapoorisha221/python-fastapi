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
        call_ids = []
        agent_ids = []
        agent_names = []
        call_dates = []
        comments = []
        sheet_name = self.cred.sheet_name
        print("sheet_name: ", sheet_name)
        df = pd.read_excel(self.cred.audio_data, sheet_name=sheet_name)
        print("the columns are: ", df.columns)
        # Append data from each column to the corresponding list
        # call_ids = df["Call id"].tolist()
        # agent_ids = df["Agent id"].tolist()
        # agent_names = df["Agent name"].tolist()
        # call_dates = df["Call Date "].tolist()

         # Check if call_id and agent_id are not NaN
        for index, row in df.iterrows():
            call_id = row["Call id"]
            agent_id = row["Agent id"]
            agent_name = row["Agent name"]
            call_date = row["Call Date "]
            comment = row["Comment"]

            if not (pd.isna(call_id) or pd.isna(agent_id)):
                call_ids.append(int(call_id))
                agent_ids.append(int(agent_id))
                agent_names.append(agent_name)
                call_dates.append(call_date)
                comments.append(comment if pd.notna(comment) else '')
        print("____________call_ids, agent_ids, agent_names, call_dates, comments_____", call_ids, agent_ids, agent_names, call_dates, comments)
        return call_ids, agent_ids, agent_names, call_dates, comments
        



if __name__ == "__main__":
    obj = starter_class()
    obj.read_data_csv()
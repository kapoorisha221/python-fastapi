import datetime
import json
import logging
import os
from pythonjsonlogger import jsonlogger

info_log_path = "logs/log_data/info.log"
error_log_path = "logs/log_data/Error.log"

InfoLogger = logging.getLogger("InfoLogger")
InfoLogger.setLevel(logging.INFO)

InfoFileHandler = logging.FileHandler(info_log_path)

InfoLogFormatter = jsonlogger.JsonFormatter('format=%(asctime)s  %(message)s',datefmt="%Y-%m-%d T%H:%M:%S%z")

InfoFileHandler.setFormatter(InfoLogFormatter)
InfoLogger.addHandler(InfoFileHandler)

ErrorLogger = logging.getLogger("ErrorLogger")
ErrorLogger.setLevel(logging.ERROR)


ErrorFileHandler = logging.FileHandler(error_log_path)

ErrorLogFormatter = jsonlogger.JsonFormatter('format=%(asctime)s %(message)s',datefmt="%Y-%m-%d T%H:%M:%S%z")

ErrorFileHandler.setFormatter(ErrorLogFormatter)
ErrorLogger.addHandler(ErrorFileHandler)

def get_Error_Logger():
    return ErrorLogger

def get_Info_Logger():
    return InfoLogger

def log_Garbage_Collector():
    current_time = datetime.datetime.now(datetime.timezone.utc)
    
    #one_week_ago = current_time - datetime.timedelta(days=7)
    one_week_ago = current_time - datetime.timedelta(seconds=1000)
    
    def is_log_old(log_line):
        log_data = json.loads(log_line)
        timestamp_str = log_data.get("asctime", "")
        if timestamp_str:
            log_timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d T%H:%M:%S%z")
            # print("________________log time stanp _________________",log_timestamp)
            # print("________________one week time stanp _________________",one_week_ago)
            return log_timestamp < one_week_ago
        return False
    

    def remove_old_logs_from_top(log_path):
        with open(log_path, 'r+') as log_file:
            lines = log_file.readlines()
            for idx, line in enumerate(lines):
                if not is_log_old(line):
                    break
            log_file.seek(0)
            log_file.writelines(lines[idx:])
            log_file.truncate()
            get_Info_Logger().info(msg="Log Deleted",extra={"location":"logger.py - remove_old_logs_from_top"})
    
    remove_old_logs_from_top(info_log_path)
    remove_old_logs_from_top(error_log_path)

if __name__ == "__main__":
    info_logger = get_Info_Logger()
    info_logger.info(msg="Success",exc_info="cause we did it!",extra={"this is extra":"cause we deserve reward"})

    error_logger = get_Error_Logger()
    error_logger.error(msg="Error",exc_info="cause we did it!",extra={"this is extra":"cause error may have something extra"})
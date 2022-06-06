import logging
#########################################
#    MISC GLOBAL VARIABLES & CONFIG     #
#########################################

#### APP DATA ####
Appversion = "0.3.0"

#### USER SETTINGS ####
setting_recursive_search = True

#### LOGGING ####
LOG_FILE_NAME = "coursePlanner.log"
LOG_LEVEL = logging.INFO

logging.basicConfig(
    encoding='utf-8',
    filename=LOG_FILE_NAME,
    level=LOG_LEVEL,
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
    )

# ʕ •ᴥ•ʔ
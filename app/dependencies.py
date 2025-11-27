import pathlib
from pyaml_env import parse_config, BaseConfig
from .db import SqliteDB
from .services import CustomerInfoService, CustomerAccountStatusService, CustomerCreditScoreService, ResidencyStatusService, PolicyService
script_directory = pathlib.Path(__file__).parent
config_path = script_directory.parent / 'data' / 'config.yml'
DATA_PATH = (script_directory.parent / 'data').resolve()
CONFIG_MAP = parse_config(config_path.resolve())
CONFIG = BaseConfig(CONFIG_MAP)
db = SqliteDB()
customer_info_service = CustomerInfoService(db)
customer_account_status_service = CustomerAccountStatusService(db)
customer_credit_score_service = CustomerCreditScoreService(db)
customer_residency_status_service = ResidencyStatusService(db)
policy_service = PolicyService(
    CONFIG.policies.overall_risk_doc,
    CONFIG.policies.interest_rate_doc)

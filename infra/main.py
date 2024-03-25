import os
import subprocess
from dotenv import load_dotenv


def config_creds_win():
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '.env'))
    load_dotenv(dotenv_path)
    cmd = f"PowerShell -ExecutionPolicy Unrestricted Set-AWSCredential -AccessKey {os.environ.get('access_key')} -SecretKey {os.environ.get('secret_key')} -StoreAs mjk"
    ec = subprocess.call(cmd, shell=True)

config_creds_win()
subprocess.call("terraform init")
subprocess.call("terraform apply")
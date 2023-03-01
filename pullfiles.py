from ppadb.client import Client as AdbClient
import os


def adb_pull_files():
    client=AdbClient(host="127.0.0.1", port=5037)
    file_path=os.getcwd()+"\\test"
    device = client.device("127.0.0.1:62001")
    opm_data_path="/mnt/user/0/primary/Android/data/com.alpha.mpsen.android/files/bundles"
    files=device.shell(f"ls {opm_data_path}")
    print("Attempting to retrieve game data files.")
    try:
        for file in files.split():
            device.pull(f"{opm_data_path}/{file}",f"{file_path}\{file}")
        print("Successfully pulled files into csv directory.")
    except Exception as error:
        print(error)
adb_pull_files()
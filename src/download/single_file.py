import subprocess
import shlex

def download_file_aria2c(url : str, output_dir : str, connections=4, splits=4):
    """A thin wrapper for aria2c download tool

    Args:
        url (str): path to a remote file
        output_dir (str) : output directory
        connections (int, optional): Connections to a server. Defaults to 4.
        splits (int, optional): quantify splits to fractionalize the file when downloading it in parallel. Defaults to 4.
    """
    cmd = [
        "aria2c",
        "-x", str(connections),
        "-s", str(splits),
        "-d", str(output_dir),
        url
    ]

    print(f"aria2c, running: {' '.join(shlex.quote(arg) for arg in cmd)}")
    result = subprocess.run(cmd, text=True)

    return result

    

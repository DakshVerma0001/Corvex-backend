import argparse
import json
import subprocess


def block_ip(ip: str):
    try:
        # ⚠️ For now we simulate instead of actually blocking
        print(f"[SIMULATION] Blocking IP: {ip}")

        # Real command (we’ll enable later)
        # subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])

        return {"success": True, "blocked_ip": ip}

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True)
    parser.add_argument("--params-json", required=True)

    args = parser.parse_args()
    params = json.loads(args.params_json)

    if args.action == "linux.firewall.block_ip":
        result = block_ip(params["ip"])
    else:
        result = {"success": False, "error": "Unknown action"}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
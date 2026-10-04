from dotenv import load_dotenv
load_dotenv()

import os

# NVIDIA key expiry: verify on build.nvidia.com (old comment "10\02\26" was ambiguous)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is not set. Add it to .env")

# verify current model name on build.nvidia.com
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "nvidia/nemotron-3-super-120b-a12b")
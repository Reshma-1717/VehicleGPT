# VehicleGPT On-Device Language Models (SLM / LLM)

VehicleGPT is designed to operate **100% offline on edge automotive hardware** (e.g. Raspberry Pi 5, NXP i.MX8, NVIDIA Jetson Orin Nano, or Qualcomm Snapdragon Ride).

## Zero Silent Downloads Policy

In strict adherence to technical and edge constraints:
- VehicleGPT **never downloads large model weights automatically or silently** during startup.
- When no model is installed in this directory, VehicleGPT automatically and gracefully uses its built-in **Deterministic Analytical Explanation Engine** (sub-20ms latency, zero hallucinations, verified mathematical proofs).

---

## Recommended Edge Candidate Models

| Model Architecture | Quantization | Disk Size | RAM Footprint | Target Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3.2 1B Instruct** | `Q4_K_M` (4-bit) | ~780 MB | ~1.1 GB | Constrained Edge (~2GB RAM, 2 ARM Cores) |
| **Qwen 2.5 1.5B Instruct** | `Q4_K_M` (4-bit) | ~980 MB | ~1.3 GB | Constrained Edge (~2GB RAM, 2 ARM Cores) |
| **Llama 3.2 3B Instruct** | `Q4_K_M` (4-bit) | ~2.0 GB | ~2.6 GB | Vehicle HPC / Cockpit Domain Controller |

---

## How to Install an On-Device Model

To enable on-device SLM text generation, download one of the candidate GGUF files and place it into this directory (`models/`):

### Option A: Llama 3.2 1B Instruct (Recommended for 2GB Edge)
```bash
# Using huggingface-cli:
huggingface-cli download bartowski/Llama-3.2-1B-Instruct-GGUF \
  Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  --local-dir models/

# Or via curl:
curl -L -o models/Llama-3.2-1B-Instruct-Q4_K_M.gguf \
  https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

### Option B: Qwen 2.5 1.5B Instruct
```bash
curl -L -o models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf
```

Update your `.env` or set `LLM_MODEL_PATH=models/Llama-3.2-1B-Instruct-Q4_K_M.gguf`.

---

## Technical Constraints & Safety Guarantees

1. **Numerical Immutability**: All numerical calculations (range drop km, efficiency drop %, temperatures, battery SOC, event counts) are calculated by the Python analytical engine and strictly passed as immutable verified facts. The language model is forbidden from inventing or recalculating numbers.
2. **Read-Only Context**: The SLM is given zero SQL write access or vehicle bus access.

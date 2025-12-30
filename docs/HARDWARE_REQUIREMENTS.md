# Hardware Requirements Guide

> Running local LLMs requires significant hardware resources. This guide helps you choose the right configuration for your budget and performance needs.

## Overview

The Sovereign Council runs multiple LLM models simultaneously:
- **3 Council Members**: Each provides an independent perspective (7-8B parameter models)
- **1 Chairman**: Synthesizes perspectives and preserves dissent (ideally 70B parameter model)
- **Analysis Engine**: Performs disagreement detection and minority report extraction

The primary bottleneck is **GPU VRAM** for model loading and inference. Secondary considerations are system RAM for model swapping and CPU for preprocessing.

---

## Hardware Tiers

### Tier 1: Consumer Grade (Entry Level)

**Target Audience**: Hobbyists, students, and those exploring local LLM inference on existing hardware.

| Component | Specification | Notes |
|-----------|---------------|-------|
| **GPU** | NVIDIA RTX 3060 12GB or RTX 4060 8GB | Single consumer GPU |
| **System RAM** | 16GB DDR4 | Minimum for model swapping |
| **CPU** | 6+ cores (Intel i5/AMD Ryzen 5) | Moderate preprocessing needs |
| **Storage** | 100GB SSD | Model storage (~30GB for base models) |

**Operational Constraints**:
- Sequential inference only (one model at a time)
- No 70B chairman model - use 7B/8B fallback
- Expect 30-60 second response times per perspective
- Total deliberation time: 3-5 minutes

**Recommended Model Configuration**:
```yaml
council:
  members:
    - id: "phi"
      model: "llama3.2:3b"  # Smaller model for constrained VRAM
    - id: "psi"
      model: "mistral:7b-q4"  # Quantized to 4-bit
  chairman:
    model: "llama3.2:8b-q4"  # Use 8B as chairman fallback
```

**Estimated Cost (New Hardware)**:
- Budget Build: $600-800 USD
- Using existing gaming PC: $0 (if compatible GPU)

**Example Configurations**:
| Option | GPU | RAM | Approx. Cost |
|--------|-----|-----|--------------|
| Budget Desktop | RTX 3060 12GB | 16GB | $700 |
| Laptop | RTX 4060 Laptop | 16GB | $1,000 |
| Used/Refurbished | RTX 3080 10GB | 16GB | $500 |

---

### Tier 2: Enthusiast Grade (Recommended)

**Target Audience**: Privacy-conscious professionals, developers, and serious home users.

| Component | Specification | Notes |
|-----------|---------------|-------|
| **GPU** | NVIDIA RTX 4070 Ti 16GB or RTX 3090 24GB | High-VRAM consumer GPU |
| **System RAM** | 32GB DDR4/DDR5 | Comfortable model management |
| **CPU** | 8+ cores (Intel i7/AMD Ryzen 7) | Good preprocessing performance |
| **Storage** | 250GB NVMe SSD | Fast model loading |

**Operational Characteristics**:
- Partial parallel inference (2-3 models concurrently)
- 70B chairman model with 4-bit quantization (Q4_K_M)
- Expect 15-30 second response times per perspective
- Total deliberation time: 1-2 minutes

**Recommended Model Configuration**:
```yaml
council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
    - id: "psi"
      model: "mistral:7b"
    - id: "omega"
      model: "qwen2.5:7b"
  chairman:
    model: "llama3.2:70b-q4"  # Quantized 70B fits in 24GB
```

**Estimated Cost (New Hardware)**:
- Desktop Build: $1,500-2,500 USD
- Pre-built Workstation: $2,000-3,000 USD

**Example Configurations**:
| Option | GPU | RAM | Approx. Cost |
|--------|-----|-----|--------------|
| RTX 4070 Ti Build | RTX 4070 Ti 16GB | 32GB | $1,800 |
| RTX 3090 Build | RTX 3090 24GB | 32GB | $1,500 (used GPU) |
| RTX 4080 Build | RTX 4080 16GB | 32GB | $2,200 |
| Multi-GPU Budget | 2x RTX 3060 12GB | 32GB | $1,400 |

---

### Tier 3: Professional Grade (Optimal)

**Target Audience**: Organizations, researchers, and users requiring production-quality inference.

| Component | Specification | Notes |
|-----------|---------------|-------|
| **GPU** | NVIDIA RTX 4090 24GB or A6000 48GB | Professional/Prosumer GPU |
| **System RAM** | 64GB DDR5 | Full parallel model management |
| **CPU** | 12+ cores (Intel i9/AMD Ryzen 9/Threadripper) | Optimal preprocessing |
| **Storage** | 500GB+ NVMe SSD | Multiple model versions |

**Operational Characteristics**:
- Full parallel inference (all models simultaneously)
- 70B chairman at 8-bit quantization (better quality)
- Expect 8-15 second response times per perspective
- Total deliberation time: 30-60 seconds

**Recommended Model Configuration**:
```yaml
council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
    - id: "psi"
      model: "mistral:7b"
    - id: "omega"
      model: "qwen2.5:7b"
  chairman:
    model: "llama3.2:70b"  # Full precision or 8-bit
```

**Estimated Cost (New Hardware)**:
- Desktop Workstation: $3,500-5,000 USD
- Professional Workstation: $6,000-10,000 USD

**Example Configurations**:
| Option | GPU | RAM | Approx. Cost |
|--------|-----|-----|--------------|
| RTX 4090 Build | RTX 4090 24GB | 64GB | $4,000 |
| Dual RTX 4080 | 2x RTX 4080 16GB | 64GB | $4,500 |
| A6000 Workstation | NVIDIA A6000 48GB | 64GB | $8,000 |

---

### Tier 4: Enterprise Grade (Maximum Performance)

**Target Audience**: Enterprise deployments, AI research labs, organizations with compliance requirements.

| Component | Specification | Notes |
|-----------|---------------|-------|
| **GPU** | 2x NVIDIA A100 80GB or H100 | Data center GPUs |
| **System RAM** | 128GB+ ECC DDR5 | Enterprise reliability |
| **CPU** | AMD EPYC or Intel Xeon | Server-grade processor |
| **Storage** | 1TB+ NVMe RAID | Redundancy and speed |

**Operational Characteristics**:
- Multiple 70B models in parallel
- Near-instant model switching
- Sub-10 second total deliberation time
- Support for larger models (Llama 405B)

**Estimated Cost**:
- $15,000-50,000+ USD depending on configuration

---

## GPU Comparison Table

| GPU | VRAM | Approx. Price (USD) | Max Model Size | Parallel 7B Models | Notes |
|-----|------|---------------------|----------------|---------------------|-------|
| RTX 3060 | 12GB | $250 (used) | 7B full / 13B Q4 | 1 | Entry level |
| RTX 4060 Ti | 16GB | $400 | 13B full / 30B Q4 | 2 | Good value |
| RTX 3090 | 24GB | $700 (used) | 30B full / 70B Q4 | 3 | Best used value |
| RTX 4070 Ti | 16GB | $700 | 13B full / 30B Q4 | 2 | Power efficient |
| RTX 4080 | 16GB | $1,000 | 13B full / 30B Q4 | 2 | Fast inference |
| RTX 4090 | 24GB | $1,600 | 30B full / 70B Q4 | 3-4 | Consumer king |
| A6000 | 48GB | $4,500 | 70B full | 6+ | Professional |
| A100 | 80GB | $10,000+ | 70B+ full | 8+ | Data center |
| H100 | 80GB | $25,000+ | 70B+ full | 10+ | Cutting edge |

---

## Apple Silicon Guide

Apple Silicon Macs offer unified memory architecture, making them viable for local LLM inference.

| Model | Unified Memory | Max Model Size | Performance Tier |
|-------|----------------|----------------|------------------|
| M1/M2 Base | 8-16GB | 7B Q4 | Consumer (limited) |
| M1/M2 Pro | 16-32GB | 13B full / 30B Q4 | Consumer |
| M1/M2 Max | 32-64GB | 30B full / 70B Q4 | Enthusiast |
| M1/M2 Ultra | 64-128GB | 70B full | Professional |
| M3 Max | 36-128GB | 30B-70B full | Enthusiast-Professional |

**Apple Silicon Notes**:
- Unified memory means CPU and GPU share RAM - no separate VRAM
- Performance is competitive but generally slower than equivalent NVIDIA GPUs
- Power efficiency is excellent for laptop use
- Use [Ollama for macOS](https://ollama.ai/) for Metal GPU acceleration

**Example Apple Configuration (M2 Max 64GB)**:
```yaml
council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
    - id: "psi"
      model: "mistral:7b"
    - id: "omega"
      model: "qwen2.5:7b"
  chairman:
    model: "llama3.2:70b-q4"  # Fits in 64GB unified memory
```

---

## Model Memory Requirements

Understanding VRAM requirements for different model sizes:

| Model Size | Full Precision | 8-bit (Q8) | 4-bit (Q4) | Notes |
|------------|----------------|------------|------------|-------|
| 3B | 6GB | 3GB | 2GB | Fast, lower quality |
| 7B | 14GB | 7GB | 4GB | Good balance |
| 8B | 16GB | 8GB | 5GB | Slightly better than 7B |
| 13B | 26GB | 13GB | 7GB | Noticeably smarter |
| 30B | 60GB | 30GB | 17GB | Significant quality jump |
| 70B | 140GB | 70GB | 40GB | Near-frontier quality |

**Memory Calculation Formula**:
```
VRAM ≈ (Parameters in billions × 2) GB for FP16
VRAM ≈ (Parameters in billions × 1) GB for INT8
VRAM ≈ (Parameters in billions × 0.5-0.6) GB for INT4
```

---

## Performance Optimization Tips

### For Consumer Hardware

1. **Use Quantized Models**: Q4_K_M offers the best quality/size tradeoff
   ```bash
   ollama pull llama3.2:8b-q4_K_M
   ```

2. **Reduce Council Size**: 2 members + chairman is viable
   ```yaml
   degradation:
     minimum_council_size: 2
   ```

3. **Sequential Inference**: Disable parallel inference
   ```yaml
   deliberation:
     stages:
       collect:
         parallel: false
   ```

4. **Swap Models**: Ollama automatically unloads unused models

### For Enthusiast/Professional Hardware

1. **Keep Models Loaded**: Pre-warm all models on startup
   ```yaml
   gateway:
     warmup:
       enabled: true
   ```

2. **Enable Parallel Inference**: Full concurrent deliberation
   ```yaml
   deliberation:
     stages:
       collect:
         parallel: true
   ```

3. **Use Higher Quality Quantization**: Q8 or full precision if VRAM allows

4. **Increase Context Window**: Longer deliberations possible
   ```yaml
   gateway:
     max_context_tokens: 8192
   ```

---

## Recommendations by Use Case

| Use Case | Recommended Tier | Key Considerations |
|----------|------------------|-------------------|
| Personal exploration | Consumer | Budget-friendly, acceptable latency |
| Daily professional use | Enthusiast | Good balance of cost and performance |
| Team/shared deployment | Professional | Fast response times, reliability |
| Air-gapped sensitive work | Professional+ | No cloud dependency, full local control |
| Compliance/regulated industry | Enterprise | Audit trails, ECC memory, redundancy |

---

## Cloud GPU Alternatives

If local hardware is not feasible, consider privacy-respecting cloud GPU rental:

| Provider | GPU Options | Privacy Notes |
|----------|-------------|---------------|
| [RunPod](https://runpod.io) | A100, H100 | Ephemeral instances available |
| [Vast.ai](https://vast.ai) | Various consumer/pro | Peer-to-peer, variable privacy |
| [Lambda Labs](https://lambdalabs.com) | A100, H100 | US-based, standard ToS |

**Warning**: Cloud deployment compromises the privacy guarantees of The Sovereign Council. Only use for testing or non-sensitive workloads.

---

## Troubleshooting

### Out of Memory Errors

```
Error: CUDA out of memory
```

**Solutions**:
1. Use smaller quantization (Q4 instead of Q8)
2. Reduce number of council members
3. Disable parallel inference
4. Close other GPU-using applications

### Slow Inference

**Causes and Solutions**:
- **Model swapping**: Increase system RAM or reduce model count
- **Disk bottleneck**: Use NVMe SSD for model storage
- **CPU preprocessing**: Ensure adequate CPU cores
- **Thermal throttling**: Improve cooling

### Model Loading Failures

```
Error: Failed to load model
```

**Solutions**:
1. Verify Ollama is running: `ollama list`
2. Pull model again: `ollama pull modelname`
3. Check disk space for model storage
4. Verify VRAM availability

---

## Future Considerations

Hardware requirements will evolve as:
- **Smaller models improve**: 3B models approaching 7B quality
- **Quantization advances**: Better quality at lower bit depths
- **Hardware accelerators**: NPUs in consumer devices
- **Apple Silicon improvements**: Each generation adds capability

The Sovereign Council configuration is designed to be flexible - update `sovereign_council.yaml` as your hardware or available models change.

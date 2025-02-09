import torch
import sys
import subprocess

def get_nvidia_smi_output():
    try:
        output = subprocess.check_output(["nvidia-smi"], universal_newlines=True)
        return output
    except:
        return "nvidia-smi command failed - NVIDIA driver might not be installed"

def check_gpu_availability():
    print("System Information:")
    print("-" * 50)
    print("Python version:", sys.version)
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    print("PyTorch CUDA version:", torch.version.cuda if hasattr(torch.version, 'cuda') else "None")
    
    print("\nNVIDIA Driver Information:")
    print("-" * 50)
    print(get_nvidia_smi_output())
    
    if torch.cuda.is_available():
        print("\nGPU Information:")
        print("-" * 50)
        print("Number of GPUs:", torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i}:")
            print("Name:", torch.cuda.get_device_name(i))
            print("Memory allocated:", torch.cuda.memory_allocated(i) / 1e9, "GB")
            print("Memory cached:", torch.cuda.memory_cached(i) / 1e9, "GB")
    else:
        print("\nTroubleshooting Steps:")
        print("-" * 50)
        print("1. Install NVIDIA CUDA Toolkit 11.8:")
        print("   https://developer.nvidia.com/cuda-11-8-0-download-archive")
        print("\n2. Install PyTorch with CUDA support:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("\n3. Verify NVIDIA drivers are installed:")
        print("   Run 'nvidia-smi' in command prompt")

if __name__ == "__main__":
    check_gpu_availability()

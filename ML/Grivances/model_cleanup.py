import os
import shutil
from glob import glob

def cleanup_model_files(base_dir='E:/ML/Grivances'):
    """Clean up unnecessary model files to save space"""
    
    cleanup_patterns = [
        '**/checkpoint-*',           # Remove intermediate checkpoints
        '**/*.bin',                 # Remove old model binaries
        '**/runs/*',                # Remove tensorboard logs
        '**/*.pt',                  # Remove pytorch checkpoints
        '**/optimizer.pt',          # Remove optimizer states
        '**/scheduler.pt',          # Remove scheduler states
        '**/*.temp',                # Remove temporary files
        '**/cache_*',               # Remove cache files
        '**/__pycache__',          # Remove Python cache
        '**/training_args.bin',     # Remove training args
    ]
    
    # Add safeguard for important files
    protected_dirs = [
        'unified_model/best_model',
        'unified_model/final_model',
    ]
    
    bytes_freed = 0
    for pattern in cleanup_patterns:
        for path in glob(os.path.join(base_dir, pattern), recursive=True):
            try:
                if os.path.isfile(path):
                    bytes_freed += os.path.getsize(path)
                    os.remove(path)
                elif os.path.isdir(path):
                    bytes_freed += sum(os.path.getsize(f) for f in glob(f"{path}/**/*", recursive=True))
                    shutil.rmtree(path)
                print(f"Removed: {path}")
            except Exception as e:
                print(f"Error removing {path}: {e}")
    
    print(f"Freed {bytes_freed / (1024*1024*1024):.2f} GB of space")

if __name__ == "__main__":
    cleanup_model_files()

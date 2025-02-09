import subprocess
import sys

def setup():
    print("Setting up environment...")
    
    # Install required packages
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError:
        print("Error installing packages")
        return False
        
    # Download required NLTK data for TextBlob
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        return False
        
    print("Setup completed successfully!")
    return True

if __name__ == "__main__":
    setup()

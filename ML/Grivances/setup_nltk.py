import nltk

def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('omw-1.4')
        print("NLTK data downloaded successfully")
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")

if __name__ == "__main__":
    download_nltk_data()

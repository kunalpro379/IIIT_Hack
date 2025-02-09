import torch
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer, ViTForImageClassification
from PIL import Image
import os
import pandas as pd
from tqdm import tqdm
import json
import numpy as np
from datetime import datetime

class GrievanceAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = self._setup_cache()
        self._load_models()
        self._setup_severity_rules()

    def _setup_cache(self):
        cache_dir = 'E:/ML/cache'
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def _load_models(self):
        # Load image captioning model
        self.caption_model = VisionEncoderDecoderModel.from_pretrained(
            'nlpconnect/vit-gpt2-image-captioning',
            cache_dir=self.cache_dir
        ).to(self.device)
        
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(
            'nlpconnect/vit-gpt2-image-captioning',
            cache_dir=self.cache_dir
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            'nlpconnect/vit-gpt2-image-captioning',
            cache_dir=self.cache_dir
        )

    def _setup_severity_rules(self):
        self.severity_rules = {
            'manhole': {
                'high': ['open', 'broken', 'missing', 'residential', 'city', 'school', 'market'],
                'medium': ['partially', 'damaged', 'suburban'],
                'low': ['minor', 'covered', 'rural']
            },
            'garbage': {
                'high': ['toxic', 'medical', 'chemical', 'city', 'residential', 'large'],
                'medium': ['overflow', 'scattered', 'suburban'],
                'low': ['small', 'contained', 'rural', 'biodegradable']
            },
            'road': {
                'high': ['major crack', 'pothole', 'highway', 'main road', 'city'],
                'medium': ['uneven', 'damaged', 'suburban'],
                'low': ['minor crack', 'rural', 'small pothole']
            }
        }

        self.location_weights = {
            'city': 3,
            'residential': 3,
            'school': 3,
            'market': 3,
            'suburban': 2,
            'rural': 1
        }

    def analyze_image(self, image_path):
        try:
            # Load and verify image
            image = Image.open(image_path).convert('RGB')
            
            # Generate caption
            caption = self._generate_caption(image)
            
            # Determine category
            category = self._determine_category(caption)
            
            # Analyze severity
            severity, severity_factors = self._analyze_severity(caption, category)
            
            # Generate detailed description
            description = self._generate_detailed_description(caption, category, severity, severity_factors)
            
            # Verify image authenticity
            authenticity = self._check_image_authenticity(image)
            
            return {
                'image_path': image_path,
                'caption': caption,
                'category': category,
                'severity': severity,
                'severity_factors': severity_factors,
                'detailed_description': description,
                'authenticity': authenticity,
                'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error analyzing {image_path}: {str(e)}")
            return None

    def _enhance_caption_with_context(self, basic_caption):
        """Enhance caption with civic grievance context"""
        caption_parts = []
        caption_lower = basic_caption.lower()
        
        # Add base caption
        caption_parts.append(basic_caption)
        
        # Analyze lighting conditions
        if 'dark' in caption_lower or 'night' in caption_lower:
            caption_parts.append("The area lacks proper lighting, creating safety concerns for residents.")
        elif 'light' in caption_lower:
            if 'no' in caption_lower or 'broken' in caption_lower:
                caption_parts.append("Non-functional street lights pose risks to pedestrian safety.")
        
        # Analyze infrastructure
        if 'street' in caption_lower or 'road' in caption_lower:
            if 'dark' in caption_lower:
                caption_parts.append("Poor visibility conditions affect public safety and mobility.")
            if any(word in caption_lower for word in ['broken', 'damaged', 'poor']):
                caption_parts.append("Infrastructure maintenance is needed to ensure public safety.")
        
        # Analyze human impact
        if any(word in caption_lower for word in ['people', 'man', 'woman', 'child']):
            caption_parts.append("Local residents are directly affected by these conditions.")
            if 'walk' in caption_lower:
                caption_parts.append("Pedestrians are forced to navigate through potentially hazardous conditions.")
        
        return ' '.join(caption_parts)

    def _generate_caption(self, image):
        pixel_values = self.feature_extractor(image, return_tensors="pt").pixel_values.to(self.device)
        
        with torch.no_grad():
            output_ids = self.caption_model.generate(
                pixel_values,
                max_length=100,
                num_beams=5,
                num_return_sequences=1
            )
        
        basic_caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        enhanced_caption = self._enhance_caption_with_context(basic_caption)
        return enhanced_caption

    def _determine_category(self, caption):
        caption_lower = caption.lower()
        
        if any(word in caption_lower for word in ['manhole', 'drain', 'sewer']):
            return 'manhole'
        elif any(word in caption_lower for word in ['garbage', 'waste', 'trash', 'dump']):
            return 'garbage'
        elif any(word in caption_lower for word in ['road', 'street', 'highway', 'pothole']):
            return 'road'
        return 'other'

    def _analyze_severity(self, caption, category):
        caption_lower = caption.lower()
        severity_score = 0
        factors = []

        if category in self.severity_rules:
            # Check category-specific rules
            for level, keywords in self.severity_rules[category].items():
                for keyword in keywords:
                    if keyword in caption_lower:
                        if level == 'high':
                            severity_score += 3
                        elif level == 'medium':
                            severity_score += 2
                        else:
                            severity_score += 1
                        factors.append(keyword)

            # Check location impact
            for location, weight in self.location_weights.items():
                if location in caption_lower:
                    severity_score += weight
                    factors.append(f"Location: {location}")

        # Determine final severity
        if severity_score >= 5:
            severity = "High"
        elif severity_score >= 3:
            severity = "Medium"
        else:
            severity = "Low"

        return severity, factors

    def _generate_detailed_description(self, caption, category, severity, factors):
        description = f"Analysis of {category.title()} Issue:\n\n"
        description += f"Primary Observation: {caption}\n\n"
        description += f"Severity Level: {severity}\n"
        description += f"Contributing Factors: {', '.join(factors)}\n\n"
        
        # Add category-specific details
        if category == 'manhole':
            description += self._get_manhole_details(caption, severity)
        elif category == 'garbage':
            description += self._get_garbage_details(caption, severity)
        elif category == 'road':
            description += self._get_road_details(caption, severity)
        
        return description

    def _check_image_authenticity(self, image):
        # Basic image authenticity checks
        authenticity_score = 100
        
        # Check metadata
        try:
            exif = image._getexif()
            if not exif:
                authenticity_score -= 20
        except:
            authenticity_score -= 20
        
        # Check image statistics
        img_array = np.array(image)
        if img_array.std() < 10:  # Too uniform
            authenticity_score -= 30
        
        return {
            'score': authenticity_score,
            'status': 'Likely Authentic' if authenticity_score > 70 else 'Possible Manipulation'
        }

    def process_folder(self, input_folder, output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        results = []
        
        image_files = [f for f in os.listdir(input_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        for image_file in tqdm(image_files):
            image_path = os.path.join(input_folder, image_file)
            result = self.analyze_image(image_path)
            if result:
                results.append(result)
        
        # Save results
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        return df

if __name__ == "__main__":
    analyzer = GrievanceAnalyzer()
    
    # Use correct train/test folders
    train_folder = "E:/ML/GrievanceProofs/Images/Train"
    test_folder = "E:/ML/GrievanceProofs/Images/Test"
    results_dir = "E:/ML/GrievanceProofs/results"
    
    # Create directories if they don't exist
    for dir_path in [train_folder, test_folder, results_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Process train images
    print("\nProcessing training images...")
    train_results = analyzer.process_folder(
        train_folder,
        os.path.join(results_dir, "train_analysis.csv")
    )
    
    # Process test images
    print("\nProcessing test images...")
    test_results = analyzer.process_folder(
        test_folder,
        os.path.join(results_dir, "test_analysis.csv")
    )
    
    # Combine results
    if train_results is not None and test_results is not None:
        all_results = pd.concat([
            train_results.assign(dataset='train'),
            test_results.assign(dataset='test')
        ])
        
        # Save combined results
        combined_output = os.path.join(results_dir, "combined_analysis.csv")
        all_results.to_csv(combined_output, index=False)
        
        print("\nAnalysis Summary:")
        print(f"Training images processed: {len(train_results)}")
        print(f"Test images processed: {len(test_results)}")
        print("\nSeverity Distribution (All):")
        print(all_results['severity'].value_counts())
        print("\nCategory Distribution:")
        print(all_results['category'].value_counts())
        print("\nResults saved to:", results_dir)
    else:
        print("\nNo images were processed successfully!")

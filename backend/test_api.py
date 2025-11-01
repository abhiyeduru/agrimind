"""
Test script to verify the disease detection API is working correctly
"""
import requests
from pathlib import Path

# Test with a sample image from the dataset
test_image_path = "../../PlantVillage/PlantVillage/Tomato___Late_blight/0a8cfb96-7bb1-456a-ab5b-087b3d2b6e1b___GHLB2 Leaf 274.JPG"

if Path(test_image_path).exists():
    print("Testing disease detection API...")
    print(f"Using test image: {test_image_path}")
    
    with open(test_image_path, 'rb') as f:
        files = {'file': f}
        data = {'user_id': 'test_user'}
        
        try:
            response = requests.post(
                'http://localhost:8000/detect_disease',
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✓ API is working!")
                print(f"  Crop: {result.get('crop')}")
                print(f"  Disease: {result.get('disease')}")
                print(f"  Is Healthy: {result.get('is_healthy')}")
                print(f"  Confidence: {result.get('confidence', 0)*100:.1f}%")
            else:
                print("\n✗ API returned an error")
                
        except requests.exceptions.ConnectionError:
            print("\n✗ Cannot connect to API. Make sure the server is running on port 8000")
        except Exception as e:
            print(f"\n✗ Error: {e}")
else:
    print(f"✗ Test image not found at: {test_image_path}")
    print("Please update the path to a valid image from your dataset")

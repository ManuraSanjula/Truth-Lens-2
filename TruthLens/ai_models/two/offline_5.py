import tensorflow as tf
import numpy as np
import os
import sys

# Try to configure system to handle unicode properly
if sys.platform.startswith('win'):
    try:
        import locale

        # Try several encodings that might work on Windows
        for loc in ['C.UTF-8', 'en_US.UTF-8', 'UTF-8', '']:
            try:
                locale.setlocale(locale.LC_ALL, loc)
                print(f"Successfully set locale to: {loc}")
                break
            except locale.Error:
                continue
    except Exception as e:
        print(f"Warning: Could not set locale: {e}")
        print("Proceeding with default encoding")

# Corrected the import statement
try:
    from ai_models.two.load import load_model  # Adjust if needed
except ImportError:
    print("Note: load_model import failed - this may be okay if you don't need it")

# Check TensorFlow version
print(f"TensorFlow version: {tf.__version__}")
print(f"Keras version: {tf.keras.__version__}")

# Set paths - use ASCII-only paths to avoid encoding issues
MODEL_CACHE_PATH = "../../model_cache"
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)


def create_compatible_model():
    """Create a minimal model that avoids version compatibility issues"""
    model = tf.keras.Sequential([
        # First conv block
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Second conv block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Flatten and output
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


try:
    # Create a simple model
    model = create_compatible_model()
    model.summary()

    # Create dummy weights
    dummy_input = np.zeros((1, 256, 256, 3), dtype=np.float32)
    try:
        dummy_output = model.predict(dummy_input)
        print("Model prediction successful")
    except Exception as e:
        print(f"Warning: Model prediction threw an error: {e}")
        print("Continuing with saving operations...")

    # Try multiple approaches to save the weights
    print("Attempting to save model weights...")
    success = False

    # Attempt 1: Save weights with .weights.h5 extension
    try:
        weights_path = os.path.join(MODEL_CACHE_PATH, "deepfake.weights.h5")
        model.save_weights(weights_path)
        print(f"✓ Success: Model weights saved to {weights_path}")
        success = True
    except Exception as e:
        print(f"× Failed approach 1: {e}")

    # Attempt 2: Only if first attempt failed - try HDF5 format
    if not success:
        try:
            weights_path = os.path.join(MODEL_CACHE_PATH, "deepfake_weights.h5")
            # No format parameter for Keras 3
            model.save_weights(weights_path)
            print(f"✓ Success: Model weights saved to {weights_path}")
            success = True
        except Exception as e:
            print(f"× Failed approach 2: {e}")

    # Attempt 3: Use a simple ASCII path
    if not success:
        try:
            weights_path = os.path.join(MODEL_CACHE_PATH, "model.h5")
            model.save_weights(weights_path)
            print(f"✓ Success: Model weights saved to {weights_path}")
            success = True
        except Exception as e:
            print(f"× Failed approach 3: {e}")

    # Save model structure to text file
    print("Attempting to save model structure...")
    structure_success = False

    try:
        structure_path = os.path.join(MODEL_CACHE_PATH, "model_structure.txt")
        with open(structure_path, 'w', encoding='utf-8') as f:
            model.summary(print_fn=lambda x: f.write(x + '\n'))
        print(f"✓ Model structure saved to {structure_path}")
        structure_success = True
    except Exception as e:
        print(f"× Failed to save structure with UTF-8: {e}")

    # Try ASCII encoding if UTF-8 failed
    if not structure_success:
        try:
            structure_path = os.path.join(MODEL_CACHE_PATH, "model_structure.txt")
            with open(structure_path, 'w', encoding='ascii', errors='replace') as f:
                model.summary(print_fn=lambda x: f.write(x + '\n'))
            print(f"✓ Model structure saved with ASCII encoding to {structure_path}")
        except Exception as e:
            print(f"× Failed to save structure with ASCII: {e}")

    # Try saving in SavedModel format - updated for Keras 3
    print("Attempting to save full model...")
    try:
        # For Keras 3, use .keras extension
        saved_model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.keras")
        model.save(saved_model_path)
        print(f"✓ Model saved in Keras format to {saved_model_path}")
    except Exception as e:
        print(f"× Failed to save with .keras extension: {e}")

        # Try HDF5 format as fallback
        try:
            h5_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")
            model.save(h5_path)
            print(f"✓ Model saved in H5 format to {h5_path}")
        except Exception as e2:
            print(f"× Failed to save in H5 format: {e2}")

            # Try SavedModel directory format as another fallback
            try:
                tf_path = os.path.join(MODEL_CACHE_PATH, "deepfake_saved_model")
                tf.saved_model.save(model, tf_path)
                print(f"✓ Model saved using tf.saved_model.save to {tf_path}")
            except Exception as e3:
                print(f"× Failed to save using tf.saved_model.save: {e3}")

except Exception as e:
    print(f"Error in main process: {e}")
    import traceback

    traceback.print_exc()

print("\nScript completed. Check above for successful operations.")
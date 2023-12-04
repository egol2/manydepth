import os
import cv2
import glob
import argparse
from .test_simple import test_simple
import imageio

def parse_folder_args():
    parser = argparse.ArgumentParser(description='Process a folder of images and create a video.')
    parser.add_argument('--folder_path', type=str, required=True, help='Path to the folder containing images.')
    parser.add_argument('--intrinsics_json_path', type=str, required=True, help='Path to the intrinsics json file.')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the model.')
    parser.add_argument('--mode', type=str, default='multi', choices=('multi', 'mono'), help='Mode: "multi" or "mono".')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save the processed images.')
    return parser.parse_args()

def process_folder_images(folder_path, args):
    print("Processing images...")
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.jpg')))  # Modify as per your image extension
    for i, target_image_path in enumerate(image_files[:-1]):  # Skip last image, no subsequent image
        source_image_path = image_files[i + 1]
        args.target_image_path = target_image_path
        args.source_image_path = source_image_path
        # Assuming test_simple saves the processed image to a specified output path
        args.output_image_path = os.path.join(args.output_path, os.path.basename(target_image_path))
        test_simple(args)
    print("Finished processing images.")

def create_video_from_images(folder_path, image_folder, output_video_path, output_gif_path, fps=24):
    print("Creating video and GIF...")
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpeg") and 'disp_multi' in img]  # Only include 'disp_multi' images
    if not images:
        raise RuntimeError("No images found for creating video and GIF")
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (2 * width, height))
    
    image_files = sorted(glob.glob(os.path.join(folder_path, '*.jpg')))

    gif_images = []
    for i, image in enumerate(images):
        input_image = cv2.imread(image_files[i])
        output_image = cv2.imread(os.path.join(image_folder, image))
        if input_image is None or output_image is None:
            print(f"Could not read one or both of the images {image} and {image}. Skipping these images.")
            continue
        # Resize output image to match input image's resolution
        output_image = cv2.resize(output_image, (width, height))
        combined_image = cv2.hconcat([input_image, output_image])
        video.write(combined_image)
        gif_images.append(combined_image[:, :, ::-1])  # Convert BGR to RGB for GIF creation
    
    cv2.destroyAllWindows()
    video.release()
    print("Finished creating video.")

    imageio.mimsave(output_gif_path, gif_images, duration=1000/fps)
    print("Finished creating GIF.")

if __name__ == "__main__":
    folder_args = parse_folder_args()
    process_folder_images(folder_args.folder_path, folder_args)
    output_video_path = os.path.join(folder_args.output_path, 'output_video.mp4')
    output_gif_path = os.path.join(folder_args.output_path, 'output_gif.gif')
    create_video_from_images(folder_args.folder_path, folder_args.output_path, output_video_path, output_gif_path)
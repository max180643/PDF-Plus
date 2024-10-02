import easyocr
import cv2
import fitz
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    # OCR
    gpu_enable = False

    # PDF config
    input_pdf_path = "input.pdf"
    output_pdf_path = "output.pdf"
    
    # Preview mode
    preview_mode = False
    preview_page = 1

    # Ignore page
    ignore_pages = []

    # Add crop margin
    margin_top = -20
    margin_bottom = 0
    margin_left = -25
    margin_right = 0

    # Start time
    start_time = time.time()

    # Open the input PDF
    pdf_document = fitz.open(input_pdf_path)

    # Preview Mode
    if (preview_mode):
        page_num = preview_page - 1
        pdf_autocrop_with_custom_margin(pdf_document, page_num, margin_top, margin_bottom, margin_left, margin_right, gpu_enable, preview_mode)
    else :
        # Detect the number of CPU cores and set the number of threads
        num_threads = os.cpu_count() or 1  # Default to 1 if os.cpu_count() is None

        # Prepare for multi-threading
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for page_num in range(len(pdf_document)):
                # Skip ignore page
                if (page_num + 1) in ignore_pages:
                    continue

                # Auto page crop
                future = executor.submit(pdf_autocrop_with_custom_margin, pdf_document, page_num, margin_top, margin_bottom, margin_left, margin_right, gpu_enable, preview_mode)
                futures.append(future)
            
            # Wait for all threads to complete
            completed_count = 0
            for future in as_completed(futures):
                future.result()  # Retrieve result or handle exceptions if any
                completed_count += 1
                print(f"Completed {completed_count}/{len(futures)} tasks.")

        # Save the cropped PDF
        pdf_document.save(output_pdf_path, deflate=True)
        pdf_document.close()

    # End time
    end_time = time.time()

    # Calculate the time taken
    process_time = end_time - start_time
    print(f"Process took {process_time:.6f} seconds")

def find_minmax_coordinates(image_path, gpu_enable=False):
    # OCR
    reader = easyocr.Reader(["en", "th"], gpu=gpu_enable)
    ocr_result = reader.readtext(image_path)

    # Initialize min and max values
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    
    # Iterate over all the bounding boxes
    for item in ocr_result:
        coords = item[0]
        for coord in coords:
            x, y = coord
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    # Return coordinates
    return min_x, min_y, max_x, max_y

def show_image_coordinates(image_path, min_x1, min_y1, max_x1, max_y1, min_x2, min_y2, max_x2, max_y2):
    # Load an image from file
    image = cv2.imread(image_path)

    # Draw the rectangle (bounding box) on the image (AutoCrop)
    # Parameters: image, top-left corner, bottom-right corner, color (BGR), thickness
    cv2.rectangle(image, (min_x1, min_y1), (max_x1, max_y1), (0, 255, 0), 1)

    # Draw the rectangle (bounding box) on the image (AutoCrop)
    # Parameters: image, top-left corner, bottom-right corner, color (BGR), thickness
    cv2.rectangle(image, (min_x2, min_y2), (max_x2, max_y2), (0, 0, 255), 1)

    # Display the image with the bounding box
    cv2.imshow('Image with Bounding Box', image)

    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def pdf_autocrop_with_custom_margin(pdf_document, page_num, margin_top=0, margin_bottom=0, margin_left=0, margin_right=0, gpu_enable=False, preview_mode=False):
    # Load pdf page
    page = pdf_document.load_page(page_num)
    
    # Get the page's MediaBox (full page area)
    media_box = page.rect
    
    # Render the page to an image
    pix = page.get_pixmap()
    
    # Save the image as a PNG file
    output_image = f"temp{page_num}.png"
    pix.save(output_image)

    # Find minmax coordinates
    min_x, min_y, max_x, max_y = find_minmax_coordinates(output_image, gpu_enable)

    # Calculate margin and ensure it's within MediaBox
    m_left = max(min_x - margin_left, 0) # ensure it doesn't go below 0
    m_top = max(min_y - margin_top, 0) # ensure it doesn't go below 0
    m_right = min(max_x + margin_right, media_box.width) # ensure it doesn't exceed page width
    m_bottom = min(max_y + margin_bottom, media_box.height) # ensure it doesn't exceed page height

    # Show coordinates (Preview mode only)
    if (preview_mode):
        show_image_coordinates(output_image, min_x, min_y, max_x, max_y, m_left, m_top, m_right, m_bottom)

    # Remove temp image
    os.remove(output_image)

    # Define the new bounding box, apply margin and ensure it's within MediaBox
    new_rect = fitz.Rect(
        m_left, # Left
        m_top, # Top
        m_right, # Right
        m_bottom # Bottom
    )

    # Check if the CropBox is within the MediaBox
    if new_rect in media_box:
        # Crop the page
        page.set_cropbox(new_rect)
    else:
        print(f"Page {page_num + 1}: CropBox {new_rect} is outside of MediaBox {media_box}. Skipping this page.")

main()
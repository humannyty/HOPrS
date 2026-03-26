import os
import cv2
import json
import shutil
import numpy as np
from flask import request, render_template, url_for, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from utils import (
    QuadTree, compare_and_output_images, count_black_pixels,
    create_red_overlay, draw_comparison, parse_file_to_tree
)
from . import sidebyside_bp


@sidebyside_bp.route('/sidebyside', methods=['GET', 'POST'])
def sidebyside():
    if request.method == 'GET':
        return render_template('sidebyside.html')

    if 'image1' not in request.files or 'image2' not in request.files:
        return "Two image files are required.", 400

    image1_file = request.files['image1']
    image2_file = request.files['image2']

    if image1_file.filename == '' or image2_file.filename == '':
        return "Both image files must be selected.", 400

    try:
        filename1 = secure_filename(image1_file.filename)
        filename2 = secure_filename(image2_file.filename)
        filepath1 = os.path.join(current_app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(current_app.config['UPLOAD_FOLDER'], filename2)
        image1_file.save(filepath1)
        image2_file.save(filepath2)

        threshold = int(request.form.get('threshold', 10))
        depth = int(request.form.get('compare_depth', 5))
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')

        image1 = cv2.imread(filepath1)
        image2 = cv2.imread(filepath2)
        if image1 is None:
            return "Error opening image 1. Please check the file.", 400
        if image2 is None:
            return "Error opening image 2. Please check the file.", 400

        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        qt1 = QuadTree(image1, depth, w1, h1, 0, 0, w1, h1, 'pdq', filename1 + ' ' + current_time)
        qt2 = QuadTree(image2, depth, w2, h2, 0, 0, w2, h2, 'pdq', filename2 + ' ' + current_time)

        qt1_path = filepath1 + '.qt'
        qt2_path = filepath2 + '.qt'
        qt1.print_tree(open(qt1_path, 'w'))
        qt2.print_tree(open(qt2_path, 'w'))

        output_folder = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'sidebyside_' + os.path.splitext(filename1)[0] + '_vs_' + os.path.splitext(filename2)[0]
        )
        os.makedirs(output_folder, exist_ok=True)

        tree1 = parse_file_to_tree(qt1_path)
        tree2 = parse_file_to_tree(qt2_path)

        image_derivative = cv2.imread(filepath2)
        image_mask = np.zeros((h2, w2, 3), np.uint8)
        image_mask[:] = (255, 255, 255)

        list_pixel_counter = [0]
        list_images = [image_derivative, image_mask]

        compare_and_output_images(list_images, list_pixel_counter, tree1, tree2,
                                  filepath1, output_folder, threshold, [0], depth)

        difference_mask_path = os.path.join(output_folder, 'difference_mask.png')
        cv2.imwrite(difference_mask_path, list_images[1], [int(cv2.IMWRITE_JPEG_QUALITY), 50])

        highlight_image_path = os.path.join(output_folder, 'highlighted_image.png')
        create_red_overlay(filepath2, difference_mask_path, highlight_image_path)

        image2_output_path = os.path.join(output_folder, filename2)
        shutil.copy(filepath2, image2_output_path)

        draw_comparison(list_images, list_pixel_counter, tree1, tree2,
                        output_folder, [-1], threshold, depth)

        comparison_image_path = None
        for file in os.listdir(output_folder):
            if file.startswith('comparison_') and file.endswith('.jpg'):
                comparison_image_path = os.path.join(output_folder, file)
                break

        if comparison_image_path is None:
            return "Comparison image not found.", 500

        unchanged_pixels = count_black_pixels(list_images[1])
        total_pixels = w2 * h2
        stats = {
            'matched_pixels': unchanged_pixels,
            'total_pixels': total_pixels,
            'proportion': unchanged_pixels / total_pixels
        }

        folder_name = os.path.basename(output_folder)
        return render_template('result.html',
                               difference_mask=url_for('compare_bp.output_file',
                                   filename=os.path.join(folder_name, 'difference_mask.png')),
                               comparison_image=url_for('compare_bp.output_file',
                                   filename=os.path.join(folder_name, os.path.basename(comparison_image_path))),
                               highlight_image=url_for('compare_bp.output_file',
                                   filename=os.path.join(folder_name, 'highlighted_image.png')),
                               new_image=url_for('compare_bp.output_file',
                                   filename=os.path.join(folder_name, filename2)),
                               stats=stats)

    except Exception as e:
        return str(e), 500

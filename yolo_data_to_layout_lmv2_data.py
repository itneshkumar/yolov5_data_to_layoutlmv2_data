import os
import cv2
import pytesseract
import pandas as pd
import easyocr


class DataFormatter:
    def __init__(self, labels_folder_path, image_folder_path):
        self.labels_folder = labels_folder_path
        self.image_folder = image_folder_path
        self.data = pd.DataFrame(columns=['image_path', 'imageWidth', 'imageHeight', 'Text', 'label', 'bbox'])
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    def process_data(self, google_ocr=False):
        for label_filename in os.listdir(self.labels_folder):
            image_name = label_filename.split('.txt')[0] + '.jpg'
            label_path = os.path.join(self.labels_folder, label_filename)
            image_path = os.path.join(self.image_folder, image_name)
            image = cv2.imread(image_path)
            image_shape = image.shape
            height, width = image_shape[0], image_shape[1]

            with open(label_path, 'r') as file:
                for line in file:
                    line_text = line.strip()
                    text_list = line_text.split(' ')
                    label = text_list[0]
                    print(label)


                    xc = float(text_list[1])
                    yc = float(text_list[2])

                    w, h = float(text_list[3]), float(text_list[4])

                    x1 = xc - w / 2
                    x2 = xc + w / 2
                    y1 = yc - h / 2
                    y2 = yc + h / 2

                    # x2, y2 = w + x1, h + y1

                    x1, x2, y1, y2 = int(x1 * width), int(x2 * width), int(y1 * height), int(y2 * height)
                    # pixelxc, pixelyc = int(xc * width), int(yc * height)

                    y2 = min(height, y2)
                    x2 = min(width, x2)
                    y1 = max(0, y1)
                    x1 = max(0, x1)

                    bbox = [x1, y1, x2, y2]

                    image_pixel = image[y1:y2, x1:x2]

                    if google_ocr:

                        extracted_text = pytesseract.image_to_string(image_pixel)
                        extracted_text = extracted_text.lower()
                        extracted_text = extracted_text.replace('\n', ' ')
                        extracted_text = extracted_text.replace('\x0c', '')
                        print(extracted_text)
                    else:
                        # Initialize EasyOCR reader
                        reader = easyocr.Reader(['en'])  # 'en' for English, you can specify other languages as needed

                        # Perform text recognition on the image
                        results = reader.readtext(image_pixel)
                        extracted_text = ''
                        for (bbox, text, prob) in results:
                            extracted_text = " " + text
                        print(extracted_text)

                        # height, width

                    upendable_data = [image_path, width, height, extracted_text, label, bbox]
                    self.data.loc[len(self.data)] = upendable_data
                    # image = cv2.rectangle(image, (x1, y1), (x2, y2), 1, 2)

                    # Displaying the image
                    # cv2.imshow('window_name', image)
                    # cv2.waitKey(1000)

    def save_to_csv(self, output_file_name):
        self.data.to_csv(output_file_name, index=False)


if __name__ == "__main__":
    labels_folder = '/home/itnesh/Pictures/dataformating/4_labels'
    # labels_folder = '/home/itnesh/Pictures/dataformating/labels'
    image_folder = '/home/itnesh/Pictures/dataformating/4_image'
    # image_folder = '/home/itnesh/Pictures/dataformating/images'
    output_file = 'output3.csv'
    # output_file = 'output1.csv'

    formatter = DataFormatter(labels_folder, image_folder)
    formatter.process_data(google_ocr=True)

    formatter.save_to_csv(output_file)

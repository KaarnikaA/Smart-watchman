import cv2
import numpy as np
from datetime import datetime
import mysql.connector

# Load the video file
video_path = "E:\Projects\smart watchman\output.mp4"
cap = cv2.VideoCapture(video_path)

# Load YOLO model for object detection
net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
layer_names = net.getLayerNames()
output_layers = [layer_names[i- 1] for i in net.getUnconnectedOutLayers()]

# Initialize SORT tracker
tracker = cv2.TrackerMOSSE_create()

con = mysql.connector.connect(
host="localhost", user="root",
password="root@2023", database="personal_details",port=3306)

# create cursor object
cursor = con.cursor()
cursor = con.cursor(buffered=True)

# Create a table to store object durations if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS object_durations (
             class TEXT,
             start_time TEXT,
             end_time TEXT,
             duration REAL
             )''')
con.commit()

trackers = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, channels = frame.shape

    # Object detection using YOLO
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Track objects and estimate durations
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(class_ids[i])
            confidence = confidences[i]

            # Check if the object is already being tracked
            tracked = False
            for tr in trackers:
                tracked_box = tr.update(frame)
                if tracked_box is not None:
                    tx, ty, tw, th = map(int, tracked_box)
                    if x == tx and y == ty and w == tw and h == th:
                        tracked = True
                        break

            if not tracked:
                # Create a new tracker for the object
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, (x, y, w, h))
                trackers.append(tracker)

                # Store object information in the database
                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO object_durations (class, start_time, end_time, duration) VALUES (?, ?, ?, ?)",
                          (label, start_time, "", 0.0))
                con.commit()

    # Remove old trackers for objects that are no longer detected
    trackers = [tr for tr in trackers if tr.update(frame) is not None]

    # Update tracked objects in the database
    for i, tracker in enumerate(trackers):
        bbox = tracker.update(frame)
        x, y, w, h = map(int, bbox)
        for row in cursor.execute("SELECT rowid, class, start_time FROM object_durations WHERE end_time = ''"):
            if row[1] == str(class_ids[i]) and row[2] == "":
                cursor.execute("UPDATE object_durations SET end_time = ?, duration = ? WHERE rowid = ?",
                              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0.0, row[0]))
                con.commit()

    # Display the frame with bounding boxes and labels
    for i, tracker in enumerate(trackers):
        bbox = tracker.update(frame)
        x, y, w, h = map(int, bbox)
        label = "Object" + str(i)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
con.close()

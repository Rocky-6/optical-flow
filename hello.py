"""test"""
import numpy as np
import cv2 as cv

# import sys
import csv

cap = cv.VideoCapture("slow_traffic_small.mp4")

# params for ShiTomasi corner detection
feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)

# Parameters for lucas kanade optical flow
lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03),
)

# Create some random colors
color = np.random.randint(0, 255, (100, 3))

# Take first frame and find corners in it
ret, old_frame = cap.read()
old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
p0 = cv.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

optical_flow_data = []

frame_index = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("No frames grabbed!")
        break

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # calculate optical flow
    p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    if p1 is not None:
        good_new = p1[st == 1]
        good_old = p0[st == 1]

    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        flow_vector = np.concatenate((old.ravel(), new.ravel()), axis=0)
        optical_flow_data.append([frame_index, frame_index + 1] + flow_vector.tolist())
        # a, b = new.ravel()
        # c, d = old.ravel()
        mask = cv.line(mask, (int(a), int(b)), (int(c), int(d)), color[i].tolist(), 2)
        frame = cv.circle(frame, (int(a), int(b)), 5, color[i].tolist(), -1)
    img = cv.add(frame, mask)

    if frame_index == 0:
        cv.imwrite("first_frame.png", img)
    cv.imwrite("optical_flow.png", img)

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    frame_index += 1

output_file = "optical_flow_data.csv"
with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["old_frame", "new_frame", "old_x", "old_y", "new_x", "old_y"])
    writer.writerows(optical_flow_data)

print("Optical flow data saved to", output_file)
